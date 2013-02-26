# Nicholas Balsbaugh & Alex Swanson
# CS251 - Data Analysis and Visualization
# Project 7 - PCA & Clustering
# Professor Bruce Maxwell
# April 9th, 2011


# Imports
import Tkinter as tk
import tkFileDialog
from ViewRef import ViewRef
import numpy as np
import pylab
import dialogPop
import math
from Tkinter import IntVar, StringVar, PhotoImage, Label, OptionMenu, Button, Entry
import os.path
import DataSet as ds
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import csv


class VIOLAS:
	"""Visual Information Observation, Logging and Analysis System"""

##### Initialization ####################################################################
	
	def __init__( self, width, height ):
		"""Initialize the Main Class for VIOLAS Program"""
		
		self.root = tk.Tk()
		self.desiredFile = None
		self.width = width
		self.height = height
		self.root.title("Welcome")
		w = tk.Message(self.root, 
					   text= " \n\n " +
					   "	Welcome to V.I.O.L.A.S.!\n\n" + 
					" Visual Information Observation, Logging, \n "
					"	   and Analysis System\n\n\n" +
					"  Please choose the desired CSV file you \n" +
					"	   would like to analyze! " +
					" \n\n\n ",
					background='blue', foreground='white', border=0, width=300, font='courier 12 bold')	 
		w.pack()

		fobj = tkFileDialog.askopenfile( parent=self.root, mode='rb', title='Choose a data file...' )
		self.desiredFile = os.path.basename(fobj.name)
		self.fileNameShort = os.path.splitext(self.desiredFile)[0]
		
		self.root.destroy()
		
		self.dataHandler = ds.DataSet( self, filename=fobj.name )
		
		self.root = tk.Tk()
		self.root.title("Configure PCA")
		self.root.geometry( "350x200-80+80" )
		
		self.pcaCut = StringVar( self.root )
		self.pcaCut.set( "Yes" )
		Label(self.root, text="Remove Last Column?").grid(row=0)
		k = apply( OptionMenu, ( self.root, self.pcaCut ) + ( "Yes", "No" ) )
		k.grid( row=0, column=1 )
		
		self.pcaNormalize = StringVar( self.root )
		self.pcaNormalize.set( "No" )
		Label(self.root, text="Normalize Before PCA?").grid(row=1)
		j = apply( OptionMenu, ( self.root, self.pcaNormalize ) + ( "No", "Yes" ) )
		j.grid( row=1, column=1 )
		
		self.varPercent = IntVar( self.root )
		self.varPercent.set( 100 )
		Label(self.root, text="Minimum Percent Variation").grid(row=2)
		l = Entry( self.root, textvariable=self.varPercent )
		l.grid(row=2, column=1)

		def callback():
			self.root.destroy()
			pcaData = self.dataHandler.buildPCA( self.dataHandler.numbData )
			self.vectorHandler = ds.DataSet( self, passData=pcaData )
			print self.eigenList
			self.initializeGUI( width, height )
		
		b = Button( self.root, text="Continue", command=callback )
		b.grid( row=3, columnspan=2 )
		



##### GUI Construction ##################################################################

	def initializeGUI( self, width, height ):
		"""Initialize the GUI."""

		# Create a Tk() object, which is the root window.
		self.root = tk.Tk()
		
		# Set the width, height and placement of the window.
		self.initDx = width
		self.initDy = height
		self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )
		self.root.maxsize( 1024, 768 )
		self.root.lift()

		# Set the title of the window
		self.root.title("V.I.O.L.A.S.++")

		# setup the menus
		if self.desiredFile == None:
			return 
		elif self.desiredFile == "BirdArrivals.csv":
			self.buildMenusBird()
		elif self.desiredFile == "EyeTracking.csv":
			self.buildMenusEye()
		elif self.desiredFile == "AustraliaCoast.csv":
			self.buildMenusCoast()
		else:
			self.buildMenusStandard()

		# Build the controls
		self.buildControls()

		# Build the objects on the Canvas
		self.buildCanvas()

		# Set up the key bindings
		self.setBindings() 
		
		# Set up the application state
		self.objects = []
		self.data = None
		
		# Sets up the shape management
		self.currentColor = "red"
		self.currentSize = 1
		self.shapeSize = 4
		self.sizeList = []
		self.shapes = []
		
		# Sets up the axis management
		self.vr = ViewRef()
		self.axesGFX = []
		self.axeslist = []
		self.axes = np.matrix( [ [ 0, 0, 0, 1 ],
								 [ 1, 0, 0, 1 ],
								 [ 0, 0, 0, 1 ],
								 [ 0, 1, 0, 1 ],
								 [ 0, 0, 0, 1 ],
								 [ 0, 0, 1, 1 ] ])
		self.buildAxes()
		
		# Copy the extent field used in handleButton3 and handlebutton3Motion 
		self.copyextent = []
		
		# List that contains the data points
		self.dpts = []
		self.data = []
		self.plotMatrix = []
		
		# Set up 3D speed management
		self.changeSpeed = 1 
		self.scaleMult = 0.1
		self.rotateConstant = 200

		
		# Set up the data display options
		self.colorUse = None
		self.colorRange = None
		self.sizeUse = None
		self.sizeMean = None
		
		# Set up the legend headers
		self.xAxisHeader = None
		self.yAxisHeader = None
		self.zAxisHeader = None
		self.colorHeader = None
		self.sizeHeader = None


	def buildCanvas(self):
		"""Create the canvas object."""
		self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy )
		self.canvas.pack( expand=tk.YES, fill=tk.BOTH )
		return


	def buildControls(self):
		"""" Build a frame and put controls in it."""
		# make a control frame
		self.cntlframe = tk.Frame(self.root)
		self.cntlframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)
		sep = tk.Frame( self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
		sep.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)

		self.var = StringVar( self.cntlframe )
		self.var.set("Oval")
		
		# Set up a legend gradient for the graph
		maxLabel = tk.Label(self.cntlframe, text="Max")
		maxLabel.pack()
		gradient = PhotoImage(file="gb.gif")
		label = tk.Label(self.cntlframe, image=gradient)
		label.pack()
		minLabel = tk.Label(self.cntlframe, text="Min")
		minLabel.pack()
		self.photo = gradient # keep a reference
		return




