import re
from spellchecker import SpellChecker

def spell_check(input_text, tokenizer, model):
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids
    output_ids = model.generate(input_ids)
    corrected_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return corrected_text


def concatenate_word_lists(word_list):
    temp = ""
    for word in word_list:
        temp += word['text'] + ' '
    
    return temp

def remove_edge_words(word_list, width = None, height = None):
    if width != None:
      result = []
      for word in word_list:
        if word['left'] > height and word['right'] < width - height:
          result.append(word)
      return result
    else:
      raise print('No width supplied in testing')


def filter_words(input_string):
    pattern = re.compile(r'[^a-zA-Z0-9\s.]')
    filtered_string = re.sub('-', ' ', input_string)
    filtered_string = re.sub(pattern, '', filtered_string)
    words = filtered_string.split()
    filtered_text = ' '.join(words)
    return filtered_text

def correct_spelling(text):
    text = filter_words(text)
    spell = SpellChecker()
    words = text.split()
    corrected_text = []
    for word in words:
        if word[0].isupper() or word is None:
            corrected_word = word
        else:
            corrected_word = spell.correction(str(word))
        if corrected_word is not None:
            corrected_text.append(corrected_word)
    if not corrected_text:
        return text
    corrected_text = " ".join(corrected_text)
    return corrected_text


def longest_common_substring(s1, s2):
    m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in range(1, 1 + len(s1)):
        for y in range(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]

def get_substring(s1, s2):
    common_substring = longest_common_substring(s1, s2)
    index_common = s2.find(common_substring)
    non_common_substring = s2[:index_common] + s2[index_common + len(common_substring):]
    return non_common_substring


