
# import the necessary packages
import numpy as np
import argparse
import cv2
import math


height = 0;
width = 0;

def guidance(image):

	temp = np.zeros( (height,width), dtype = np.int8)
	print(np.shape(temp))


	for x in range(0,height):
		for y in range(0,width):
			px = image[x,y]
			M = max(px[0],px[1],px[2])
			temp[x,y] = M

	return temp

def fun_s(p,q):

	if( (p-q) >= 0 ):
		return 1
	else:
		return 0

def fun_w(p,q):

	sigma = 15
	res = float( abs( p - q) / (2*(sigma*sigma) ) )
	res = -res
	res = math.exp(res)
	return res

def filter(L,img):

	global height
	global width
	channel = 3
	filtered = np.zeros( (height,width), dtype=np.int8)
	print(np.shape(filtered))

	for x in range(0,height):
		for y in range(0,width):

			##### Extracting region of interest #####
			# handling upper-left boundary values
			if (x < 7 and y < 7):
				roi = img[0:x+7,0:y+7]

			# handling pixels where only x<7
			elif(x < 7):
				roi = img[0:x+7,y-7:y+7]

			# handling pixels where only y < 7
			elif(y < 7):
				roi = img[x-7:x+7,0:y+7]

			# handling right boundary
			elif( (x+7) > height and (y+7) > width):
				roi = img[x-7:height,y-7:width]

			# handling pixels where only x exceeds
			elif( (x+7) > height ):
				roi = img[x-7:height,y-7:y+7]

			# handling pixels where only y exceeds
			else:
				roi = img[x-7:x+7, y-7:width]

				
			
			# filter
			num = 0
			den = 0
			for k in range(0,255):
				s = fun_s(k,L[x,y])
				w = fun_w(k,L[x,y])
				num = num + s * w * freq(k,roi) * k
				den = den + s * w * freq(k,roi)
			en = num / den
			filtered[x,y] = en


			return filtered

def freq(k,roi):
	ht = np.size(roi,0)
	wt = np.size(roi,1)
	count = 0
	for i in range(0,ht):
		for j in range(0,wt):
			if( roi[i,j] == k ):
				count = count + 1

	return count
	
	
# function to get the reflectance
def decompose(image,k):

	global height,width


	ref =  np.zeros( (height,width,3), dtype=np.int8)
	#ref[:,:,:] = image[:,:,:] / k[:,:,:]

	for x in range(0,height):
		for y in range(0,width):
			if(k[x,y] != 0):
				ref[x,y,0] = image[x,y,0] / k[x,y]
				ref[x,y,1] = image[x,y,1] / k[x,y]
				ref[x,y,2] = image[x,y,2] / k[x,y]

			else:
				ref[x,y,0] = image[x,y,0]
				ref[x,y,1] = image[x,y,1]
				ref[x,y,2] = image[x,y,2]
	return ref

# function to construct image from reflectance and illumination
def get_enhanced(ref,fil):

	global height,width


	en =  np.zeros( (height,width,3), dtype=np.int8)

	for x in range(0,height):
		for y in range(0,width):

			# for blue channel
			en[x,y,0] = int(ref[x,y,0]) * int(fil[x,y])

			# for green channel
			en[x,y,1] = int(ref[x,y,1]) * int(fil[x,y])

			# for red channel
			en[x,y,2] = int(ref[x,y,2]) * int(fil[x,y])

	return en
	
# getting log 

def get_log(fil):

	global height,width
	Llg =  np.zeros( (height,width))
	epsilon = 1
	for x in range(0,height):
		for y in range(0,width):

			Llg[x,y] = np.log10(fil[x,y] + epsilon)

	return Llg


# delta function
def delta(x,y):

	if(x==y):
		return 1
	else:
		return 0	



# Calculating C.D.F
def cl(v):

	global width
	global height

	Llg = cv2.imread("Llg.jpeg")
	llg = cv2.cvtColor(Llg,cv2.COLOR_BGR2GRAY)
	fil = cv2.imread("k.jpeg")
	Lr = cv2.cvtColor(fil,cv2.COLOR_BGR2GRAY)
	num = 0
	den = 0

	for k in range(0,v):
		for i in range(0,height):
			for j in range(0,width):

				num = num + llg[i,j] * delta(k,Lr[i,j])
				den = den + llg[i,j]
	print "Values:-"	
	print num
	print den

	res = num / den
	print "From cl "
	print res
	print "Value sent"
	return res

# specified histogram
def s(z):

	epsilon = 1
	res = np.log10(z + epsilon)
	return res

# cdf for specific histogram	
def cf(z):

	num = 0
	den = 0
	for i in range(0,z):
		num = num + s(i)

	for i in range(0,255):
		den = den + s(i)

	res = num / den
	return(res)

# bi-log transformation
def blt(x):

	# L = gray levels
	print x;
	print "Values received"
	L = 256
	res = 0
	
	for v in range(0,255):
		print v
		print "Value above "
		print cf(v)
		print cl(x)
		if(int(cf(v)) == int(cl(x))):
			res = v
			break

	print("out of blt")

	return res	

# mapping of illumination
def mapped():

	global height
	global width
	

	fil = cv2.imread("k.jpeg")
	Lr = cv2.cvtColor(fil,cv2.COLOR_BGR2GRAY)
	print("shape of Lr")
	print(np.shape(Lr))
	Lm = np.zeros( (height,width), dtype=np.int8)
	print "Entering in the loop"
	for x in range(0,height):
		print "Entering in inner  loop"
		for y in range(0,width):
			print(Lr[x,y])
			#print "calling with "+ Lr[x,y]
			Lm[x,y] = blt(Lr[x,y])
			print Lm[x,y]
			
	print(".................... out of mapped ..................")
	return Lm


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image")
args = vars(ap.parse_args())

# load the image, apply the max RGB filter, and show the
# output images
image = cv2.imread(args["image"])

# since we need frequency characteristics of gray levels
gray_img = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

# calculating dimenions of input image 
height = np.size(image,0)
width = np.size(image,1)

# computing guidance image
L = guidance(image)


# filtering to get illumination
k = filter(L,gray_img)
print(np.shape(k))
cv2.imwrite('k.jpeg',L)
fil = cv2.imread("k.jpeg")
#print(np.shape(fil))

# display input
cv2.imshow("Input",image)

# display illumination
cv2.imshow("fil",fil)

fil_gray = cv2.cvtColor(fil,cv2.COLOR_BGR2GRAY)

# getting reflectance
refl = decompose(image,fil_gray)
cv2.imwrite("reflectance.jpeg",refl)

ref = cv2.imread("reflectance.jpeg")
cv2.imshow("reflectance",ref)




# constructing original image

org = get_enhanced(ref,fil_gray)
cv2.imwrite("org.jpeg",org)
org = cv2.imread("org.jpeg")
cv2.imshow("org",org)

#### Bi-log transformation ####

# calculate log of estimated illumination
Llg = get_log(fil_gray)
print("shape of Llg")
print(np.shape(Llg))
cv2.imwrite("Llg.jpeg",Llg)

# getting mapped illumination
Lm = mapped()

# getting enhanced image

enhanced = get_enhanced(ref,Lm)
cv2.imwrite("enhanced.jpeg",enhanced)
en = cv2.imread("enhanced.jpeg")
cv2.imshow("enhanced.jpeg",en)



cv2.waitKey(0)