##### Menu Cases ########################################################################
	
	def buildMenusStandard(self):
		"""Menu for the Standard CSV file"""
		# create a new menu
		self.menu = tk.Menu(self.root)

		# set the root menu to our new menu
		self.root.config(menu = self.menu)

		# create a variable to hold the individual menus
		self.menulist = []

		#create a menu for information about the program
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "About", menu = cmdmenu )
		self.menulist.append(cmdmenu)
		
		# create a file menu
		filemenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "File", menu = filemenu )
		self.menulist.append(filemenu)
		
		# create a menu for graphs
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "Graphs", menu = cmdmenu )
		self.menulist.append(cmdmenu)
		
		
		# create a menu for calculations
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "Calculations", menu = cmdmenu )
		self.menulist.append(cmdmenu)
		
		# create a menu to view the data set
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "View Data", menu = cmdmenu )
		self.menulist.append(cmdmenu)

		# menu text for the elements
		menutext = [ [ 'Information About Program' ],
					 [ 'Open New File...\t\t\xE2\x8C\x98O', '-', 'Save As...', 'Save PCA As...', 'Export to ARFF...', 'Export to ARFF PCA...', '-', 'Quit\t\t\t\t\xE2\x8C\x98Q' ],
					 [ 'Histogram...', 'Scatterplot...', '-', 'Plot PCA...', '-', 'Box Plot...' ],
					 [ 'Mean', 'Median', 'Mode', 'Range', 'Standard Deviation', '-', 'All Calculations'],
					 [ 'View Data Set' ] ]

		# menu callback functions
		menucmd = [ [self.handleAbout],
					[self.handleOpenNew, None, self.handleSaveCSV, self.handleSavePCA, self.handleExportARFF, self.handleExportARFFPCA, None, self.handleQuit],
					[self.handleCmd1, self.handleCmd2, None, self.handleCmdPCA, None, self.handleCmd7 ],
					[self.handleCmd3, self.handleCmd4, self.handleCmd5, self.handleCmd8, self.handleCmd9, None, self.handleCmd6],
					[self.handleView] ]
		
		# build the menu elements and callbacks
		for i in range( len( self.menulist ) ):
			for j in range( len( menutext[i]) ):
				if menutext[i][j] != '-':
					self.menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
				else:
					self.menulist[i].add_separator()
		

	def buildMenusBird(self):
		"""Menu for the Arrival Bird CSV file"""
		# Create a new menu
		self.menu = tk.Menu(self.root)

		# Set the root menu to our new menu
		self.root.config(menu = self.menu)

		# create a variable to hold the individual menus
		self.menulist = []

		# Create a menu for information about the program
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "About", menu = cmdmenu )
		self.menulist.append(cmdmenu)
		
		# Create a file menu
		filemenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "File", menu = filemenu )
		self.menulist.append(filemenu)
		
		# Create a menu for graphs
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "Graphs", menu = cmdmenu )
		self.menulist.append(cmdmenu)
		
		# Create a menu for specialize graphs
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "Special", menu = cmdmenu )
		self.menulist.append(cmdmenu)	

		# Create a menu for calculations
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "Calculations", menu = cmdmenu )
		self.menulist.append(cmdmenu)
		
		# Create a menu to view the data set
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "View Data", menu = cmdmenu )
		self.menulist.append(cmdmenu)

		# Menu text for the elements
		menutext = [ [ 'Information About Program' ],
					 [ 'Open New File...\t\t\xE2\x8C\x98O', '-', 'Save As...', 'Save PCA As...', 'Export to ARFF...', 'Export to ARFF PCA...', '-', 'Quit\t\t\t\t\xE2\x8C\x98Q' ],
					 [ 'Histogram...', 'Scatterplot...', '-', 'Plot PCA...', '-', 'Box Plot...' ],
					 [ 'Boxplot Analysis for Arrival Date by Region' ],
					 [ 'Mean', 'Median', 'Mode', 'Range', 'Standard Deviation', '-', 'All Calculations'],
					 [ 'View Data Set' ] ]

		# Menu callback functions
		menucmd = [ [self.handleAbout],
					[self.handleOpenNew, None, self.handleSaveCSV, self.handleSavePCA, self.handleExportARFF, self.handleExportARFFPCA, None, self.handleQuit],
					[self.handleCmd1, self.handleCmd2, None, self.handleCmdPCA, None, self.handleCmd7 ],
					[self.handleSpecial2 ],
					[self.handleCmd3, self.handleCmd4, self.handleCmd5, self.handleCmd8, self.handleCmd9, None, self.handleCmd6],
					[self.handleView] ]
		
		# Build the menu elements and callbacks
		for i in range( len( self.menulist ) ):
			for j in range( len( menutext[i]) ):
				if menutext[i][j] != '-':
					self.menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
				else:
					self.menulist[i].add_separator()


	def buildMenusEye(self):
		"""Menu for the Eye Tracking CSV file"""
		# Create a new menu
		self.menu = tk.Menu(self.root)

		# Set the root menu to our new menu
		self.root.config(menu = self.menu)

		# Create a variable to hold the individual menus
		self.menulist = []

		# Create a menu for information about the program
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "About", menu = cmdmenu )
		self.menulist.append(cmdmenu)
		
		# Create a file menu
		filemenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "File", menu = filemenu )
		self.menulist.append(filemenu)
		
		# Create a menu for graphs
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "Graphs", menu = cmdmenu )
		self.menulist.append(cmdmenu)
		
		# Create a menu for calculations
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "Special", menu = cmdmenu )
		self.menulist.append(cmdmenu)

		# Create a menu to view the data set
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "View Data", menu = cmdmenu )
		self.menulist.append(cmdmenu)

		# Menu text for the elements
		menutext = [ [ 'Information About Program' ],
					 [ 'Open New File...\t\t\xE2\x8C\x98O', '-', 'Save As...', 'Save PCA As...', 'Export to ARFF...', 'Export to ARFF PCA...', '-', 'Quit\t\t\t\t\xE2\x8C\x98Q' ],
					 [ 'Histogram...', 'Scatterplot...', '-', 'Plot PCA...', '-', 'Box Plot...' ],
					 [ 'View Fixation Results'],
					 [ 'Mean', 'Median', 'Mode', 'Range', 'Standard Deviation', '-', 'All Calculations'],
					 [ 'View Data Set' ] ]

		# Menu callback functions
		menucmd = [ [self.handleAbout],
					[self.handleOpenNew, None, self.handleSaveCSV, self.handleSavePCA, self.handleExportARFF, self.handleExportARFFPCA, None, self.handleQuit],
					[self.handleCmd1, self.handleCmd2, None, self.handleCmdPCA, None, self.handleCmd7 ],
					[self.handleSpecial1],
					[self.handleCmd3, self.handleCmd4, self.handleCmd5, self.handleCmd8, self.handleCmd9, None, self.handleCmd6],
					[self.handleView] ]
		
		# Build the menu elements and callbacks
		for i in range( len( self.menulist ) ):
			for j in range( len( menutext[i]) ):
				if menutext[i][j] != '-':
					self.menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
				else:
					self.menulist[i].add_separator()


	def buildMenusCoast(self):
		"""Menu for the Australia Coast CSV file"""
		# create a new menu
		self.menu = tk.Menu(self.root)

		# set the root menu to our new menu
		self.root.config(menu = self.menu)

		# create a variable to hold the individual menus
		self.menulist = []

		#create a menu for information about the program
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "About", menu = cmdmenu )
		self.menulist.append(cmdmenu)
		
		# create a file menu
		filemenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "File", menu = filemenu )
		self.menulist.append(filemenu)
		
		# create a menu for graphs
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "Graphs", menu = cmdmenu )
		self.menulist.append(cmdmenu)
		
		# create a menu for calculations
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "Calculations", menu = cmdmenu )
		self.menulist.append(cmdmenu)
		
		# create a menu to view the data set
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "View Data", menu = cmdmenu )
		self.menulist.append(cmdmenu)

		# menu text for the elements
		menutext = [ [ 'Information About Program' ],
					 [ 'Open New File...\t\t\xE2\x8C\x98O', '-', 'Save As...', 'Save PCA As...', 'Export to ARFF...', 'Export to ARFF PCA...', '-', 'Quit\t\t\t\t\xE2\x8C\x98Q' ],
					 [ 'Histogram...', 'Scatterplot...', '-', 'Plot PCA...', '-', 'Box Plot...' ],
					 [ 'Mean', 'Median', 'Mode', 'Range', 'Standard Deviation', '-', 'All Calculations'],
					 [ 'View Data Set' ] ]

		# menu callback functions
		menucmd = [ [self.handleAbout],
					[self.handleOpenNew, None, self.handleSaveCSV, self.handleSavePCA, self.handleExportARFF, self.handleExportARFFPCA, None, self.handleQuit],
					[self.handleCmd1, self.handleCmd2, None, self.handleCmdPCA, None, self.handleCmd7 ],
					[self.handleCmd3, self.handleCmd4, self.handleCmd5, self.handleCmd8, self.handleCmd9, None, self.handleCmd6],
					[self.handleView] ]
		
		# build the menu elements and callbacks
		for i in range( len( self.menulist ) ):
			for j in range( len( menutext[i]) ):
				if menutext[i][j] != '-':
					self.menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
				else:
					self.menulist[i].add_separator()





