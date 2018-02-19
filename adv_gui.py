import pygtk
pygtk.require('2.0')
import gtk
import pango
import numpy as np
import cv2
import math



text = " "
class SysInfo:

	# function to view input image
	def on_button_view_clicked(self,widget):
		pixbuf = gtk.gdk.pixbuf_new_from_file(text)

		pixbuf = pixbuf.scale_simple(800,500,gtk.gdk.INTERP_BILINEAR)
		self.image.set_from_pixbuf(pixbuf)
		self.image.show()


	# Function to get input image and process it
	def on_button_submit_clicked(self,widget):

		path = self.t1.get_text()
		global text
		text = path
		print text

		self.image.set_size_request(800,500)

		pixbuf = gtk.gdk.pixbuf_new_from_file(path)

		pixbuf = pixbuf.scale_simple(800,500,gtk.gdk.INTERP_BILINEAR)
		self.image.set_from_pixbuf(pixbuf)
		self.image.show()


		image = cv2.imread(path)

		ie = filter(image)
		cv2.imwrite('ie.jpg',ie)
		print("Illumination Estimated....")

		L = guidance(image)
		cv2.imwrite('L.jpg',L)
		print("Guidance Image Computed....")

		n = step(ie)
		print("Step-Up Function Computed....")

		e = exp_fun(ie)
		print("Exponential Function Computed....")

		enhanced = joint(n,e,ie)
		cv2.imwrite('enhanced.jpeg',enhanced)
		print("Image Enhanced....")

		self.t1.set_text("Done")


	# function to display the image resulting from illumination estimation
	def on_button_est_clicked(self,widget):

		pixbuf = gtk.gdk.pixbuf_new_from_file("ie.jpg")

		pixbuf = pixbuf.scale_simple(800,500,gtk.gdk.INTERP_BILINEAR)
		self.image.set_from_pixbuf(pixbuf)
		self.image.show()



	# function to display the guidance image
	def on_button_guidance_clicked(self,widget):

		pixbuf = gtk.gdk.pixbuf_new_from_file("L.jpg")

		pixbuf = pixbuf.scale_simple(800,500,gtk.gdk.INTERP_BILINEAR)
		self.image.set_from_pixbuf(pixbuf)
		self.image.show()



	def on_button_joint_clicked(self,widgrt):
		pixbuf = gtk.gdk.pixbuf_new_from_file("enhanced.jpeg")

		pixbuf = pixbuf.scale_simple(800,500,gtk.gdk.INTERP_BILINEAR)
		self.image.set_from_pixbuf(pixbuf)
		self.image.show()


	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("destroy",gtk.main_quit)
		self.window.set_border_width(5)
		self.window.set_title("Image Enhancement System")


		self.main_hbox = gtk.HBox()
		self.window.add(self.main_hbox)
		self.button_vbox = gtk.VBox()
		self.main_hbox.pack_start(self.button_vbox,expand=False)
		self.sec_vbox = gtk.VBox()


		self.main_hbox.pack_start(self.sec_vbox,expand=True)

		#filename_list = ["Input","illuination_estimation","guidance_image"]

		self.t1 = gtk.Entry(max=0)
		self.t1.set_activates_default(True)

		self.button_vbox.pack_start(self.t1,expand=False)


		button_view = gtk.Button("View input")
		button_submit = gtk.Button("Submit input")
		button_est = gtk.Button("Illumination est")
		button_guidance = gtk.Button("guidance img")
		button_joint = gtk.Button("joint edge preserving Filter")

		self.button_vbox.pack_start(button_submit,expand=False)
		self.button_vbox.pack_start(button_view,expand=False)
		self.button_vbox.pack_start(button_est,expand=False)
		self.button_vbox.pack_start(button_guidance,expand=False)
		#self.button_vbox.pack_start(button_step_up,expand=False)
		self.button_vbox.pack_start(button_joint,expand=False)


		button_submit.connect("clicked",self.on_button_submit_clicked)
		button_est.connect("clicked",self.on_button_est_clicked)
		button_guidance.connect("clicked",self.on_button_guidance_clicked)
		button_view.connect("clicked",self.on_button_view_clicked)
		#button_step_up.connect("clicked",self.on_button_step_up_clicked)
		button_joint.connect("clicked",self.on_button_joint_clicked)

		self.scroll_win = gtk.ScrolledWindow()


		self.label = gtk.Label("IMAGE ENHANCEMENT SYSTEM")
		self.label.set_size_request(50,100)

		self.sec_vbox.pack_start(self.label,expand=False,fill=True)

		self.sec_vbox.pack_start(self.scroll_win,expand=True,fill=True)
		self.image = gtk.Image()



		self.scroll_win.add_with_viewport(self.image)

		col = gtk.gdk.Color('#3b5998')
		self.window.modify_bg(gtk.STATE_NORMAL,col)

		self.window.show_all()



