import numpy as np
import csv
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pytesseract
from PIL import Image
import os, os.path
import codecs
import re
import sys

def main(no_lines,side,names,img_index,algo):
    s = ""
    # use googles OCR program
    #text = pytesseract.image_to_string(no_lines)
    data = pytesseract.image_to_data(no_lines,config='--c tessedit_char_whitelist=1234567890abcdefghijklmnopqrstuvwxyz --psm 6')
    #boxes = pytesseract.image_to_boxes(no_lines)
    # remove a bunch of problem characters
    data_fixed = re.sub(ur'\u2014','',data)
    data_fixed = re.sub(ur'\ufb02','',data_fixed)
    data_fixed = re.sub(ur'\ufb01','',data_fixed)
    data_fixed = re.sub(ur'\xab','',data_fixed)
    data_fixed = re.sub(ur'\u2019','',data_fixed)
    data_fixed = re.sub(ur'\u2018','',data_fixed)
    data_fixed = re.sub(ur'\u201d','',data_fixed)
    data_fixed = re.sub(ur'\u201c','',data_fixed)
    data_fixed = re.sub(ur'\xb0','',data_fixed)
    data_fixed = re.sub(ur'\xe9','',data_fixed)
    data_fixed = re.sub(ur'\xa7','',data_fixed)
    data_fixed = re.sub(ur'\xa5','',data_fixed)
    data_fixed = re.sub(ur'\xa3','',data_fixed)
    data_fixed = re.sub(ur'\xa2','',data_fixed)
    data_fixed = re.sub(ur'\xbb','',data_fixed)
    data_fixed = re.sub(ur'\xa9','',data_fixed)
    data_fixed = re.sub(ur'\xae','',data_fixed)
    data_fixed = re.sub(ur'\u20ac','',data_fixed)
    
    # save the data
    file = open(s.join(["./outputs/raw_",side,"_output/",names[img_index][0:-4],"_raw.txt"]),'w')  
    file.write(data_fixed) 
    file.close() 
    
    # open the data and read it in
    data_mat = []
    with open(s.join(["./outputs/raw_",side,"_output/",names[img_index][0:-4],"_raw.txt"])) as f:
        data_mat.append([line.split() for line in f])
       
    
    # find how confident the thing is
    sum_of_conf = 0
    range2 = np.shape(data_mat)
    real_range = range2[1]
    for i in range(1,range2[1]):
        if int(float(data_mat[0][i][10]))<0:
            real_range = real_range-1
        elif int(float(data_mat[0][i][3]))>1:
            real_range = real_range-1
        else:
            sum_of_conf = sum_of_conf+int(float(data_mat[0][i][10]))
    
    #print("sum of the confidence:",sum_of_conf,"average confidence:",sum_of_conf/real_range)
    
    # reformat just what we want into a csv
    
    # remove everything with left less than 10 or greater than 1000, and top less than 10 or greater than 1700
    # or if the height or width is less than 10
    output_data_strings = np.array([])
    output_data_confs = np.array([])
    output_data_rows = np.array([])
    output_data_par = np.array([])
    for i in range(1,range2[1]):
        cur_left = int(float(data_mat[0][i][6]))
        cur_top = int(float(data_mat[0][i][7]))
        cur_height = int(float(data_mat[0][i][8]))
        cur_width = int(float(data_mat[0][i][9]))
        cur_conf = int(float(data_mat[0][i][10]))
        #if (cur_left<10) or (cur_left>3000) or (cur_top<20) or (cur_top>3000) or (cur_height<20) or (cur_width<10) or (cur_conf<50):
        if (cur_height<20) or (cur_width<30) or (cur_conf<50):
            x = 1
        else:
            output_data_strings = np.append(output_data_strings,data_mat[0][i][-1])
            output_data_confs = np.append(output_data_confs,int(data_mat[0][i][-2]))
            output_data_rows = np.append(output_data_rows,int(data_mat[0][i][4]))
            output_data_par = np.append(output_data_par,int(data_mat[0][i][3]))

    if any(x in ["sand","clay","Sand","Clay","SAND","CLAY"] for x in output_data_strings):
        contains_sand_or_clay = 1
    else:
        contains_sand_or_clay = 0


            # take the output data and rearrange it and then print it as a csv
    data_formated = []
    strings = []
    confs = []
    if len(output_data_rows) == 0:
        mean_conf = -1
    else:
        for j in range(int(output_data_par[0]),int(output_data_par[-1])+1):
            curr_par = output_data_strings[np.where(output_data_par[:]  == j)]
            curr_par_confs = output_data_confs[np.where(output_data_par[:] == j)]
            curr_rows = output_data_rows[np.where(output_data_par[:] == j)]
            try:
                for i in range(int(curr_rows[0]),int(curr_rows[-1])+1):
                    curr_strings = curr_par[np.where(curr_rows[:] == i)]
                    curr_confs = curr_par_confs[np.where(curr_rows[:] == i)]
                    strings.append([list(curr_strings)])
                    confs.append([list(curr_confs)])
            except:
                pass

        mean_conf = int(np.mean(output_data_confs))
        if mean_conf<70:
            level = "less_70/"
        elif mean_conf<75:
            level = "less_75/"
        elif mean_conf<80:
            level = "less_80/"
        elif mean_conf<90:
            level = "less_90/"
        else:
            level = "less_100/"
    
        range3 = np.shape(confs)
        with open(s.join(["./outputs/",side,"_output/",level,algo,names[img_index][0:-4],".txt"]), 'wb') as resultFile1:
            wr1 = csv.writer(resultFile1)
            for i in range(0,range3[0]):
                wr1.writerow(np.asarray(strings[i][0]))
        resultFile1.close()
            
        with open(s.join(["./outputs/conf_",side,"_output/",level,algo,names[img_index][0:-4],"_confs.txt"]), 'wb') as resultFile1:
            wr1 = csv.writer(resultFile1)
            for i in range(0,range3[0]):
                wr1.writerow(np.asarray(confs[i][0]))

        resultFile1.close()


    return mean_conf,contains_sand_or_clay