##### Key and Mouse Binding #############################################################

	def setBindings(self):
		"""Sets the key bindings to functions."""
		self.root.bind( '<Button-1>', self.handleButton1 )
		self.root.bind( '<Button-2>', self.handleButton2 )
		self.root.bind( '<Button-3>', self.handleButton3 )
		self.root.bind( '<B1-Motion>', self.handleButton1Motion )
		self.root.bind( '<B2-Motion>', self.handleButton2Motion )
		self.root.bind( '<B3-Motion>', self.handleButton3Motion )
		self.root.bind( '<Command-q>', self.handleModQ )
		self.root.bind( '<Command-o>', self.handleModO )
		self.root.bind( '<Command-s>', self.handleModS )
		self.root.bind( '<Command-e>', self.handleModE )
		



##### Handle Key-Presses ################################################################

	def handleModQ(self, event):
		"""Handles the CMD-Q quit key press."""
		self.handleQuit()

		
	def handleQuit(self):
		"""Handles the Quit scenario."""
		self.root.destroy()


	def handleModO(self, event):
		"""Handles the CMD-O open key press."""	
		self.handleOpenNew()
		
	
	def handleModS( self, event ):
		"""Handles the CMD-S save key press."""
		self.handleSaveCSV()
		
		
	def handleModE( self, event ):
		"""Handle the CMS-E export key press."""
		self.handleExportARFF()



