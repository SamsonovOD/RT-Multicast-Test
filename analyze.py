import random, time
import cv2
import numpy, pandas
from threading import Thread
from multiprocessing import Process

bad_frame_count = []
color_check = []
seq1 = [(36, 28, 237),(0, 242, 255),(76, 177, 34),(0, 0, 0),(164, 73, 163),(201, 174, 255),(255, 255, 255),(127, 127, 127),(234, 217, 153),(29, 230, 181)]
seq2 = [(36, 29, 237),(38, 127, 254),(14, 201, 255),(0, 241, 254),(29, 230, 181),(76, 177, 33),(235, 217, 154),(232, 161, 0),(189, 146, 112),(203, 71, 63),(165, 73, 163),(87, 123, 185),(255, 255, 255),(127, 127, 127),(0, 0, 0),(21, 0, 136),(201, 174, 255),(195, 235, 197),(192, 25, 223),(86, 164, 117)]

def check_color(i, frame, test):
    get_i = i-1
    if test == 1:
        while get_i > len(seq1): get_i = get_i - len(seq1)
        if seq1[get_i][0] == frame[0][0][0] and seq1[get_i][1] == frame[0][0][1] and seq1[get_i][2] == frame[0][0][2]:
            color_check.append("yes")
        else:
            color_check.append("wrong")
    elif test == 2:
        while get_i > len(seq2): get_i = get_i - len(seq2)
        if seq2[get_i][0] == frame[0][0][0] and seq2[get_i][1] == frame[0][0][1] and seq2[get_i][2] == frame[0][0][2]:
            color_check.append("yes")
        else:
            color_check.append("wrong")

def work(i, frame, y1 = 0, y2 = 0, x1 = 0, x2 = 0):
    f_y = len(frame)
    f_x = len(frame[0])
    if y2 > f_y or y2 == 0: y2 = f_y
    if x2 > f_x or x2 == 0: x2 = f_x
    frame = frame[y1:y2,x1:x2].reshape((y2-y1)*(x2-x1), 3)
    if len(frame)*3 != numpy.count_nonzero(frame == frame[0]):
        bad_frame_count.append(i)

def vid(y1 = 0, y2 = 0, x1 = 0, x2 = 0, test = 1):
    start = time.time()
    i = 0
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    while i < frames:
        i += 1
        ret, frame = cap.read()            
        p1 = Thread(target=work, args=(i, frame, y1, y2, x1, x2))
        p2 = Thread(target=check_color, args=(i, frame, test))
        p1.start()          
        p2.start()
        if i == frames:
            p1.join()
            p2.join()
    print("FPS:", frames/(time.time() - start))
    if len(bad_frame_count) > 0:
        print("Bad frames detected:", bad_frame_count)
    else:
        print("Video is good")
    print(color_check)
    bad_frame_count.clear()
    color_check.clear()

if __name__ == '__main__':

    cap = cv2.VideoCapture("good.mp4", cv2.CAP_ANY)
    print("= small VID GOOD? =")
    vid(test = 1)
    
    cap = cv2.VideoCapture("bad.mp4", cv2.CAP_ANY)
    print("\n= small VID BAD (8, 12, 24)? =")
    vid(test = 1)
    
    cap = cv2.VideoCapture("goodhd.mp4", cv2.CAP_ANY)
    print("\n= HD VID GOOD? =")
    vid(test = 2)
    
    cap = cv2.VideoCapture("badhd.mp4", cv2.CAP_ANY)
    print("\n= HD VID BAD? (8, 25, 42, 59)=")
    vid(200, 1000, 300, 1800, test = 2)