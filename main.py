import numpy as np
import cv2
import time
from serial import Serial
from lane_lines import draw_lanes
from grabscreen1 import grab_screen
from text_recognition2 import traffic_sign
from traffic_light import get_classification

def roi(img, vertices):
    
    #blank mask:
    mask = np.zeros_like(img)   
    
    #filling pixels inside the polygon defined by "vertices" with the fill color    
    cv2.fillPoly(mask, vertices, 255)
    
    #returning the image only where mask pixels are nonzero
    masked = cv2.bitwise_and(img, mask)
    return masked



def process_img(image):
    original_image = image
    # convert to gray
    processed_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # edge detection
    processed_img =  cv2.Canny(processed_img, threshold1 = 200, threshold2=300)
    # Change threshold1 & threshold 2 for changing line intensity
    # higher value for lower line intensity
    
    
    processed_img = cv2.GaussianBlur(processed_img,(5,5),0)
    
    vertices = np.array([[10,500],[10,300],[300,200],[500,200],[800,300],[800,500]], np.int32)


    processed_img = roi(processed_img, [vertices])

    # more info: http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
    #                                     rho   theta   thresh  min length, max gap:        
    lines = cv2.HoughLinesP(processed_img, 2, np.pi/180, 15, np.array([]), 20, 30)
    m1 = 0
    m2 = 0
    try:
        l1, l2, m1,m2 = draw_lanes(original_image,lines)
        cv2.line(original_image, (l1[0], l1[1]), (l1[2], l1[3]), [0,255,0], 30)
        cv2.line(original_image, (l2[0], l2[1]), (l2[2], l2[3]), [0,255,0], 30)
    except Exception as e:
        print(str(e))
        pass
    try:
        for coords in lines:
            coords = coords[0]
            try:
                cv2.line(processed_img, (coords[0], coords[1]), (coords[2], coords[3]), [255,0,0], 3)
                
                
            except Exception as e:
                print(str(e))
    except Exception as e:
        pass

    return processed_img,original_image, m1, m2

def straight():
    print('straight')
    ser.write(str.encode('1'))
    time.sleep(slowtime)

def left():
    print('left')
    ser.write(str.encode('2'))
    time.sleep(slowtime)
    
def right():
    print('right')
    ser.write(str.encode('3'))
    time.sleep(slowtime)

def stop():
    print('stop')
    ser.write(str.encode('4'))
    time.sleep(slowtime)


for i in list(range(4))[::-1]:
    print(i+1)
    time.sleep(1)

#ser=Serial('COM4',9600)
ser=Serial('COM5',9600)
last_time = time.time()
slowtime = 1.0 #slow down serial commands

while True:
    screen = grab_screen()
    print('Frame took {} seconds'.format(time.time()-last_time))
    last_time = time.time()
    new_screen,original_image, m1, m2 = process_img(screen)
    cv2.imshow('window', new_screen)
    new_screen1 = traffic_sign(screen)
    cv2.imshow('window1', new_screen1)
    #cv2.imshow('window2',cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    
    if m1 < 0 and m2 < 0:
        right()
    elif m1 > 0  and m2 > 0:
        left()
    else:
        straight()
    
    #cv2.imshow('window',cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break