##### Mouse Commands ####################################################################

	def handleButton1(self, event):
		"""Get the location of the Button 1 press."""
		self.baseClick = (event.x, event.y)


	def handleButton2(self, event):
		"""Get the location of the Button 2 press."""
		self.baseClick2 = (event.x, event.y)
	

	def handleButton3( self, event ):
		"""Get the location of the Button 3 press."""
		self.scaleEvent = ( event.x, event.y )
		self.originalExtent = self.vr.extent


	def handleButton1Motion(self, event):
		"""Handle button 1, which controls the moving."""
		diff = ( float(event.x - self.baseClick[0]), float(event.y - self.baseClick[1]) )
		self.baseClick = ( event.x, event.y )
		dx = diff[0]/self.vr.view[0]
		dy = diff[1]/self.vr.view[1]
		delta0 = self.changeSpeed*dx*self.vr.extent[0]
		delta1 = self.changeSpeed*dy*self.vr.extent[1]
		self.vr.vrp += delta0*self.vr.u
		self.vr.vrp += delta1*self.vr.vup
		self.updateAxes()
		self.updatePlot()
		
	
	def handleButton2Motion(self, event):
		"""Handle button 2, which controls the rotation."""
		diff = ( float(event.x - self.baseClick2[0]), float(event.y - self.baseClick2[1]) )
		delta0 = ( diff[0]/self.rotateConstant )*math.pi
		delta1 = -((diff[1]/self.rotateConstant)*math.pi)
		if len(self.axesToPlot) == 3:
			self.vr.rotateVRC( delta0, delta1, 0 )
		elif len(self.axesToPlot) == 2:
			self.vr.rotateVRC( 0, 0, delta1 )
		self.updateAxes()
		self.baseClick2 = ( event.x, event.y )
		self.updatePlot()


	def handleButton3Motion( self, event ):
		"""Handle button 3, which controls the scaling."""
		diff = float(event.y - self.scaleEvent[1])
		sFactor = 1 + (diff*self.scaleMult)
		if ( sFactor > 3 ):
			sFactor = 3
		elif ( sFactor < 0.1):
			sFactor = 0.1
		extentVal = self.originalExtent[0] * sFactor
		self.shapeSize = self.shapeSize / sFactor
		self.vr.extent = [ extentVal, extentVal, extentVal ]
		self.updateAxes()
		self.shapeSize = 4 / self.vr.extent[0]
		self.updatePlot()




##### Menu Commands #####################################################################		
	
	def handleCmd1(self):
		print 'handling command 1'
		
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			if self.dataHandler.metaData[i][1] == "numeric":
				axisHeaders.append( self.dataHandler.metaData[i][0] )
		
		dialogPop.GraphDialog( self, self.dataHandler, "Histogram", axisHeaders )
		
		return

	def handleCmd2(self):
		print 'handling command 2'
		
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			if self.dataHandler.metaData[i][1] == "numeric":
				axisHeaders.append( self.dataHandler.metaData[i][0] )
		
		dialogPop.GraphDialog( self, self.dataHandler, "Scatterplot", axisHeaders )


	def handleCmd3(self):
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			if self.dataHandler.metaData[i][1] == "numeric":
				axisHeaders.append( self.dataHandler.metaData[i][0] )
				
		dialogPop.StatsBox( self, self.dataHandler, "Mean", axisHeaders )
		
		
	def handleCmd4(self):
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			if self.dataHandler.metaData[i][1] == "numeric":
				axisHeaders.append( self.dataHandler.metaData[i][0] )

		dialogPop.StatsBox( self, self.dataHandler, "Median", axisHeaders )


	def handleCmd5(self):
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			if self.dataHandler.metaData[i][1] == "numeric":
				axisHeaders.append( self.dataHandler.metaData[i][0] )

		dialogPop.StatsBox( self, self.dataHandler, "Mode", axisHeaders )
	
	
	def handleCmd6(self):
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			if self.dataHandler.metaData[i][1] == "numeric":
				axisHeaders.append( self.dataHandler.metaData[i][0] )

		dialogPop.StatsBox( self, self.dataHandler, "All", axisHeaders )
		
		
	def handleCmd7(self):
		self.boxPlot()
		
		
	def handleCmd8(self):
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			if self.dataHandler.metaData[i][1] == "numeric":
				axisHeaders.append( self.dataHandler.metaData[i][0] )

		dialogPop.StatsBox( self, self.dataHandler, "Range", axisHeaders )
		
		
	def handleCmd9( self ):
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			if self.dataHandler.metaData[i][1] == "numeric":
				axisHeaders.append( self.dataHandler.metaData[i][0] )

		dialogPop.StatsBox( self, self.dataHandler, "Standard Deviation", axisHeaders )
		
	
	def handleCmdPCA( self ):
		"""TO-DO"""
		axisHeaders = []
		for i in range( len( self.vectorHandler.metaData ) ):
			if self.vectorHandler.metaData[i][1] == "numeric":
				axisHeaders.append( self.vectorHandler.metaData[i][0] )
		
		dialogPop.GraphDialog( self, self.vectorHandler, "PCA", axisHeaders  )
		
		
	def handleCmdClusters( self ):
		"""TO-DO"""
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			if self.dataHandler.metaData[i][1] == "numeric":
				axisHeaders.append( self.dataHandler.metaData[i][0] )
				
		dialogPop.GraphDialog( self, self.dataHandler, "Clusters", axisHeaders  )
		
		

