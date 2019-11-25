import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os, os.path
import codecs
import re
import PyPDF2
import sys
import subprocess
from subprocess import call

# for troubleshooting
def plot_image(img):
    plt.imshow(img)
    plt.show()
    plt.figure(figsize = (100,50))

# function to load the pngs
def load_pngs(path):
    imgs = []
    names = []
    valid_images = [".jpg",".gif",".png",".tga"]
    for f in os.listdir(path):
        ext = os.path.splitext(f)[1]
        if ext.lower() not in valid_images:
            continue
        imgs.append(cv2.imread(os.path.join(path,f), 0))
        names.append(os.path.join(path,f))

        # troubleshooting
        #print(os.path.join(path,f))

    # return the image list   
    return imgs,names

def main(pdf_flag):

    # if pdf flag is set, convert the pdfs to pngs, if not skip to the png step
    if pdf_flag == 1:

        # find all the pdfs in this folder or subfolders
        command = 'find . -type f -name "*.pdf"'    

        # runs the command from above, and saves the returned stuff as p
        p = subprocess.Popen(command, universal_newlines = True, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    
        # reads p into a text list, then waits a bit, then splits it up.
        text = p.stdout.read()
        retcode = p.wait()
        file_paths = text.splitlines()

        # convert them all into pngs and put them in the png folder
        range_end = np.size(file_paths)
        for i in range(range_end):
            s = ""
            str1 = file_paths[i][12:len(file_paths[i])-4]
            str2 = ".png"
            path2 = s.join([str1,str2])
            path1 = s.join([file_paths[i][0:len(file_paths[i])],"[0]"])

            # the ImageMagick step
            subprocess.call(["convert","-density","600","-trim",path1,"-resize","5400x7000!","-quality","600",path2])


            # try this later, different options for qualilty
            # convert -density 600 in.pdf -threshold 15% -type bilevel -compress fax out.pdf
            text = p.stdout.read()
            retcode = p.wait()
            subprocess.call(["mv",path2,"test_pngs"])
    
    # load the images
    imgs,names = load_pngs("test_pngs")
    range_end = len(imgs)
    
    # make the boxes
    right_box = [1200,4600,-2800,-50]
    left_box = [1200,4600,50,2800]

    # save the left and right windows of each png
    for i in range(range_end):
        s = ""
        str1 = names[i][10:-4]
        str2 = ".png"
        str3 = "./right_pngs/"
        str4 = "./left_pngs/"
        path1 = s.join([str3,str1,str2])
        path2 = s.join([str4,str1,str2])
        cv2.imwrite(path1,imgs[i][right_box[0]:right_box[1],right_box[2]:right_box[3]])
        cv2.imwrite(path2,imgs[i][left_box[0]:left_box[1],left_box[2]:left_box[3]])

    return np.shape(imgs)[0]

if __name__ == '__main__':
    main(int(sys.argv[1]))

