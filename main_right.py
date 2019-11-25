# import all the differently optimized algorithms, right now only solid_vert_lines and bold_letters are working well
import solid_vert_lines
import bold_letters
#import dashed_vert_lines
#import thick_text
#import faded_text
import sorting_cropping
import ocr_time
import time
from multiprocessing import Pool
from itertools import product

# first take the good pdfs and chop them into left and right sections
start = time.time()

# this script outputs the correct number of pdfs
number_of_pdfs = sorting_cropping.main()
finished_cropping = time.time()

# but can set it manually as the step above only needs to be done once
#number_of_pdfs=193

# TO DO
# fiddle with the algos below, the qualilty and thus size of the images was increased so the kernels and filters 
# need to be adjusted and tuned again.

# run the algorithms we have for every cropped pdf
algorithms = ["solid_vert_lines","bold_letters"]
for j in range(len(algos)):
	algo = algos[j]
	for i in range(number_of_pdfs-1):
		if algo == "solid_vert_lines":					# run the first algorithm
			temp_img,names = solid_vert_lines.main("right",i,0)
		elif algo == "bold_letters":					# run the second algorithm, add more elif steps for additional algorithms if needed
			temp_img,names = bold_letters.main("right",i,0)

		# find the average confidence from the algorithm, and some other stuff
		mean_conf,contains_s_c = ocr_time.main(temp_img,"right",names,i,algo)

		# print some information
		print("MC ",algo,": ",mean_conf,", CSC:",contains_s_c,", PDF:",names[i])

# time it all
finished_everything = time.time()
print(finished_cropping-start,finished_everything-finished_cropping)