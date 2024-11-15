# Author: Sam Shenoi
# Description: This file generates a simple gui to demonstrate the PHP microbe algorithm

# Imports
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib_venn import venn2
import json

class UIScreen:
	def __init__(self):
		# Initial set up
		self.root = Tk()
		self.root.geometry("600x400")

		self.frame = Frame(self.root)
		self.frame.grid(row=0,column=0, sticky="n")


	def submit(self):
		data = self.feature_info.get()
		# Run the algorithm here

		# Display a pictorial representation here
		# Sets for testing.. Will use the sample data in the json file
		set1 = set(['A', 'B', 'C', 'D'])
		set2 = set(['C', 'D', 'E', 'F'])

		# Create Venn diagram
		venn2([set1, set2], ('Set 1', 'Set 2'))
		plt.savefig("outputimage.png")


		# Display the image
		# Technically there is a way to do it without saving the file, but I'm lazy and
		#   this way your user can have the image saved.
		#   https://www.geeksforgeeks.org/how-to-embed-matplotlib-charts-in-tkinter-gui/
		self.img = ImageTk.PhotoImage(file="outputimage.png")
		self.canvas.create_image(0, 0, anchor=NW, image=self.img)
		self.canvas.config(height=self.img.height(), width=self.img.width())
		self.canvas.update()



	def run(self):
		# Variables for holding data
		self.feature_info = StringVar()

		# Create basic UI
		ttk.Label(self.frame, text="Enter your symptoms, test results, risk factors!").grid(column=0, row=0)
		name_entry = ttk.Entry(self.frame,textvariable = self.feature_info, font=('calibre',10,'normal'))
		name_entry.grid(column=1, row=0)
		ttk.Button(self.frame, text="Submit", command=self.submit).grid(column=0, row=2)

		# Create a reusable canvas for displaying images
		self.canvas = Canvas(self.root, height=200, width=200)
		self.canvas.grid(row=2)
		# Run the main loop to keep the screen up
		self.root.mainloop()




if __name__ == "__main__":
	UIScreen().run()