##### Miscellaneous Handlers ############################################################		
	
	def handleView( self ):
		"""Handle the menu option for preparing the data view."""
		dialogPop.DataViewDialog(self.desiredFile, self.beautifulPrint() )
		return
		
	
	def handleReplotScatter( self ):
		
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			if self.dataHandler.metaData[i][1] == "numeric":
				axisHeaders.append( self.dataHandler.metaData[i][0] )
		
		dialogPop.GraphDialog( self, self.dataHandler, "Scatterplot", axisHeaders )
	
	
	def handleSpecial1(self):
		dialogPop.GraphDialog( self, self.dataHandler, "Special1", [] )
	
	def handleSpecial2(self):
		"""Creates a boxplot of arrival times by each region"""
		dataNames = ['One',' Five', 'Seven', 'Eight', 'Nine', 'Ten', 'Twelve',
					  'Thirteen', 'Fourteen', 'Fifteen' ]
		dOne = []
		dFive = []
		dSeven = []
		dEight = []
		dNine = []
		dTen = []
		dTwelve = []
		dThirteen = []
		dFourteen = []
		dFifteen = []
		
		# Creates seperate data sets for each region
		dCount = len(self.dataHandler.rawData)
		for i in range(2, dCount):
			if self.dataHandler.rawData[i][2].lstrip() == 'One':
				dOne.append( float( self.dataHandler.rawData[i][4] ) )
			elif self.dataHandler.rawData[i][2].lstrip() == 'Five':
				dFive.append( float( self.dataHandler.rawData[i][4] ) )
			elif self.dataHandler.rawData[i][2].lstrip() == 'Seven':
				dSeven.append( float( self.dataHandler.rawData[i][4] ) )
			elif self.dataHandler.rawData[i][2].lstrip() == 'Eight':
				dEight.append( float( self.dataHandler.rawData[i][4] ) )
			elif self.dataHandler.rawData[i][2].lstrip() == 'Nine':
				dNine.append( float( self.dataHandler.rawData[i][4] ) )		
			elif self.dataHandler.rawData[i][2].lstrip() == 'Ten':
				dTen.append( float( self.dataHandler.rawData[i][4] ) )		
			elif self.dataHandler.rawData[i][2].lstrip() == 'Twelve':
				dTwelve.append( float( self.dataHandler.rawData[i][4] ) )		
			elif self.dataHandler.rawData[i][2].lstrip() == 'Thirteen':
				dThirteen.append( float( self.dataHandler.rawData[i][4] ) )		
			elif self.dataHandler.rawData[i][2].lstrip() == 'Fourteen':
				dFourteen.append( float( self.dataHandler.rawData[i][4] ) )		
			else:
				dFifteen.append( float( self.dataHandler.rawData[i][4] ) )		

		#Turns each regional data sets into numpy matrices
		dOne = np.matrix(dOne)
		dFive = np.matrix(dFive)
		dSeven = np.matrix(dSeven)
		dEight = np.matrix(dEight)
		dNine = np.matrix(dNine)
		dTen = np.matrix(dTen)
		dTwelve = np.matrix(dTwelve)
		dThirteen = np.matrix(dThirteen)
		dFourteen = np.matrix(dFourteen)
		dFifteen = np.matrix(dFifteen)
		
		data = [dOne, dFive,  dSeven, dEight, dNine, dTen, dTwelve, dThirteen,
			   dFourteen, dFifteen]
		
		#Set up graph preferences
		fig = plt.figure(figsize=(15,10))
		fig.canvas.set_window_title('Comparison of Arrival Dates by Region')
		ax1 = fig.add_subplot(111)
		plt.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)
		
		bp = plt.boxplot(data, notch=0, sym='+', vert=1, whis=1.5)
		plt.setp(bp['boxes'], color='black')
		plt.setp(bp['whiskers'], color='black')
		plt.setp(bp['fliers'], color='red', marker='+')
		
		ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
					  alpha=0.5)
		
		ax1.set_axisbelow(True)
		ax1.set_title('Comparison of Arrival Dates by Region', fontsize=15)
		ax1.set_xlabel('Region', fontsize=18)
		ax1.set_ylabel('Value', fontsize=18)
		
		# Create the box displays. Alternate color in order for easier viewing.
		boxColors = ['green','blue']
		numBoxes = 10
		medians = range(numBoxes)
		for i in range(numBoxes):
			box = bp['boxes'][i]
			boxX = []
			boxY = []
			for j in range(5):
				boxX.append(box.get_xdata()[j])
				boxY.append(box.get_ydata()[j])
			boxCoords = zip(boxX,boxY)
			
			k = i % 2
			boxPolygon = Polygon(boxCoords, facecolor=boxColors[k])
			ax1.add_patch(boxPolygon)
			med = bp['medians'][i]
			medianX = []
			medianY = []
			for j in range(2):
				medianX.append(med.get_xdata()[j])
				medianY.append(med.get_ydata()[j])
				plt.plot(medianX, medianY, 'k')
				medians[i] = medianY[0]

			plt.plot([np.average(med.get_xdata())], [np.average(data[i])], color='w', marker='*', markeredgecolor='k')
		
		# Set the axes ranges and axes labels
		ax1.set_xlim(0.5, numBoxes+0.5)
		top = 350
		bottom = 0
		ax1.set_ylim(bottom, top)
		xtickNames = plt.setp(ax1, xticklabels=dataNames)
		plt.setp(xtickNames, rotation=45, fontsize=13)
	
		# Basic legend
		plt.figtext(0.80, 0.08, 'Legend', color='black', style='normal',
				   size='larger')
		plt.figtext(0.80, 0.04, '*', color='black', weight='roman', size='medium')
		plt.figtext(0.815, 0.04, ' Average Value', color='black', weight='roman',
				   size='medium')
		
		plt.show()
	
	
	def handleOpenNew( self ):
		fobj = tkFileDialog.askopenfile( parent=self.root, mode='rb', title='Choose a data file...' )
		if ( fobj == None ):
			return
		self.desiredFile = os.path.basename(fobj.name)
		
		self.root.destroy()
		
		self.pcaChoice.destroy()
		self.isPCA = True
		self.dataHandler = ds.DataSet( self, filename=fobj.name )
		pcaData = self.dataHandler.buildPCA( self.dataHandler.numbData )
		self.vectorHandler = ds.DataSet( self, passData=pcaData )
		self.initializeGUI( self.width, self.height )
		
		
	def handleFilter( self ):
		"""Handle the command for the filter menu item and begin
		   the filtering process."""
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			if self.dataHandler.metaData[i][1] != "date":
				axisHeaders.append( self.dataHandler.metaData[i][0] )
		
		dialogPop.GraphDialog( self, self.dataHandler, "Filter", axisHeaders )
		
		
	def handleAbout( self ):
		"""Handles the About scenario"""
		dialogPop.WelcomeDialog()
		return	
		
		
		


