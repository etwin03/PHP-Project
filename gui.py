# Author: Sam Shenoi
# Description: This file generates a simple gui to demonstrate the PHP microbe algorithm

# Imports
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib_venn import venn2
import json
import requests
from main_algorithm import *
import numpy as np

class UIScreen:
	def __init__(self):
		# Initial set up
		self.root = Tk()
		self.root.geometry("1000x600")

		self.frame = Frame(self.root)
		self.frame.grid(row=0,column=0, sticky="n")

		#createAllMicrobeData()
		#global allSymptoms
		#allSymptoms = requests.get('https://idwebsite.herokuapp.com/getAllSymptoms').json()



	def submit(self):
		userData = [self.symptoms.get(), self.testResults.get(), self.riskFactors.get()]
		symptoms, testResults, riskFactors = processUserData(userData)
		# Run the algorithm here
		global sortedMicrobeNames
		sortedMicrobes, sortedMicrobeNames = main_algorithm(symptoms, testResults, riskFactors)

		# Display a pictorial representation here

		# make data:

		topTenMicrobeNames = []
		topTenMicrobeNames2 = []
		topTenMicrobeValues = []
		count = 0
		for microbe in sortedMicrobeNames:
			if count == 5:
				break
			topTenMicrobeNames.append(microbe)
			topTenMicrobeNames2.append(microbe[0:-1])
			topTenMicrobeValues.append(sortedMicrobeNames[microbe])
			count += 1

		# plot
		plt.rcParams["figure.figsize"] = (10,4)
		fig, ax = plt.subplots()

		

		p = ax.barh(np.arange(5), topTenMicrobeValues)
		ax.bar_label(p, label_type='center', fmt='%.3f')	

		ax.set_yticks(np.arange(5), labels=topTenMicrobeNames2)
		ax.invert_yaxis()
			

		ax.set(xlim=(0, sortedMicrobeNames[topTenMicrobeNames[0]] * 1.5))

		#plt.figure(constrained_layout=True)
		plt.tight_layout()

		plt.savefig("outputimage.png")


		# Display the image
		# Technically there is a way to do it without saving the file, but I'm lazy and
		#   this way your user can have the image saved.
		#   https://www.geeksforgeeks.org/how-to-embed-matplotlib-charts-in-tkinter-gui/
		self.img = ImageTk.PhotoImage(file="outputimage.png")
		self.canvas.create_image(0, 0, anchor=NW, image=self.img)
		self.canvas.config(height=self.img.height(), width=self.img.width())
		self.canvas.update()

	def displayRanks(self):
		for widget in self.frame.grid_slaves():
			widget.grid_forget()
		self.canvas.delete('all')
		tRanks = Text(self.frame)
		count = 1
		for microbe in sortedMicrobeNames:
			if microbe[-1] == '0':
				tRanks.insert(END, '\n' + f'{count}. {microbe[0:-1]}')
			if microbe[-1] == '1':
				tRanks.insert(END, '\n' + f'{count}. {microbe[0:-1]}')
			if microbe[-1] == '2':
				tRanks.insert(END, '\n' + f'{count}. {microbe[0:-1]}')
			if microbe[-1] == '3':
				tRanks.insert(END, '\n' + f'{count}. {microbe[0:-1]}')
			count += 1
		tRanks.grid(column=0, row=0)
		ttk.Button(self.frame, text="Return", command=self.run).grid(column=1, row=1)
			

	def run(self):
		for widget in self.frame.grid_slaves():
			widget.grid_forget()

		# Variables for holding data
		self.symptoms = StringVar()
		self.testResults = StringVar()
		self.riskFactors = StringVar()

		# Create basic UI
		ttk.Label(self.frame, text="Enter your symptoms").grid(column=0, row=0, sticky='w')
		ttk.Label(self.frame, text="Enter your test results").grid(column=0, row=1, sticky='w')
		ttk.Label(self.frame, text="Enter your risk factors").grid(column=0, row=2, sticky='w')
		eSymptoms = ttk.Entry(self.frame,textvariable = self.symptoms, font=('calibre',10,'normal'))
		eTestResults = ttk.Entry(self.frame,textvariable = self.testResults, font=('calibre',10,'normal'))
		eRiskFactors = ttk.Entry(self.frame,textvariable = self.riskFactors, font=('calibre',10,'normal'))
		eSymptoms.grid(column=1, row=0, sticky = 'w')
		eTestResults.grid(column=1, row=1, sticky = 'w')
		eRiskFactors.grid(column=1, row=2, sticky = 'w')
		ttk.Button(self.frame, text="Submit", command=self.submit).grid(column=0, row=3)
		ttk.Button(self.frame, text="Display Ranks", command=self.displayRanks).grid(column=2,row=4)

		# Create a reusable canvas for displaying images
		self.canvas = Canvas(self.root, height=200, width=200)
		self.canvas.grid(column=0, columnspan=2, row=4)
		# Run the main loop to keep the screen up
		self.root.mainloop()




if __name__ == "__main__":
	UIScreen().run()