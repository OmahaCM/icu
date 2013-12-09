#!/usr/bin/python
"""
Have to execute using "sudo python facedetect.py --cascade=face.xml 0"
(Normal build sudo python "%f")
This program is demonstration for face and object detection using haar-like features.
The program finds faces in a camera image or video stream and displays a red box around them.

Original C implementation by:  ?
Python implementation by: Roman Stanchak, James Bowman
"""
import sys
import cv2.cv as cv
from optparse import OptionParser
import time
import threading
import readline
import pygame
from pygame.locals import *
import sys
import smbus

# Parameters for haar detection
# From the API:
# The default parameters (scale_factor=2, min_neighbors=3, flags=0) are tuned 
# for accurate yet slow object detection. For a faster operation on real video 
# images the settings are: 
# scale_factor=1.2, min_neighbors=2, flags=CV_HAAR_DO_CANNY_PRUNING, 
# min_size=<minimum possible face size

min_size = (20, 20)
image_scale = 2
haar_scale = 1.2
min_neighbors = 2
haar_flags = 0

"""i2c Code"""
bus = smbus.SMBus(1) # Open up a i@C bus.
address = 0x2a # Setup Arduino address

sendstring = "" # This will be my send variable (RPI-to-Arduino)
bytearraytowrite = [] #Actual array for holding bytes after conversion from string.

#This function actually does the writing to the I2C bus.
def toWrite(a): 
	global sendstring
	global bytearraytowrite
	bytearraytowrite = map(ord, sendstring) #This rewrites the string as bytes.
	for i in a:
		bus.write_byte(address, i)

def txrx_i2c():
	global sendstring
	#while True:
	sdata = "" 
	rdata = ""
	for i in range(0, 5):
			rdata += chr(bus.read_byte(address));
	#print rdata
	#print bytearraytowrite
	#print "".join(map(chr, bytearraytowrite)) #Will convert bytearray to string.
	
	#Writes the key commands to the i2c bus.
	toWrite(bytearraytowrite)
	
	
	#time.sleep(.6);

def detect_and_draw(img, cascade):
    global sendstring
    
    # allocate temporary images
    gray = cv.CreateImage((img.width,img.height), 8, 1)
    small_img = cv.CreateImage((cv.Round(img.width / image_scale),
			       cv.Round (img.height / image_scale)), 8, 1)

    # convert color input image to grayscale
    cv.CvtColor(img, gray, cv.CV_BGR2GRAY)

    # scale input image for faster processing
    cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)

    cv.EqualizeHist(small_img, small_img)

    if(cascade):
        t = cv.GetTickCount()
        faces = cv.HaarDetectObjects(small_img, cascade, cv.CreateMemStorage(0),
                                     haar_scale, min_neighbors, haar_flags, min_size)
        t = cv.GetTickCount() - t
        print "detection time = %gms" % (t/(cv.GetTickFrequency()*1000.))
        if faces:
            for ((x, y, w, h), n) in faces:
                # the input to cv.HaarDetectObjects was resized, so scale the 
                # bounding box of each face and convert it to two CvPoints
                pt1 = (int(x * image_scale), int(y * image_scale))
                pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
                cv.Rectangle(img, pt1, pt2, cv.RGB(255, 0, 0), 3, 8, 0)
                x1 = int(x * image_scale)
                y1 = int(y * image_scale)
                x2 = int((x + w) * image_scale)
                y2 = int((y + h) * image_scale)
                sendstring = str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2) + ","
                sendstring = sendstring.translate(None, '() ')
                print sendstring
                txrx_i2c()
                sendstring = ""
    cv.ShowImage("result", img)

if __name__ == '__main__':

    parser = OptionParser(usage = "usage: %prog [options] [filename|camera_index]")
    parser.add_option("-c", "--cascade", action="store", dest="cascade", type="str", help="Haar cascade file, default %default", default = "../data/haarcascades/haarcascade_frontalface_alt.xml")
    (options, args) = parser.parse_args()

    cascade = cv.Load(options.cascade)
    
    if len(args) != 1:
        parser.print_help()
        sys.exit(1)

    input_name = args[0]
    if input_name.isdigit():
        #Where the image is actually captured from camera. "capture" is the variable holding image.
        capture = cv.CreateCameraCapture(int(input_name)) 
    else:
        capture = None

    cv.NamedWindow("result", 1)

    width = 160 #leave None for auto-detection
    height = 120 #leave None for auto-detection

    if width is None:
    	width = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH)) #Gets the width of the image.
    else:
    	cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_WIDTH,width) #Gets the width of the image.   

    if height is None:
	height = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT))
    else:
	cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_HEIGHT,height) 

    if capture: #If "capture" actually got an image.
        frame_copy = None
        while True:

            frame = cv.QueryFrame(capture) 
            if not frame:
                cv.WaitKey(0)
                break
            if not frame_copy:
                frame_copy = cv.CreateImage((frame.width,frame.height),
                                            cv.IPL_DEPTH_8U, frame.nChannels)

#                frame_copy = cv.CreateImage((frame.width,frame.height),
#                                            cv.IPL_DEPTH_8U, frame.nChannels)

            if frame.origin == cv.IPL_ORIGIN_TL:
                cv.Copy(frame, frame_copy)
            else:
                cv.Flip(frame, frame_copy, 0)
            
            detect_and_draw(frame_copy, cascade)

            if cv.WaitKey(10) >= 0:
                break
    else:
        image = cv.LoadImage(input_name, 1)
        detect_and_draw(image, cascade)
        cv.WaitKey(0)

    cv.DestroyWindow("result")