##### Axes Construction #################################################################		
	
	def buildAxes( self ):
		"""Initialize the visual axes."""
		vtm = self.vr.build()
		screenpoints = ( vtm * self.axes.transpose() ).transpose()
		# X-Axis
		xAxisPoints = ( screenpoints[0,0], screenpoints[0,1], screenpoints[1,0], screenpoints[1,1] )
		xAxis = self.canvas.create_line( xAxisPoints, fill='red')
		# Y-Axis
		yAxisPoints = ( screenpoints[2,0], screenpoints[2,1], screenpoints[3,0], screenpoints[3,1] )
		yAxis = self.canvas.create_line( yAxisPoints, fill='green')
		# Z-Axis
		zAxisPoints = ( screenpoints[4,0], screenpoints[4,1], screenpoints[5,0], screenpoints[5,1] )
		zAxis = self.canvas.create_line( zAxisPoints, fill='blue')
		# Add them to the GFX list
		self.axesGFX = [ xAxis, yAxis, zAxis ]
		
		
		
		
##### Plotting ##########################################################################
	
	def plotScatter( self ):
		"""Plots chosen points to the ViewRef display canvas with required
		   options."""
		   
		if self.colorUse.get() == "Last Column":
			self.colorUse.set( self.dataHandler.metaData[-1][0] )
		
		# Configure point color if necessary.
		if self.colorUse.get() != "No":
			self.buildAxisColor( self.colorUse.get() )
		else:
			self.currentColor = "#ff0000"
		
		# Configure point size if necessary.
		if self.sizeUse.get() != "No":
			self.buildAxisSize( self.sizeUse.get() )
		else:
			self.currentSize = 1
			self.sizeList = []
		
		# Add columns of 1's to the data to satisfy the ViewRef requirements.
		underFour = 4 - len( self.axesToPlot )
		onesColumn = np.ones( (len(self.plotMatrix), 1) )
		while ( underFour != 0 ):
			self.plotMatrix = np.hstack( (self.plotMatrix, onesColumn) )
			underFour = underFour - 1
		
		# Build the display output and configure the points individually.
		transform = self.vr.build()
		screenpoints = ( transform * self.plotMatrix.transpose() ).transpose()
		for i in range( len( screenpoints )):
			x = screenpoints[i, 0]
			y = screenpoints[i, 1]
			
			# Configure the point's color.
			if( self.colorUse.get() != "No" and self.colorUse.get() != "Clusters" ):
				self.currentColor = self.setPointColor( self.colorUse.get(), i )
			elif( self.colorUse.get() == "Clusters" ):
				self.currentColor = self.setClusterColor( i )
			else:
				self.currentColor = self.currentColor
			
			# Configure the point's size.	
			if( self.sizeUse.get() != "No" ):
				self.currentSize = float( self.setPointSize( self.sizeUse.get(), i ) )
			else:
				self.currentSize = self.currentSize
			
			# Create the size to save to the list of sizes.
			sSize = self.currentSize * self.shapeSize
			self.sizeList.append( sSize )
			
			
			# Configure the point's shape.
			if ( self.var.get() == "Square" ):		  
				shapeBBox = ( x-sSize, y-sSize, x+sSize, y+sSize )
				newShape = self.canvas.create_rectangle( shapeBBox, fill=self.currentColor)
				self.shapes.append( newShape )
			elif ( self.var.get() == "Oval" ):
				shapeBBox = ( x-sSize, y-sSize, x+sSize, y+sSize )
				newShape = self.canvas.create_oval( shapeBBox, fill=self.currentColor)
				self.shapes.append( newShape )
			elif ( self.var.get() == "Line" ):
				shapeBBox = ( x-sSize, y-sSize, x+sSize, y+sSize )
				newShape = self.canvas.create_line( shapeBBox, fill=self.currentColor, width=3 )
				self.shapes.append( newShape )
				
		# Set up the legend
		self.legendBuild()
				
	
	def boxPlot( self ):
		# Create some random data for the boxplot.
		pylab.figure( 3 )
		b = pylab.boxplot( self.dataHandler.numbData )

		# Change the box lines to red, with linewidth 2.
		boxlines = b['boxes']
		for line in boxlines:
			line.set_color('r')
			line.set_linewidth(2)

		# Change the median lines to green, with linewidth 2.
		medlines = b['medians']
		for line in medlines:
			line.set_color('g')
			line.set_linewidth(2)
			
		pylab.title("Box Plot of the Data")
		pylab.xlabel( "Axes" )
		
		pylab.show()
		return
		
	
	def legendBuild( self ):
		"""Constructs a visual legend for the scatterplot based on the options
		   chosen during the configuration."""
		self.canvas.create_text(600,50, text='Legend', fill='black', font=('verdana', 14, 'underline'))
		if self.xAxisHeader != None:
			self.canvas.create_text(600,75, text='x-axis = ' + self.xAxisHeader, fill='red', font=('verdana', 12))
			
		if self.yAxisHeader != None:
			self.canvas.create_text(600,100, text='y-axis = ' + self.yAxisHeader, fill='green', font=('verdana', 12))
			
		if self.zAxisHeader != None:
			self.canvas.create_text(600,125, text='z-axis = ' + self.zAxisHeader, fill='blue', font=('verdana', 12))
			
		if self.colorHeader != None and self.zAxisHeader != None:
			self.canvas.create_text(600,150, text='color = ' + self.colorHeader, fill='black', font=('verdana', 12))
		elif self.colorHeader != None and self.zAxisHeader == None:
			self.canvas.create_text(600,125, text='color = ' + self.colorHeader, fill='black', font=('verdana', 12))
			
		if self.sizeHeader != None and self.colorHeader != None and self.zAxisHeader != None:
			self.canvas.create_text(600,175, text='size = ' + self.sizeHeader, fill='black', font=('verdana', 12))
		elif self.sizeHeader != None and self.colorHeader == None and self.zAxisHeader != None:
			self.canvas.create_text(600,150, text='size = ' + self.sizeHeader, fill='black', font=('verdana', 12))
		elif self.sizeHeader != None and self.colorHeader == None and self.zAxisHeader == None:
			self.canvas.create_text(600,125, text='size = ' + self.sizeHeader, fill='black', font=('verdana', 12))
		elif self.sizeHeader != None and self.colorHeader != None and self.zAxisHeader == None:
			self.canvas.create_text(600,150, text='size = ' + self.sizeHeader, fill='black', font=('verdana', 12))
		
		
