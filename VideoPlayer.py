#!/usr/bin/env python3

import threading
import cv2
import queue
import base64

mutex = threading.Lock()
class threadedQueue():
    
    def __init__(self):
        self.semaphore = threading.Semaphore(10) #10 the given capacity
        self.queue = queue.Queue()
    #put the image inside queue
    def put(self,frame):
        self.semaphore.acquire()#gets semaphore and decreases total by one; will get released when image is popped
        mutex.acquire()
        self.queue.put(frame)
        mutex.release()
    #retrieve image from queue
    def get(self):
        self.semaphore.release()
        mutex.acquire()
        frame = self.queue.get()
        mutex.release()
        return frame
    #check if queue has frames
    def isEmpty(self):
        mutex.acquire()
        isEmpty = self.queue.empty()
        mutex.release()
        return isEmpty

queueOne = threadedQueue()
queueTwo = threadedQueue()
filename = 'clip.mp4'
#stores total frames in video
c = cv2.VideoCapture(filename)
total = int(c.get(cv2.CAP_PROP_FRAME_COUNT))-1


def extractFrames(fileName = 'clip.mp4', maxFramesToLoad=9999):
    # Initialize frame count
    count = 0
    # open video file
    vidcap = cv2.VideoCapture(fileName)
    # read first image
    success,image = vidcap.read()
    print(f'Reading frame {count} {success}')
    while success:
        success, jpgImage = cv2.imencode('.jpg', image)
        queueOne.put(image)
        count +=1
        success,image = vidcap.read()
        print(f'Reading frame {count} {success}')
         
    print('Frame extraction complete')
    #queueOne.put('end')
    

def convertToGrayscale():
    count = 0
    while True:
        if queueOne.isEmpty():
            continue
        getting = queueOne.get()
        #if last frame was already processed, leave
        if count == total:
            break
         
        #convert to grayscale
        grayScaleFrame = cv2.cvtColor(getting, cv2.COLOR_BGR2GRAY)

        queueTwo.put(grayScaleFrame)
        print(f'Converting frame {count}')
        count +=1
    
    


def displayFrames():

    #initialize frame count
    count = 0
 
    while True:
        #my take on the flag
        if count == total:
            break
        if queueTwo.isEmpty():
            continue
        # get the next frame
        frame = queueTwo.get()
        print(f'Displaying frame {count}')
        # display the image in a window called "video" and wait 42ms
        # before displaying the next frame

        cv2.imshow('Video', frame)

        if cv2.waitKey(42) and 0xFF == ord("q"):
            break
        count += 1
                
    print('Finished displaying all frames')
    # cleanup the windows
    cv2.destroyAllWindows()
    
threadOne = threading.Thread(target= extractFrames)
threadTwo = threading.Thread(target = convertToGrayscale)
threadThree = threading.Thread(target = displayFrames)
threadOne.start()
threadTwo.start()
threadThree.start()