# function to calculate illumination estimation (Using local Max-RGB algorithm)
def filter(image):

	cv2.imwrite('fl.jpg',image)
	temp = cv2.imread('fl.jpg')

	height = np.size(temp,0)
	width = np.size(temp,1)


	ie = np.zeros( (height,width), dtype=np.int8)

	for x in range(0,height):
		for y in range(0,width):

			# Handling the pixel at origin (0,0)
			if(x == 0 and y == 0):
				roi = temp[0:1,0:1]
				max_blue = np.amax(roi[:,:,0])
				max_green = np.amax(roi[:,:,1])
				max_red = np.amax(roi[:,:,2])
				est = max(max_blue,max_green,max_red)
				ie[x,y] = est

			# Handling the pixel at upper boundary (where x = 0)
			elif(x == 0):
				roi = temp[0:1,y-1:y+1]
				max_blue = np.amax(roi[:,:,0])
				max_green = np.amax(roi[:,:,1])
				max_red = np.amax(roi[:,:,2])
				est = max(max_blue,max_green,max_red)
				ie[x,y] = est

			# Handling the pixel at left boundary (where y = 0)
			elif(y == 0):
				roi = temp[x-1:x+1,0:1]
				max_blue = np.amax(roi[:,:,0])
				max_green = np.amax(roi[:,:,1])
				max_red = np.amax(roi[:,:,2])
				est = max(max_blue,max_green,max_red)
				ie[x,y] = est

			# Handling the pixel at (height,width)
			elif(x == height and y == width):
				roi = temp[x-1:x,y-1:y]
				max_blue = np.amax(roi[:,:,0])
				max_green = np.amax(roi[:,:,1])
				max_red = np.amax(roi[:,:,2])
				est = max(max_blue,max_green,max_red)
				ie[x,y] = est

			# Handling the pixels at bottom boundary (where x = height)
			elif(x == height):
				roi = temp[x-1:x,y-1:y+1]
				max_blue = np.amax(roi[:,:,0])
				max_green = np.amax(roi[:,:,1])
				max_red = np.amax(roi[:,:,2])
				est = max(max_blue,max_green,max_red)
				ie[x,y] = est

			# Handling the pixels at right boundary (where y = width)
			elif(y == width):
				roi = temp[x-1:x+1,y-1:y]
				max_blue = np.amax(roi[:,:,0])
				max_green = np.amax(roi[:,:,1])
				max_red = np.amax(roi[:,:,2])
				est = max(max_blue,max_green,max_red)
				ie[x,y] = est


			# Handling Non-boundary pixels
			else:
				roi = temp[x-1:x+1,y-1:y+1]
				max_blue = np.amax(roi[:,:,0])
				max_green = np.amax(roi[:,:,1])
				max_red = np.amax(roi[:,:,2])
				est = max(max_blue,max_green,max_red)
				ie[x,y] = est


	return(ie)




