# import the necessary packages
from imutils.object_detection import non_max_suppression
import numpy as np
# import pytesseract
import argparse
import cv2
import os
import time
import threading
import csv
import torch
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

def decode_predictions(scores, geometry):
	# grab the number of rows and columns from the scores volume, then
	# initialize our set of bounding box rectangles and corresponding
	# confidence scores
	(numRows, numCols) = scores.shape[2:4]
	rects = []
	confidences = []

	# loop over the number of rows
	for y in range(0, numRows):
		# extract the scores (probabilities), followed by the
		# geometrical data used to derive potential bounding box
		# coordinates that surround text
		scoresData = scores[0, 0, y]
		xData0 = geometry[0, 0, y]
		xData1 = geometry[0, 1, y]
		xData2 = geometry[0, 2, y]
		xData3 = geometry[0, 3, y]
		anglesData = geometry[0, 4, y]

		# loop over the number of columns
		for x in range(0, numCols):
			# if our score does not have sufficient probability,
			# ignore it
			if scoresData[x] < args["min_confidence"]:
				continue

			# compute the offset factor as our resulting feature
			# maps will be 4x smaller than the input image
			(offsetX, offsetY) = (x * 4.0, y * 4.0)

			# extract the rotation angle for the prediction and
			# then compute the sin and cosine
			angle = anglesData[x]
			cos = np.cos(angle)
			sin = np.sin(angle)

			# use the geometry volume to derive the width and height
			# of the bounding box
			h = xData0[x] + xData2[x]
			w = xData1[x] + xData3[x]

			# compute both the starting and ending (x, y)-coordinates
			# for the text prediction bounding box
			endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
			endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
			startX = int(endX - w)
			startY = int(endY - h)

			# add the bounding box coordinates and probability score
			# to our respective lists
			rects.append((startX, startY, endX, endY))
			confidences.append(scoresData[x])

	# return a tuple of the bounding boxes and associated confidences
	return (rects, confidences)


def decode_predictions(scores, geometry):
	# grab the number of rows and columns from the scores volume, then
	# initialize our set of bounding box rectangles and corresponding
	# confidence scores
	(numRows, numCols) = scores.shape[2:4]
	rects = []
	confidences = []
 
	# loop over the number of rows
	for y in range(0, numRows):
		# extract the scores (probabilities), followed by the
		# geometrical data used to derive potential bounding box
		# coordinates that surround text
		scoresData = scores[0, 0, y]
		xData0 = geometry[0, 0, y]
		xData1 = geometry[0, 1, y]
		xData2 = geometry[0, 2, y]
		xData3 = geometry[0, 3, y]
		anglesData = geometry[0, 4, y]
 
		# loop over the number of columns
		for x in range(0, numCols):
			# if our score does not have sufficient probability,
			# ignore it
			if scoresData[x] < args["min_confidence"]:
				continue
 
			# compute the offset factor as our resulting feature
			# maps will be 4x smaller than the input image
			(offsetX, offsetY) = (x * 4.0, y * 4.0)
 
			# extract the rotation angle for the prediction and
			# then compute the sin and cosine
			angle = anglesData[x]
			cos = np.cos(angle)
			sin = np.sin(angle)
 
			# use the geometry volume to derive the width and height
			# of the bounding box
			h = xData0[x] + xData2[x]
			w = xData1[x] + xData3[x]
 
			# compute both the starting and ending (x, y)-coordinates
			# for the text prediction bounding box
			endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
			endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
			startX = int(endX - w)
			startY = int(endY - h)
 
			# add the bounding box coordinates and probability score
			# to our respective lists
			rects.append((startX, startY, endX, endY))
			confidences.append(scoresData[x])
 
	# return a tuple of the bounding boxes and associated confidences
	return (rects, confidences)


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type=str,
	help="path to input image")
ap.add_argument("-east", "--east", type=str, default = "frozen_east_text_detection.pb",
	help="path to input EAST text detector")
ap.add_argument("-c", "--min-confidence", type=float, default=0.5,
	help="minimum probability required to inspect a region")
ap.add_argument("-w", "--width", type=int, default=320,
	help="nearest multiple of 32 for resized width")
ap.add_argument("-e", "--height", type=int, default=320,
	help="nearest multiple of 32 for resized height")
ap.add_argument("-p", "--padding", type=float, default=0.0,
	help="amount of padding to add to each border of ROI")
args = vars(ap.parse_args())


 
# Get the list of all files and directories
path = args["image"]
print(args)
confidence_thres = args["min_confidence"]


dir_list = os.listdir(path)
 
print("Files and directories in '", path, "' :")
 
# prints all files
print(dir_list)

result = {}
file_names = []

#net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
#net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
class CPU_multi_task_wraper:
	dir_sublist = [];
	t = None;
	def __init__(self, sublist):
		self.dir_sublist = sublist;
		self.t = threading.Thread(target = self.classify)
		self.t.start()
	def classify(self):
		net = cv2.dnn.readNet(args["east"])
		for i in self.dir_sublist:
		# load the input image and grab the image dimensions
			try:
				image = cv2.imread(args["image"]+"/"+i)
				orig = image.copy()
				(origH, origW) = image.shape[:2]
			except:
				print("unsupported file type")
				continue
			
			 
			# set the new width and height and then determine the ratio in change
			# for both the width and height
			(newW, newH) = (args["width"], args["height"])
			rW = origW / float(newW)
			rH = origH / float(newH)
			 
			# resize the image and grab the new image dimensions
			image = cv2.resize(image, (newW, newH))
			(H, W) = image.shape[:2]

			# define the two output layer names for the EAST detector model that
			# we are interested in -- the first is the output probabilities and the
			# second can be used to derive the bounding box coordinates of text
			layerNames = [
				"feature_fusion/Conv_7/Sigmoid",
				"feature_fusion/concat_3"]
			 
			# load the pre-trained EAST text detector
			#print("[INFO] loading EAST text detector...")

			
			


			# construct a blob from the image and then perform a forward pass of
			# the model to obtain the two output layer sets
			blob = cv2.dnn.blobFromImage(image, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop=False)
			net.setInput(blob)


			(scores, geometry) = net.forward(layerNames)
			
			# decode the predictions, then  apply non-maxima suppression to
			# suppress weak, overlapping bounding boxes
			(rects, confidences) = decode_predictions(scores, geometry)
			#print(confidences)
			boxes = non_max_suppression(np.array(rects), probs=confidences)

			  
			  # sort the results bounding box coordinates from top to bottom
			#results = sorted(results, key=lambda r:r[0][1])
			#print(len(boxes))
			#print(len(results));
			threshold = 5;
			
			result[i] = "HWT_Gen" if len(boxes)>threshold else "AT_Gen"

	def join(self):
		self.t.join()
'''
n = CPU_multi_task_wraper(dir_list)

n.join()



'''


thread_num = 2
n = len(dir_list)
threads = []
for i in range(thread_num):
	print(int(i*n/thread_num),int((i+1)*n/thread_num))
	thread = CPU_multi_task_wraper(dir_list[int(i*n/thread_num):int((i+1)*n/thread_num)])
	threads.append(thread)

for i in threads:
	i.join()


f = open('east_result.csv', 'w')
writer = csv.writer(f)
header = ["filename", "east_decision"]
writer.writerow(header)

for i in result.keys():
	writer.writerow([i,result[i]])


print(result,len(result))