##### Updating Functions ################################################################
		
	def updateAxes( self ):
		"""Update all the axes in the plot to fit the transformed space."""
		vtm = self.vr.build()	 
		screenpoints = ( vtm * self.axes.transpose() ).transpose()
		for i in range( len( self.axesGFX ) ):
			x = i*2
			y = x+1
			self.canvas.coords( self.axesGFX[i], screenpoints[x,0], screenpoints[x,1], screenpoints[y,0], screenpoints[y,1] )


	def updatePlot( self ):
		"""Update all the shapes in the plot to fit the transformed space."""
		if self.plotMatrix == None:
			return
		transform = self.vr.build()
		screenpoints = ( transform * self.plotMatrix.transpose() ).transpose()
		for i in range( len( screenpoints )):
			sSize = self.sizeList[i]
			x = screenpoints[i, 0]
			y = screenpoints[i, 1]
			self.canvas.coords( self.shapes[i], x-sSize, y-sSize, x+sSize, y+sSize )



##### Printing ##########################################################################
	
	def beautifulPrint( self ):
		"""Returns the complete contents of the data set in a well-spaced, readable
		   layout by column."""
		printArray = []
		headArray = []
		for i in range( len( self.dataHandler.metaData ) ):
			tempHeadString = "" + self.dataHandler.metaData[i][0] + " (" + self.dataHandler.metaData[i][1] + ")"
			headArray.append( tempHeadString )
		printArray.append( headArray )
		
		for j in range( 2, len( self.dataHandler.rawData ) ):
			printRow = []
			for i in range( len(self.dataHandler.rawData[1]) ):
				printRow.append( self.dataHandler.rawData[j][i].lstrip() )
			printArray.append( printRow )

		widestCols = []
		numCols = len(printArray[0] )
		for x in range( numCols ):
			tempWide = 0
			for y in range( len( printArray ) ):
				if ( len( str(printArray[y][x]) ) > tempWide):
					tempWide = len( printArray[y][x] )
			widestCols.append( tempWide )
		for i in range( len(widestCols) ):
			widestCols[i] = int(widestCols[i]/8)+1
		output = "\n"
		headString = ""
		for col in range( len(printArray[0]) ):
			strAdd = str( printArray[0][col] )
			numTabs = widestCols[col] - int(len(strAdd)/8)
			strAdd = strAdd+(numTabs*"\t")
			headString += strAdd
		output += headString + 2*("\n")
		
		for row in range( 1, len(printArray) ):
			lineString = ""
			for col in range( len(printArray[0]) ):
				strAdd = str( printArray[row][col] )
				numTabs = widestCols[col] - int(len(strAdd)/8)
				strAdd = strAdd+(numTabs*"\t")
				lineString += strAdd
			output += lineString + ("\n")
		return output+"\n"
	
	
	
	
##### Color Functionality ###############################################################

	def setPointColor( self, axisName, point ):
		"""Sets the color of a given point by using the pre-generated color
		   weighting."""
		if ( self.dataHandler.filteredData != None ):
			axis = self.dataHandler.getFilteredAxis( axisName )
		else:	
			axis = self.dataHandler.getNumericAxis( axisName )
		pointvalue = float( axis[point] )
		pointvalue = float((pointvalue-self.colorMin)/self.colorRange)

		green = int(pointvalue*255)
		blue = int((1-pointvalue)*255)
		
		redString = "00"
		blueString = str(hex(blue)[2:])
		if len(blueString) == 1 :
			blueString = "0"+blueString
		greenString = str(hex(green)[2:])
		if len(greenString) == 1 :
			greenString = "0"+greenString
		
		hexValue = "#"+redString + greenString + blueString

		return hexValue
		
		
	def buildAxisColor( self, axisName ):
		"""Generates the color weighting values for use in plotting an axis
		   as the point color."""
		if ( self.dataHandler.filteredData != None ):
			axis = self.dataHandler.getFilteredAxis( axisName )
		else:	
			axis = self.dataHandler.getNumericAxis( axisName )
		minimum = None
		for val in axis:
			if minimum == None:
				minimum = val
			elif val < minimum:
				minimum = val
		rangeFloat = axis.max(0) - axis.min(0)

		self.colorRange = rangeFloat
		self.colorMin = minimum
		
		
	def setClusterColor( self, point ):
		
		colorList = ["red", "blue", "green", "yellow", "cyan", "magenta", 
				 "orange", "turquoise", "maroon", "coral", "tan", "salmon",
				 "gold", "purple", "brown" ]
		
		labelNum = self.labels[ point ]
		
		color = colorList[ labelNum ]
		
		return color




##### Size Functionality ################################################################
	
	def setPointSize( self, axisName, point ):
		"""Sets the size of a given point by using the pre-generated size
		   weighting."""
		if ( self.dataHandler.filteredData != None ):
			axis = self.dataHandler.getFilteredAxis( axisName )
		else:	
			axis = self.dataHandler.getNumericAxis( axisName )
		pointvalue = float( axis[point] )	
		pointvalue = float(pointvalue/self.sizeMean)
		return pointvalue
		
		
	def buildAxisSize( self, axisName ):
		"""Generates the size weighting values for use in plotting an axis
		   as the point size."""
		if ( self.dataHandler.filteredData != None ):
			axis = self.dataHandler.getFilteredAxis( axisName )
		else:	
			axis = self.dataHandler.getNumericAxis( axisName )
		minimum = None
		for val in axis:
			if minimum == None:
				minimum = val
			elif val < minimum:
				minimum = val
		meanFloat = float( self.mean( axis ) )
		self.sizeMean = meanFloat
		self.sizeMin = minimum
		
		
		
		