# Function to calculate Guidance image (using Max-RGB algorithm)
def guidance(image):

	cv2.imwrite('fl.jpg',image)
	temp = cv2.imread('fl.jpg')

	height = np.size(temp,0)
	width = np.size(temp,1)


	for x in range(0,height):
		for y in range(0,width):
			px = temp[x,y]
			M = max(px[0],px[1],px[2])
			if(px[0] == M):
				px[1] = 0
				px[2] = 0
			elif(px[1] == M):
				px[0] = 0
				px[2] = 0
			else:
				px[0] = 0
				px[1] = 0

	return temp

# Step-Up Function
def step(ie):

	temp = cv2.imread('fl.jpeg')

	print(type(ie))

	L = cv2.imread('L.jpeg')



	height = np.size(temp,0)
	width = np.size(temp,1)
	channel = 3
	n = np.zeros( (height,width,channel), dtype=np.int8)



	for x in range(1,height-1):
		for y in range(1,width-1):

			roi = ie[x-1:x+1,y-1:y+1]

			# for blue Channel
			for i in range(x-1,x+1):
				for j in range(y-1,y+1):

					if( (ie[i,j] - L[x,y,0]) >= 0):
						n[i,j,0] = 1

					else:
						n[i,j,0] = 0


                        # for Green Channel
			for i in range(x-1,x+1):
				for j in range(y-1,y+1):

					if( (ie[i,j] - L[x,y,1]) >= 0):
						n[i,j,1] = 1

					else:
						n[i,j,1] = 0

			# for red Channel
			for i in range(x-1,x+1):
                                for j in range(y-1,y+1):

                                        if( (ie[i,j] - L[x,y,2]) >= 0):
                                                n[i,j,2] = 1

                                        else:
                                                n[i,j,2] = 0


	return n


# Exponential range Function
def exp_fun(ie):

	sigma = 80;

	temp = cv2.imread('fl.jpeg')
	height = np.size(temp,0)
	width = np.size(temp,1)
	channel = 3

	e = np.zeros( (height,width,channel), dtype=np.int8)
	L = cv2.imread('L.jpeg')

	for x in range(1,height-1):
		for y in range(1,width-1):


			for i in range(x-1,x+1):
				for j in range(y-1,y+1):

					# For Blue Channel
					res = float( abs( (ie[i,j] - L[x,y,0]) ) / (2*(sigma*sigma)) )
					res = -res
					res = math.exp(res)
					e[x,y,0] = res

					# For Green Channel
					res = float(abs( (ie[i,j] - L[x,y,1]) )/ (2*(sigma*sigma)) )
					res = -res
					res = math.exp(res)
					e[x,y,1] = res

					# For Red Channel
					res = float(abs( (ie[i,j] - L[x,y,2]) ) / (2*(sigma*sigma)) )
					res = -res
					res = math.exp(res)
					e[x,y,2] = res



	return e

