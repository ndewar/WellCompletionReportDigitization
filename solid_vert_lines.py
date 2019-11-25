import numpy as np
import cv2
import csv
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import os, os.path
from skimage.filters.rank import mean_bilateral
from skimage.filters.rank import median
from skimage.morphology import disk
import codecs
import re
import sys
 
def auto_canny(image, sigma=0.33): 
    
    # blur the image a little bit first
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    
    # compute the median of the single channel pixel intensities
    v = np.median(blurred)
 
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(blurred, lower, upper)
 
    # return the edged image
    return edged

def load_test_images(path):
    imgs = []
    names = []
    valid_images = [".jpg",".gif",".png",".tga"]
    for f in os.listdir(path):
        ext = os.path.splitext(f)[1]
        if ext.lower() not in valid_images:
            continue
        imgs.append(cv2.imread(os.path.join(path,f), 0))
        names.append(f)
    # return the image list   
    return imgs,names

def plot_image(img):
    plt.imshow(img)
    plt.show()
    plt.figure(figsize=(100,50))
    
def main(side,img_index,testing):

    s = ""
    # load the images
    imgs,names = load_test_images(s.join([side,"_pngs"]))

    # make a horz kernel
    zeros = np.zeros((2,100),np.float32)#/25
    kernel_hor = np.ones((1,100),np.float32)#/25
    kernel_hor = np.concatenate((zeros, kernel_hor), axis=0)
    kernel_hor = np.concatenate((kernel_hor, zeros), axis=0)
    
    # make a vert kernel
    zeros = np.zeros((100,2),np.float32)
    kernel_vert = np.ones((100,1),np.float32)
    kernel_vert = np.concatenate((zeros, kernel_vert), axis=1)
    kernel_vert = np.concatenate((kernel_vert, zeros), axis=1)
    #kernel_vert = np.ones((200,1),np.float32)
    
    # make another horz kernel
    kernel_spec1 = np.ones((1,3), np.uint8)
    kernel_spec2 = np.ones((3,1), np.uint8)
    kernel_vert_short = np.ones((1,30), np.uint8)
    kernel_hor_short = np.ones((30,1), np.uint8)
    
    # make a uniform kernel
    kernel_uniform = np.ones((3,3),np.uint8)

    # select the image to work with
    img = imgs[img_index]

    # get the horizontal and vertical lines
    dst_hor = cv2.filter2D(img,-1,kernel_hor)
    dst_vert = cv2.filter2D(img,-1,kernel_vert)
    
    # erode it abit to make sure you get all the lines
    dst_hor = cv2.erode(dst_hor,kernel_vert_short,iterations=10)
    dst_hor = cv2.erode(dst_hor,kernel_uniform,iterations=1)
    dst_hor = cv2.erode(dst_hor,kernel_spec2,iterations=1)
    dst_hor = cv2.dilate(dst_hor,kernel_uniform,iterations=1)
    dst_vert = cv2.erode(dst_vert,kernel_hor_short,iterations=10)
    dst_vert = cv2.erode(dst_vert,kernel_uniform,iterations=1)
    dst_vert = cv2.dilate(dst_vert,kernel_uniform,iterations=1)
    
    # threshold the shit and then subtract from the original image
    ret,thresh1 = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
    ret,thresh2 = cv2.threshold(dst_vert,127,255,cv2.THRESH_BINARY)
    ret,thresh3 = cv2.threshold(dst_hor,127,255,cv2.THRESH_BINARY)
    thresh2 = 255-thresh2
    thresh3 = 255-thresh3
    thresh1 = 255-thresh1
    ret,thresh_final = cv2.threshold(thresh2+thresh3,127,255,cv2.THRESH_BINARY)
    no_lines = thresh1-thresh_final
    
    no_lines = 255-no_lines
    
    # threshold again
    ret,no_lines = cv2.threshold(no_lines,127,255,cv2.THRESH_BINARY)
    
    # try and remove the stamp across the image
    d_im = cv2.dilate(no_lines, kernel_spec1, iterations=1)
    e_im = cv2.erode(d_im, kernel_uniform, iterations = 1)
    
    # apply a filter to remove speckle
    no_lines = median(e_im, disk(2))
    
    # convert to binary and invert one last time
    no_lines = cv2.bitwise_not(no_lines)


    # plot it if troubleshooting
    if testing == 1:
        plt.subplot(221),plt.imshow(thresh1,cmap='gray'),plt.title('Original')
        plt.xticks([]), plt.yticks([])
        plt.subplot(222),plt.imshow(thresh3,cmap='gray'),plt.title('horizontal')
        plt.xticks([]), plt.yticks([])
        plt.subplot(223),plt.imshow(thresh2,cmap='gray'),plt.title('vertical')
        plt.xticks([]), plt.yticks([])
        plt.subplot(224),plt.imshow(no_lines,cmap='gray'),plt.title('vertical')
        plt.xticks([]), plt.yticks([])
        plt.figure(figsize=(2000,2000))
        plt.show()

    return no_lines,names

if __name__ == '__main__':
    main(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))
