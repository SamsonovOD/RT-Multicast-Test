import os, os.path
import ffmpeg
import random, time
import cv2
import numpy as np
import threading
from multiprocessing import Process

bad_frame_count = []
color_check = []
check_seq = [0]
seq1 = []
frametest = []

def color_get(frame):
    ok = 0
    i = 0
    while ok == 0 and i < len(seq1):
        get = frame[len(frame)//2][len(frame[0])//2]
        if seq1[i][0] == get[0] and seq1[i][1] == get[1] and seq1[i][2] == get[2]:
            check_seq.insert(0,i)
            ok = 1
        else:
            i += 1
            check_seq.append(get)
    
def check_color(i, frame):
    get_i = i
    while get_i > len(seq1)-1: get_i = get_i - len(seq1)
    get_i = get_i - len(seq1)
    get = frame[len(frame)//2][len(frame[0])//2]
    k = get_i+len(seq1)+check_seq[0]
    while k > len(seq1)-1: k = k - len(seq1)
    if seq1[get_i + check_seq[0]][0] == get[0] and seq1[get_i + check_seq[0]][1] == get[1] and seq1[get_i + check_seq[0]][2] == get[2]:
        # color_check.append("correct ["+str(i)+str(get)+" vs "+str(k)+str(seq1[get_i + check_seq[0]])+"]")
        color_check.append("Y")
    else:
        # color_check.append("wrong ["+str(i)+str(get)+" vs "+str(k)+str(seq1[get_i + check_seq[0]])+"]")
        color_check.append("B")
        color_get(frame)

def corrupt_check(i, frame, y1 = 0, y2 = 0, x1 = 0, x2 = 0):
    f_y = len(frame)
    f_x = len(frame[0])
    if y2 > f_y or y2 == 0: y2 = f_y
    if x2 > f_x or x2 == 0: x2 = f_x
    frame2 = frame[y1:y2,x1:x2].reshape((y2-y1)*(x2-x1), 3)
    if len(frame2)*3 != np.count_nonzero(frame2 == frame2[0]):
        get = frame[len(frame)//2][len(frame[0])//2]
        bad_frame_count.append((i, (get[0], get[1], get[2])))

class VideoCaptureAsync:
    def __init__(self, src=0):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()

    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def start(self):
        if self.started:
            print('[!] Asynchroneous video capturing has already been started.')
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self

    def isOpened(self):
        return self.cap.isOpened()

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()

class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        cap = VideoCaptureAsync("udp://127.0.0.1:2000")
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.start()
        i = 0
        while True:
            _, frame = cap.read()
            c = (frame[len(frame)//2][len(frame[0])//2][0], frame[len(frame)//2][len(frame[0])//2][1], frame[len(frame)//2][len(frame[0])//2][2])
            if len(frametest) == 0:
                color_get(frame)
                frametest.append(c)
                # p1 = threading.Thread(target=corrupt_check, args=(i, frame, len(frame)//3, (len(frame)//3)+(len(frame)//3), len(frame)//3, (len(frame)//3)+(len(frame)//3)))
                # p1.start()       
                # p1.join()
                p2 = threading.Thread(target=check_color, args=(i, frame))   
                p2.start()
                p2.join()
                i += 1
            else:
                if frametest[-1][0] != c[0] or frametest[-1][1] != c[1] or frametest[-1][2] != c[2]: 
                    frametest.append(c)
                    # p1 = threading.Thread(target=corrupt_check, args=(i, frame, 2*(len(frame)//5), 3*(len(frame)//5), 2*(len(frame[0])//6), 3*(len(frame[0])//6)))
                    # p1.start()       
                    # p1.join()
                    p2 = threading.Thread(target=check_color, args=(i, frame))   
                    p2.start()
                    p2.join()
                    i += 1
            # cv2.imshow('Capture', frame)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                cv2.destroyWindow('Capture')
            if i > 100:
                break
            # if cv2.getWindowProperty('Capture', 4) < 1:
                # break
        cap.stop()
        cv2.destroyAllWindows()
        print("Original:", seq1)
        print("Capture:", frametest)
        print("Seq check:", color_check)
        if len(bad_frame_count) > 0:
            print("Corrupt frames detected:", bad_frame_count)
        else:
            print("Video is good")
	
def prepwork():
    cap = cv2.VideoCapture('multicast4.mp4')
    while(cap.isOpened()):
        ret, frame = cap.read()
        if frame is not None:
            get = (frame[len(frame)//2][len(frame[0])//2][0], frame[len(frame)//2][len(frame[0])//2][1], frame[len(frame)//2][len(frame[0])//2][2])
            if len(seq1) > 1:
                if get == seq1[0]:
                    break
            seq1.append(get)
        else:
            break
    cap.release()
    
if __name__ == '__main__':
    prepwork()
    Main().start()