# Joint edge-preserving Filter
def joint(n,e,ie):
	temp = cv2.imread('fl.jpeg')
	height = np.size(temp,0)
	width = np.size(temp,1)
	channel = 3

	numr = np.zeros( (height,width,channel), dtype=np.int8)
	den = np.zeros( (height,width,channel), dtype=np.int8)
	sum_numr = np.zeros( (height,width,channel), dtype=np.int8)
	sum_den = np.zeros( (height,width,channel), dtype=np.int8)
	k = np.zeros( (height,width,channel), dtype=np.int8)



	for i in range(0,height):
		for j in range(0,width):

			# For blue Channel
			numr[i,j,0] = n[i,j,0]*e[i,j,0]*ie[i,j]
			den[i,j,0] =  n[i,j,0]*e[i,j,0]

			# For Green Channel
			numr[i,j,1] = n[i,j,1]*e[i,j,1]*ie[i,j]
			den[i,j,1] =  n[i,j,1]*e[i,j,1]

			# For Red Channel
			numr[i,j,2] = n[i,j,2]*e[i,j,2]*ie[i,j]
			den[i,j,2] =  n[i,j,2]*e[i,j,2]

	for x in range(0,height):
		for y in range(0,width):

			#### Handling the pixel at origin(0,0) ####
			if(x == 0 and y == 0):
				# .... For Blue Channel .... #
				# For numerator
				roi_n = numr[0:1,0:1,0]
				sum_numr[x,y,0] = np.sum(roi_n)

				# For denominator
				roi_d = den[0:1,0:1,0]
				sum_den[x,y,0] = np.sum(roi_d)

				# .... For Green Channel .... #
				# For numerator
				roi_n = numr[0:1,0:1,1]
				sum_numr[x,y,1] = np.sum(roi_n)

				# For denominator
				roi_d = den[0:1,0:1,1]
				sum_den[x,y,1] = np.sum(roi_d)

				# .... For Red Channel .... #
				# For numerator
				roi_n = numr[0:1,0:1,2]
				sum_numr[x,y,2] = np.sum(roi_n)

				# For denominator
				roi_d = den[0:1,0:1,2]
				sum_den[x,y,2] = np.sum(roi_d)

			##### Handling the pixel at upper boundary (where x = 0)
			elif(x == 0):
				# .... For Blue Channel .... #
				# For numerator
				roi_n = numr[0:1,y-1:y+1,0]
				sum_numr[x,y,0] = np.sum(roi_n)

				# For denominator
				roi_d = den[0:1,y-1:y+1,0]
				sum_den[x,y,0] = np.sum(roi_d)

				# .... For Green Channel .... #
				# For numerator
				roi_n = numr[0:1,y-1:y+1,1]
				sum_numr[x,y,1] = np.sum(roi_n)

				# For denominator
				roi_d = den[0:1,y-1:y+1,1]
				sum_den[x,y,1] = np.sum(roi_d)

				# .... For Red Channel .... #
				# For numerator
				roi_n = numr[0:1,y-1:y+1,2]
				sum_numr[x,y,2] = np.sum(roi_n)

				# For denominator
				roi_d = den[0:1,y-1:y+1,2]
				sum_den[x,y,2] = np.sum(roi_d)

			##### Handling the pixels at left boundary (where y = 0)
			elif(y == 0):
				# .... For blue Channel .... #
				# For numerator
				roi_n = numr[x-1:x+1,0:1,0]
				sum_numr[x,y,0] = np.sum(roi_n)

				# For denominator
				roi_d = den[x-1:x+1,0:1,0]
				sum_den[x,y,0] = np.sum(roi_d)

				# .... For Green Channel .... #
				# For numerator
				roi_n = numr[x-1:x+1,0:1,1]
				sum_numr[x,y,1] = np.sum(roi_n)

				# For denominator
				roi_d = den[x-1:x+1,0:1,1]
				sum_den[x,y,1] = np.sum(roi_d)


				# .... For Red Channel .... #
				# For numerator
				roi_n = numr[x-1:x+1,0:1,2]
				sum_numr[x,y,2] = np.sum(roi_n)

				# For denominator
				roi_d = den[x-1:x+1,0:1,2]
				sum_den[x,y,2] = np.sum(roi_d)

			##### Handling the pixel at (height,width)
			elif(x == height and y == width):
				# ....For blue Channel .... #
				# For numerator
                                roi_n = numr[x-1:x,y-1:y,0]
				sum_numr[x,y,0] = np.sum(roi_n)

				# For denominator
				roi_d = den[x-1:x,y-1:y,0]
				sum_den[x,y,0] = np.sum(roi_d)

				# .... For Green Channel .... #
				# For numerator
                                roi_n = numr[x-1:x,y-1:y,1]
				sum_numr[x,y,1] = np.sum(roi_n)

				# For denominator
				roi_d = den[x-1:x,y-1:y,1]
				sum_den[x,y,1] = np.sum(roi_d)

				# .... For Red .... #
				# For numerator
                                roi_n = numr[x-1:x,y-1:y,2]
				sum_numr[x,y,2] = np.sum(roi_n)

				# For denominator
				roi_d = den[x-1:x,y-1:y,2]
				sum_den[x,y,2] = np.sum(roi_d)

			##### Handling pixels at bottom boundary (where x = height)
			elif(x == height):

				# .... For Blue Channel .... #
				# For numerator
				roi_n = numr[x-1:x,y-1:y+1,0]
				sum_numr[x,y,0] = np.sum(roi_n)

				# For denominator
				roi_d = den[x-1:x,y-1:y+1,0]
				sum_den[x,y,0] = np.sum(roi_d)


				# .... For Green Channel .... #
				# For numerator
				roi_n = numr[x-1:x,y-1:y+1,1]
				sum_numr[x,y,1] = np.sum(roi_n)

				# For denominator
				roi_d = den[x-1:x,y-1:y+1,1]
				sum_den[x,y,1] = np.sum(roi_d)


				# .... For Red Channel .... #
				# For numerator
				roi_n = numr[x-1:x,y-1:y+1,2]
				sum_numr[x,y,2] = np.sum(roi_n)

				# For denominator
				roi_d = den[x-1:x,y-1:y+1,2]
				sum_den[x,y,2] = np.sum(roi_d)


			# Handling Pixels at right Boundary (where x = width)
			elif(y == width):

				# .... For Blue Channel .... #
				# For numerator
				roi_n = numr[x-1:x+1,y-1:y,0]
				sum_numr[x,y,0] = np.sum(roi_n)

				# For Denominator
				roi_d = den[x-1:x+1,y-1:y,0]
				sum_den[x,y,0] = np.sum(roi_d)

				# .... For Green Channel .... #
				# For numerator
				roi_n = numr[x-1:x+1,y-1:y,1]
				sum_numr[x,y,1] = np.sum(roi_n)

				# For Denominator
				roi_d = den[x-1:x+1,y-1:y,1]
				sum_den[x,y,1] = np.sum(roi_d)

				# .... For Red Channel .... #
				# For numerator
				roi_n = numr[x-1:x+1,y-1:y,2]
				sum_numr[x,y,2] = np.sum(roi_n)

				# For Denominator
				roi_d = den[x-1:x+1,y-1:y,2]
				sum_den[x,y,2] = np.sum(roi_d)



			#### Handling Non-Boundary values ####
			else:
				### For blue Channel

				# for numerator
				roi_n = numr[x-1:x+1,y-1:y+1,0]
				sum_numr[x,y,0] = np.sum(roi_n)

				# for denominator
				roi_d = den[x-1:x+1,y-1:y+1,0]
				sum_den[x,y,0] =  np.sum(roi_d)

				### For Green Channel

				# for numerator
				roi_n = numr[x-1:x+1,y-1:y+1,1]
				sum_numr[x,y,1] = np.sum(roi_n)

				# for denominator
				roi_d = den[x-1:x+1,y-1:y+1,1]
				sum_den[x,y,1] =  np.sum(roi_d)

				### For Red Channel

				# for numerator
				roi_n = numr[x-1:x+1,y-1:y+1,2]
				sum_numr[x,y,2] = np.sum(roi_n)

				# for denominator
				roi_d = den[x-1:x+1,y-1:y+1,2]
				sum_den[x,y,2] =  np.sum(roi_d)


	for i in range(0,height):
		for j in range(0,width):

			# No need to handle boundary pixels separately

			# For Blue Channel
			k[x,y,0] = sum_numr[x,y,0] / sum_den[x,y,0]

			# For Green Channel
			k[x,y,1] = sum_numr[x,y,1] / sum_den[x,y,1]

			# For Red Channel
			k[x,y,2] = sum_numr[x,y,2] / sum_den[x,y,2]

	return(k)


SysInfo()
gtk.main()