##### Basic Math Functions ##############################################################
	
	def mean( self, var ):
		"""Returns the mean for a column of numerical data."""
		over = 0
		for i in range( len( var ) ):
			over += var[i][0]
		under = len( var )
		return (over/under)[0,0]
	
	
	def median( self, var ):
		"""Returns the median for a column of numerical data."""
		var = sorted(var)
		if len(var) % 2 == 1:
			return var[(len(var)+1)/2-1][0]
		else:
			lower = var[len(var)/2-1][0]
			upper = var[len(var)/2][0]
		return ( float(lower + upper) ) / 2
	
	
	def mode( self, var ):
		"""Returns the mode for a column of numerical data."""
		modeL = []
		num = 0
		temp = None

		#sort the list
		var.sort()
		
		#for the values in a list
		for i in range(len(var)):
			count = 1
			value = var[i,0]
		
			#for all the values after the current index
			for j in range(i+1,len(var)):
				if var[j,0] == value:
					count += 1
					temp = var[i+1,0]
				else:
					break
			if count > num and count > 1:
				modeL = []
				num = count
				modeL.append(temp)
			elif count == num and count > 1:
				modeL.append(temp)
				i += count
		
		if len( modeL ) == 0:
			return "All Values Only Occur Once"
		else:
			return str(modeL[:])


	def range( self, var ):
		"""Returns the range for a column of numerical data."""
		var = sorted( var )
		return (var[-1][0] - var[0][0])[0,0]
		
		
	def stdDev( self, var ):
		"""Returns the standard deviation for a column of numerical data."""
		return np.std(var)

		
		
					
##### Export Functions ##################################################################

	def handleExportARFF( self ):
	
		self.saveChoice = "Normal"
		
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			axisHeaders.append( self.dataHandler.metaData[i][0] )
			
		dialogPop.FileExportDialog( self, self.dataHandler, axisHeaders )
		
	
	def handleExportARFFPCA( self ):
		
		self.saveChoice = "PCA"
		
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			axisHeaders.append( self.dataHandler.metaData[i][0] )
			
		dialogPop.FileExportDialog( self, self.dataHandler, axisHeaders )
	
	
	def handleSaveCSV( self ):
		
		self.saveChoice = "Normal"
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			axisHeaders.append( self.dataHandler.metaData[i][0] )
		
		dialogPop.FileSaveDialog( self, self.dataHandler, axisHeaders )
		
	
	def handleSavePCA( self ):
		
		self.saveChoice = "PCA"
		axisHeaders = []
		for i in range( len( self.vectorHandler.metaData ) ):
			axisHeaders.append( self.vectorHandler.metaData[i][0] )
		
		dialogPop.FileSaveDialog( self, self.vectorHandler, axisHeaders )
		
		
	def writeCSVFile( self ):
		# Write the 
		
		if self.saveChoice == "Normal":
			dataSet = self.dataHandler
		elif self.saveChoice == "PCA":
			dataSet = self.vectorHandler
		
		axisHeaders = []
		for i in range( len( self.dataHandler.metaData ) ):
			axisHeaders.append( self.dataHandler.metaData[i][0] )
		
		writeMatrix = None
		if ( self.numSaveCols.get() == 'All' ):
			writeMatrix = dataSet.rawData
		else:
			for choice in self.saveChoiceList:
				choice = choice.get()
				tempCol = dataSet.getAxis( choice )
				if writeMatrix == None:
					writeMatrix = tempCol
				else:
					writeMatrix = np.hstack( ( writeMatrix, tempCol ) )
			writeMatrix = (np.array(writeMatrix)).tolist()
			
		newFile = open( self.saveFileName.get()+'.csv', 'wb' )
		writer = csv.writer( newFile )
		for line in writeMatrix:
			print line
			writer.writerow( line )
		newFile.close()
	
		
	def writeARFFFile( self ):
		"""TO-DO"""
		fileString = "%\n% Created with V.I.O.L.A.S.++\n%\n\n"
		fileString += "@relation "+self.fileNameShort+"\n\n"
		
		if self.saveChoice == "Normal":
			toUse = self.dataHandler.metaData
		elif self.saveChoice == "PCA":
			toUse = self.vectorHandler.metaData
		
		
		for i in range( self.numVarVecs ):
			fileString += "@attribute "+toUse[i][0]+"\t"+toUse[i][1]+"\n"
			
		if self.saveChoice == "PCA":
			fileString += "@attribute label\tnumeric\n"
		
		fileString += "\n@data\n"
		
		if self.saveChoice == "PCA":
			tempMatrix = np.copy( self.vectorHandler.numbData )
			tempMatrix = tempMatrix[ :self.numVarVecs ]
			labelRow = self.pcaLabelList.T
			print tempMatrix.shape
			print labelRow.shape
			tempMatrix = np.hstack( ( tempMatrix, labelRow ) )
		else:
			tempMatrix = np.copy( self.dataHandler.numbData )
		
		writeList = (np.array(tempMatrix)).tolist()
		for row in writeList:
			writeRow = ""
			for element in row:
				writeRow += str(element)+","
			fileString += writeRow[:-1]+"\n"
		
		newFile = open( self.saveFileName.get()+'.arff', 'wb' )
		newFile.write( fileString )
		newFile.close()




##### Main ##############################################################################

	def main( self ):
		"""Executes the main program and begins V.I.O.L.A.S"""
		self.root.mainloop()
		


		
if __name__ == "__main__":
	dapp = VIOLAS(800, 800)
	dapp.main()