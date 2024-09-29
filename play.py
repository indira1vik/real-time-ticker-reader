import cv2
import streamlink
import sys, getopt
import threading
import xml.etree.ElementTree as ET
import multiprocessing
import time

from video import VideoObj
from find_ticker import get_tickers
from extract_text import extract_scrolling_text
from reader import (
    get_substring,
    correct_spelling,
    concatenate_word_lists,
    remove_edge_words,
)
from voice import stage_tts, speak

word_list = []
engine = stage_tts()

def extract_stream_link(video_api):
    try:
        streams = streamlink.streams(video_api)
        stream_url = streams["best"].url
        return stream_url
    except Exception as ex:
        print(f"Error: {ex}")
        return None


def save_coord(video_cap, tickers, photo_number):
    try:
        tree = ET.parse("annotations.xml")
        root = tree.getroot()
    except FileNotFoundError:
        root = ET.Element("annotations")
        tree = ET.ElementTree(root)
    
    for ticker in tickers:
        image_elem = ET.SubElement(root, "image")
        image_elem.set("id", str(photo_number))
        image_elem.set("name", f"ticker_image_{photo_number}.png")
        image_elem.set("width", str(video_cap.width))
        image_elem.set("height", str(video_cap.width))

        miny, maxy = ticker[0]
        minx, maxx = ticker[1]

        box_elem = ET.SubElement(image_elem, "box")
        box_elem.set("label", "ticker")
        box_elem.set("source", "manual")
        box_elem.set("occluded", "0")
        box_elem.set("xtl", str(minx))
        box_elem.set("ytl", str(miny))
        box_elem.set("xbr", str(maxx))
        box_elem.set("ybr", str(maxy))
        box_elem.set("z_order", "0")

    tree = ET.ElementTree(root)
    tree.write("annotations.xml")


def save_image(image, tickers, photo_number):
    for ticker in tickers:
        miny, maxy = ticker[0]
        minx, maxx = ticker[1]
        cv2.rectangle(image, (minx, miny), (maxx, maxy), (0, 0, 255), 2)
        cv2.imwrite(f"images/ticker_image_{photo_number}.png", image)


def save_image_empty(image, photo_number):
    cv2.imwrite(f"coords/ticker_image_{photo_number}.png", image)


def capture_initial_frames(video, frame_count):
    frames = [video.frames() for _ in range(frame_count)]
    return frames


def cmd_line_help():
    print('Usage Example:\npython run.py -v "<video_url/video_api>"\npython run.py -r "<video_path>"\npython run.py -c\npython run.py -h')


def read_aloud(text):
    if engine._inLoop:
        engine.endLoop()
    engine.say(text)
    engine.runAndWait()

def audio_process(queue):
    while True:
        if not queue.empty():
            text = queue.get()
            read_aloud(text)



def main(video_url, recorded_video, camera):
    start_time = time.time()
    if video_url != "":
        stream_url = extract_stream_link(video_url)
        video_cap = VideoObj(stream_url)
    elif recorded_video != "":
        video_cap = VideoObj(recorded_video)
    elif camera != False:
        video_cap = VideoObj(0)
    else:
        print("Invalid arguments provided\n")
        cmd_line_help()
        sys.exit(1)

    window_tab_name = "Video Streaming Tab"
    cv2.namedWindow(window_tab_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_tab_name, 854, 480)

    frame_count = 120
    initial_frames = capture_initial_frames(video_cap, frame_count)
    tickers, height, width = get_tickers(video_cap, initial_frames)

    end_time = time.time()

    frame_counter = -6
    photo_number = 0
    prev = ""
    combined_string = ""
    print_string_output = ""

    full_big_string = ""

    queue = multiprocessing.Queue()

    audio_proc = multiprocessing.Process(target=audio_process, args=(queue,))
    audio_proc.start()

    video_start_time = end_time - start_time
    print(f"Time taken from program start to video start: {video_start_time:.2f} seconds")

    for ticker in tickers:
        miny, maxy = tickers[0][0]
        minx, maxx = tickers[0][1]
        print("Ticker coords: ", minx, miny, maxx, maxy)

    while True:
        frame = video_cap.frames()
        for ticker in tickers:
            miny, maxy = tickers[0][0]
            minx, maxx = tickers[0][1]
            cv2.rectangle(frame, (minx, miny), (maxx, maxy), (0, 0, 255), 2)
        
        cv2.imshow(window_tab_name, frame)

        image = video_cap.frames_neat()
        # save_image_empty(image,photo_number)
        frame_counter += 1

        if frame_counter % 72 == 0:
            for ticker in tickers:
                word_list = extract_scrolling_text(image, ticker)
                print("\nWord list Extracted from Ticker Region:\n")
                for i in word_list[0]:
                    print(f"Text: {i['text']:<20} || Left: {i['left']:>8.2f} || Right: {i['right']:>8.2f} || Bottom: {i['bottom']:>8.2f} || Top: {i['top']:>8.2f} || Confidence: {i['confidence']:>2.2f} ||")
                word_list = remove_edge_words(word_list[0], width, height)
                print("\nWord list After Removal of Edge Words:\n")
                for i in word_list:
                    print(f"Text: {i['text']:<20} || Left: {i['left']:>8.2f} || Right: {i['right']:>8.2f} || Bottom: {i['bottom']:>8.2f} || Top: {i['top']:>8.2f} || Confidence: {i['confidence']:>2.2f} ||")

                ticker_text = concatenate_word_lists(word_list)
                print("\nComplete text after Removal of Edge words:\n\"",ticker_text,"\"")
                ticker_text = correct_spelling(str(ticker_text))
                print("\nComplete text after Spelling Correction:\n\"",ticker_text,"\"")

                s1 = ticker_text
                if prev != "":
                    combined_string = get_substring(prev, s1)
                    print_string_output = combined_string                    
                else:
                    print_string_output = ticker_text
                prev = s1

                print("Continuous Text: ", print_string_output)
                full_big_string += print_string_output
                queue.put(print_string_output)

            # save_image(image, tickers, photo_number)
            # save_coord(video_cap,tickers,photo_number)
            photo_number += 1

            if not ticker_text:
                print("No Ticker Text found")
                initial_frames = capture_initial_frames(video_cap, frame_count=72)
                tickers, height, width = get_tickers(video_cap, initial_frames)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    

    video_cap.release()
    cv2.destroyAllWindows()
    audio_proc.terminate()

    print("Complete Text Appeared in Video: \n",full_big_string)


if __name__ == "__main__":
    input_video_url = ""
    input_recorded_video = ""
    camera = False

    try:
        options, args = getopt.getopt(sys.argv[1:], "hv:r:c")
    except getopt.GetoptError:
        cmd_line_help()
        sys.exit(1)

    for opt, arg in options:
        if opt in ["-h"]:
            cmd_line_help()
            sys.exit(1)
        elif opt in ["-v"]:
            input_video_url = arg
        elif opt in ["-r"]:
            input_recorded_video = arg
        elif opt in ["-c"]:
            camera = True

    main(input_video_url, input_recorded_video, camera)
