import cv2
import pytesseract
import numpy as np

def extract_scrolling_text(image, ticker):
    miny, maxy = ticker[0]
    minx, maxx = ticker[1]
    ticker_region = image[miny:maxy, minx:maxx].astype(np.uint8)
    ticker_region_gray = cv2.cvtColor(ticker_region, cv2.COLOR_BGR2GRAY)
    
    ocr_output = pytesseract.image_to_data(ticker_region_gray, config="--psm 6", output_type=pytesseract.Output.DICT)

    result = []
    for i in range(len(ocr_output['level'])):
        if ocr_output['level'][i] == 1:
            last_page = ocr_output['page_num'][i]
            result.append([])
        elif (ocr_output['level'][i] == 5) and (len(ocr_output['text'][i]) > 0) and (ocr_output['text'][i] != " "):
            word = {}
            word["text"] = ocr_output['text'][i]
            word["left"] = float(ocr_output['left'][i])
            word["top"] = float(ocr_output['top'][i])
            word["right"] = float(ocr_output['left'][i]) + float(ocr_output['width'][i])
            word["bottom"] = float(ocr_output['top'][i]) + float(ocr_output['height'][i])
            word["confidence"] = float(ocr_output['conf'][i]) / 100.0
            result[-1].append(word)

    return result

