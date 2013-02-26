# Nicholas Balsbaugh & Alex Swanson
# CS251 - Data Analysis and Visualization
# Project 6 - Visualization II
# Professor Bruce Maxwell
# April 9th, 2011


# Imports
from Tkinter import Entry, Label, Button, Tk, OptionMenu, StringVar, IntVar
import pylab
import Tkinter as tk
from ViewRef import ViewRef
import matplotlib.pyplot as plt


class GraphDialog:
	
##### Initialization ####################################################################

	def __init__( self, main, dataInstance, plotType, axes ):
		self.root = Tk() 
		self.dataInstance = dataInstance
		self.axes = axes
		self.bins = 0
		self.main = main
		self.dataInstance.filteredData = None
		self.plotType = plotType
		
		if plotType == "Histogram":
			self.dataInstance.axesToPlot = [ None ]
			
			# Set up the dropdown menu
			self.root.title('Choose Preferences For Histogram')
			self.root.geometry('350x150-80+80')
			self.filterHeader = None
			
			self.histoAxis = StringVar( self.root )
			self.histoAxis.set( axes[0] ) # initial value
			
			Label(self.root, text="Variable").grid( row=0, column=0, sticky=tk.W )
			Label(self.root, text="Bins").grid( row=1, column=0, sticky=tk.W )
			Label(self.root, text="Variable to Filter").grid( row=2, column=0, sticky=tk.W )
			Label(self.root, text="Number of Filters").grid( row=3, column=0, sticky=tk.W )
			
			self.tempVar = ()
			for i in range( len( self.axes ) ):
				self.tempVar = self.tempVar + (self.axes[i], )
			w = apply( OptionMenu, (self.root, self.histoAxis) + self.tempVar )
			w.grid(row=0, column=1, sticky=tk.E)
			
			binList = []
			for i in range( 25 ):
				binList.append( i+1 )
			binList = tuple( binList )
			self.bins = IntVar( self.root )
			self.bins.set( 10 )
			k = apply( OptionMenu, (self.root, self.bins) + binList )
			k.grid(row=1, column=1, sticky=tk.E)
			
			headersTuple = ()
			for i in range( len( self.dataInstance.metaData ) ):
				headersTuple = headersTuple + (self.dataInstance.metaData[i][0], )
			self.histoFilterHead = StringVar( self.root )
			headerDrop = apply( OptionMenu, (self.root, self.histoFilterHead ) + headersTuple )
			headerDrop.grid(row=2, column=1, sticky=tk.E)
			
			self.filterNum = StringVar( self.root )
			self.filterNum.set( "None" )
			filterTuple = ( "None", "One", "Two", "Three", "Four", "Five" )
			filterDrop = apply( OptionMenu, ( self.root, self.filterNum ) + filterTuple )
			filterDrop.grid( row=3, column=1, sticky=tk.E )
			
			def callback():
				self.root.destroy()
				if ( self.filterNum.get() != "None" ):
					self.main.histoAxis = self.histoAxis
					self.main.histoFilterHead = self.histoFilterHead
					self.histoFilter()
				else:
					self.histoCase()

			b = Button( self.root, text="Continue", command=callback )
			b.grid( row=5, columnspan=2, sticky=tk.E )
			
		elif plotType == "Scatterplot":
			# Set up the dropdown menu 
			self.root.title('Choose Number of Axes For Scatterplot')
			self.root.geometry('325x80-80+80')
			self.axisNum = IntVar( self.root )
			self.axisNum.set( 2 ) # initial value
			
			axisCountList = []
			for i in range( len( axes ) ):
				if i != 0 and i < 3:
					axisCountList.append( i+1 )
			axisCountList = tuple( axisCountList )
			
			Label(self.root, text="Number of Axes").grid(row=0)	   
			w = apply( OptionMenu, (self.root, self.axisNum) + axisCountList )
			w.grid( row=0, column=1, sticky=tk.E )
			
			b = Button( self.root, text="Confirm Number of Axes", command=self.scatterCase )
			b.grid( row=1, columnspan=2 )

		elif plotType == "Special1":
			self.root.destroy()
			self.special1Case()
			
			
		elif plotType == "PCA":
			self.root.title('Choose Options for PCA Plot')
			self.root.geometry('325x80-80+80')
			self.axisNum = IntVar( self.root )
			self.axisNum.set( 2 ) # initial value
			
			axisCountList = []
			for i in range( len( axes ) ):
				if i != 0 and i < 3:
					axisCountList.append( i+1 )
			axisCountList = tuple( axisCountList )
			
			Label(self.root, text="Number of Dimesions").grid(row=0)	   
			w = apply( OptionMenu, (self.root, self.axisNum) + axisCountList )
			w.grid( row=0, column=1, sticky=tk.E )
			
			b = Button( self.root, text="Confirm PCA Options", command=self.pcaCase )
			b.grid( row=1, columnspan=2 )




##### ScatterPlot-Related Functions #######################################################
	
	def scatterCase( self ):
		"""Controls the window used to choose options for a new scatterplot."""
		self.root.destroy()
		self.main.shapes = []
		self.main.canvas.delete( tk.ALL )
		self.main.vr = ViewRef()
		self.main.buildAxes()
		
		self.scatterWin = Tk()
		self.scatterWin.title('Choose Axes For Scatterplot')
		
		self.main.axesToPlot = [None]*self.axisNum.get()
		self.axisChoice = StringVar( self.scatterWin )
		
		winHeight = 150+(self.axisNum.get()*20)
		sizeString = "300x"+str( winHeight )+"-80+80"
		
		axisNames = []
		for i in range( self.axisNum.get() ):
			if i == 0:
				axisNames.append("X Axis")
			elif i == 1:
				axisNames.append("Y Axis")
			elif i == 2:
				axisNames.append("Z Axis")
			else:
				axisNames.append("Color")
		
		self.scatterWin.geometry( sizeString )
		
		self.axesTuple = ()
		for i in range( len( self.axes ) ):
			self.axesTuple = self.axesTuple + ( self.axes[i], )
		
		self.axisChoice.set( self.axesTuple[0] )
				
		for i in range( self.axisNum.get() ):
			self.main.axesToPlot[i] = StringVar( self.scatterWin )
			self.main.axesToPlot[i].set( self.axesTuple[i] ) # initial value
			Label(self.scatterWin, text=axisNames[i]).grid(row=i)
			w = apply( OptionMenu, (self.scatterWin, self.main.axesToPlot[i]) + self.axesTuple )
			w.grid( row=i, column=1 )
			
		for i in range( len( self.main.axesToPlot ) ):
			if i == 0:
				self.main.xAxisHeader = self.main.axesToPlot[i].get()
			if i == 1:
				self.main.yAxisHeader = self.main.axesToPlot[i].get()
			if i == 2:
				self.main.zAxisHeader = self.main.axesToPlot[i].get()
			
		self.main.colorUse = StringVar( self.scatterWin )
		self.main.colorUse.set( "No" )
		colorList = []
		for item in self.axes:
			colorList.append( item )
		colorTuple = tuple( [ "No" ] + colorList + [ "Clusters" ] )
		Label(self.scatterWin, text="Use an axis as a color?").grid( row=self.axisNum.get(), column=0)
		colorDrop = apply( OptionMenu, (self.scatterWin, self.main.colorUse) + colorTuple )
		colorDrop.grid( row=self.axisNum.get(), column=1 )
		
		self.main.sizeUse = StringVar( self.scatterWin )
		self.main.sizeUse.set( "No" )
		sizeList = []
		for item in self.axes:
			sizeList.append( item )
		sizeTuple = tuple( [ "No" ] + sizeList )
		Label(self.scatterWin, text="Use an axis as a size?").grid( row=self.axisNum.get()+1, column=0)
		sizeDrop = apply( OptionMenu, (self.scatterWin, self.main.sizeUse) + sizeTuple )
		sizeDrop.grid( row=self.axisNum.get()+1, column=1 )
		
		self.main.filterUse = StringVar( self.scatterWin )
		self.main.filterUse.set( "None" )
		filterTuple = ( "None", "One", "Two" )
		Label( self.scatterWin, text="Number of Filters").grid( row=self.axisNum.get()+2, column=0)
		filterDrop = apply( OptionMenu, (self.scatterWin, self.main.filterUse) + filterTuple )
		filterDrop.grid( row=self.axisNum.get()+2, column=1 )
		
		def callback():
			self.scatterWin.destroy()
			if ( self.main.filterUse.get() != "None" ):
				self.filterCase()
			elif ( self.main.colorUse.get() == "Clusters" and self.main.filterUse.get() == "None" ):
				self.clusterCase()
			else:
				self.scatterBuild()
				
		b = Button( self.scatterWin, text="Continue", command=callback )
		b.grid( row=self.axisNum.get()+3, columnspan=2 )


	def scatterBuild( self ):
		"""Manages the configuration of the scatter data, the axes options and the
		   legend creation process."""
		self.resetLegendHeaders()
		
		# Configure the data for the scatterplot.
		self.dataInstance.prepareScatterData()
		
		# Configure the strings for the legend labels.
		for i in range( len( self.main.axesToPlot ) ):
			if i == 0:
				self.main.xAxisHeader = self.main.axesToPlot[i].get()
			if i == 1:
				self.main.yAxisHeader = self.main.axesToPlot[i].get()
			if i == 2:
				self.main.zAxisHeader = self.main.axesToPlot[i].get()
		if self.main.colorUse.get() != "No":
			self.main.colorHeader = self.main.colorUse.get()
		if self.main.sizeUse.get() != "No":
			self.main.sizeHeader = self.main.sizeUse.get()
		
		print "Building Scatterplot"
		self.main.plotScatter()




##### Histogram-Related Functions #######################################################

	def histoCase( self ):
		print "Building Histogram"
		
		header = self.histoAxis.get()
		
		if ( self.filterNum.get() == "None" ):
			data = self.dataInstance.getNumericAxis( self.histoAxis.get() )
		else:
			labels = []
			data = []
			for set in self.main.histoCols:
				labels.append( set[0] )
				data.append( set[1] )
		
		pylab.ion()
		if ( self.filterNum.get() == "None" ):
			pylab.hist( data, bins=self.bins.get(), label=header )
		else:
			pylab.hist( data, bins=self.bins.get(), label=labels )

		pylab.legend()
		pylab.xlabel( header )
		pylab.ylabel("Frequency")
		pylab.title("Histogram" )

		pylab.show()

	
	def histoFilter( self ):
		self.root = Tk()
		self.root.title('Choose Histogram Filters for '+self.main.histoFilterHead.get() )
		
		filterCount = 0
		if self.filterNum.get() == "One":
			filterCount = 1
		elif self.filterNum.get() == "Two":
			filterCount = 2
		elif self.filterNum.get() == "Three":
			filterCount = 3
		elif self.filterNum.get() == "Four":
			filterCount = 4
		elif self.filterNum.get() == "Five":
			filterCount = 5
			
		winHeight = str(25+(40*filterCount))
		self.root.geometry('400x'+winHeight+'-80+80')
		
		self.main.histoFilterList = []
		
		for i in range( filterCount ):
			
			tempFilter = StringVar( self.root )
			
			labelText = "Filter "+str(i+1)
			Label( self.root, text=labelText ).grid(row=i, column=0, sticky=tk.W)
			
			filterText = Entry( self.root, textvariable=tempFilter )
			filterText.grid( row=i, column=1)
			
			self.main.histoFilterList.append( tempFilter )
			
		def callback():
			self.root.destroy()
			self.dataInstance.prepareHistoData()
			self.histoCase()
			
			
		b = Button( self.root, text="Continue", command=callback )
		b.grid( row=filterCount, columnspan=2 )
		
		
		
		
##### PCA-related Functions ############################################################

	def pcaCase( self ):
		"""Controls the window used to choose options for a new PCA and clustering
		   visualization."""
		self.root.destroy()
		self.main.shapes = []
		self.main.canvas.delete( tk.ALL )
		self.main.vr = ViewRef()
		self.main.buildAxes()
		
		self.scatterWin = Tk()
		self.scatterWin.title('Choose Eigenvectors For Visualization')
		
		self.main.filterUse = StringVar( self.scatterWin )
		self.main.filterUse.set( "None" )
		self.main.colorUse = StringVar( self.scatterWin )
		self.main.colorUse.set( "No" )
		self.main.sizeUse = StringVar( self.scatterWin )
		self.main.sizeUse.set( "No" )
		self.main.clusterChoice = StringVar( self.scatterWin )
		self.main.clusterChoice.set( "Normal" )
		
		self.main.axesToPlot = [None]*self.axisNum.get()
		self.axisChoice = StringVar( self.scatterWin )
		
		winHeight = 200+(self.axisNum.get()*20)
		sizeString = "300x"+str( winHeight )+"-80+80"
		
		axisNames = []
		for i in range( self.axisNum.get() ):
			if i == 0:
				axisNames.append("X Axis")
			elif i == 1:
				axisNames.append("Y Axis")
			elif i == 2:
				axisNames.append("Z Axis")
		
		self.scatterWin.geometry( sizeString )
		
		self.axesTuple = ()
		for i in range( len( self.axes ) ):
			self.axesTuple = self.axesTuple + ( self.axes[i], )
		
		self.axisChoice.set( self.axesTuple[0] )
				
		for i in range( self.axisNum.get() ):
			self.main.axesToPlot[i] = StringVar( self.scatterWin )
			self.main.axesToPlot[i].set( self.axesTuple[i] ) # initial value
			Label(self.scatterWin, text=axisNames[i]).grid(row=i)
			w = apply( OptionMenu, (self.scatterWin, self.main.axesToPlot[i]) + self.axesTuple )
			w.grid( row=i, column=1 )
			
		self.main.colorUse = StringVar( self.scatterWin )
		self.main.colorUse.set( "No" )
		colorTuple = ( "No", "Clusters", "Last Column")
		Label(self.scatterWin, text="Use color?").grid( row=self.axisNum.get(), column=0)
		colorDrop = apply( OptionMenu, (self.scatterWin, self.main.colorUse) + colorTuple )
		colorDrop.grid( row=self.axisNum.get(), column=1 )
			
		for i in range( len( self.main.axesToPlot ) ):
			if i == 0:
				self.main.xAxisHeader = self.main.axesToPlot[i].get()
			if i == 1:
				self.main.yAxisHeader = self.main.axesToPlot[i].get()
			if i == 2:
				self.main.zAxisHeader = self.main.axesToPlot[i].get()

		def callback():
			self.scatterWin.destroy()
			if ( self.main.colorUse.get() == "Clusters" ):
				self.pcaClusters()
			else:
				self.scatterBuild()
		
		b = Button( self.scatterWin, text="Continue", command=callback )
		b.grid( row=self.axisNum.get()+3, columnspan=2 )
		
		
	def pcaClusters( self ):
		self.scatterWin = Tk()
		self.scatterWin.title('Choose Options For Clustering')
		
		winHeight = 150+(self.axisNum.get()*20)
		sizeString = "300x"+str( winHeight )+"-80+80"
		self.scatterWin.geometry( sizeString )
		
		self.main.clusterNum = IntVar( self.scatterWin )
		self.main.clusterNum.set( 3 )
		clusterNumTuple = ()
		for i in range( 2, 15 ):
			clusterNumTuple += ( (i+1), )
		Label(self.scatterWin, text="Number of Clusters").grid(row=1)
		k = apply( OptionMenu, (self.scatterWin, self.main.clusterNum) + clusterNumTuple )
		k.grid( row=1, column=1 )

		def callback():
			self.scatterWin.destroy()
			self.dataInstance.prepareClusters()
			self.scatterBuild()
		
		b = Button( self.scatterWin, text="Continue", command=callback )
		b.grid( row=2, columnspan=2 )
		
		
##### Cluster-related Functions #########################################################

	def clusterCase( self ):
		"""Controls the window used to choose options for a new PCA and clustering
		   visualization."""
		
		self.scatterWin = Tk()
		self.scatterWin.title('Choose Options For Clustering')
		
		winHeight = 150+(self.axisNum.get()*20)
		sizeString = "300x"+str( winHeight )+"-80+80"
		self.scatterWin.geometry( sizeString )
		
		self.main.clusterChoice = StringVar( self.scatterWin )
		self.main.clusterChoice.set( "Normal" )
		clusterChoiceTuple = ( "Normal", "PCA" )
		Label(self.scatterWin, text="Data by which to Cluster").grid(row=0)
		w = apply( OptionMenu, (self.scatterWin, self.main.clusterChoice) + clusterChoiceTuple )
		w.grid( row=0, column=1 )
		
		self.main.clusterNum = IntVar( self.scatterWin )
		self.main.clusterNum.set( 3 )
		clusterNumTuple = ()
		for i in range( 2, 15 ):
			clusterNumTuple += ( (i+1), )
		Label(self.scatterWin, text="Number of Clusters").grid(row=1)
		k = apply( OptionMenu, (self.scatterWin, self.main.clusterNum) + clusterNumTuple )
		k.grid( row=1, column=1 )

		def callback():
			self.scatterWin.destroy()
			self.dataInstance.prepareClusters()
			self.scatterBuild()
		
		b = Button( self.scatterWin, text="Continue", command=callback )
		b.grid( row=2, columnspan=2 )
		
		




##### Filtering-Related Functions #######################################################	
	
	def filterCase( self ):
		
		self.root = Tk()
		self.root.title('Choose Filter Options')
		
		if ( self.main.filterUse.get() == "One" ):
			filterCount = 1
		elif ( self.main.filterUse.get() == "Two" ):
			filterCount = 2
		
		winHeight = str(30+(130*filterCount))
		
		self.root.geometry('500x'+winHeight+'-80+80')
		
		localFilterList = []
		self.main.filterList = None
		
		for i in range( filterCount ):
			headerFilter = StringVar( self.root )
			exactFilter = StringVar( self.root )
			minValFilter = StringVar( self.root )
			maxValFilter = StringVar( self.root )
			
			chooseMessage = " (Choose an axis and fill in either 'Exact Value' OR the 'Max' and 'Min')"
			sectionName = "Filter "+str(i+1)+chooseMessage
			Label(self.root, text=sectionName ).grid(row=(5*i), columnspan=2)
			Label(self.root, text="Axis to Filter").grid(row=(5*i)+1, column=0, sticky=tk.W)
			Label(self.root, text="Exact Value").grid(row=(5*i)+2, column=0, sticky=tk.W)
			Label(self.root, text="Min Value").grid(row=(5*i)+3, column=0, sticky=tk.W)
			Label(self.root, text="Max Value").grid(row=(5*i)+4, column=0, sticky=tk.W)
			
			gridPlace = []
			for k in range( (5*i)+1, 5*(i+1) ):
				gridPlace.append( k )
			
			headersTuple = ()
			for i in range( len( self.dataInstance.metaData ) ):
				headersTuple = headersTuple + (self.dataInstance.metaData[i][0], )
			drop = apply( OptionMenu, (self.root, headerFilter) + headersTuple )
			drop.grid(row=gridPlace.pop(0), column=1)
			
			headerFilter.set( headersTuple[0] )

			text1 = Entry( self.root, textvariable=exactFilter )
			text1.grid(row=gridPlace.pop(0), column=1)

			text2 = Entry( self.root, textvariable=minValFilter )
			text2.grid(row=gridPlace.pop(0), column=1)

			text3 = Entry( self.root, textvariable=maxValFilter )
			text3.grid(row=gridPlace.pop(0), column=1)
			
			fieldList = [ headerFilter, exactFilter, minValFilter, maxValFilter ]
			
			localFilterList.append( fieldList )
			
		def callback():
			"""Handles the button press at the end of the filter function."""
			self.root.destroy()
			
			for i in range( len( localFilterList ) ):
				for j in range( len( localFilterList[0] ) ):
					localFilterList[i][j] = localFilterList[i][j].get()
			self.main.filterList = localFilterList
			
			if ( self.main.colorUse.get() == "Clusters" ):
				self.dataInstance.filteredSelect()
				self.clusterCase()
			else:
				self.dataInstance.filteredSelect()
				if ( self.plotType == "Scatterplot" ):
					self.dataInstance.filteredSelect()
					self.scatterBuild()
				elif ( self.plotType == "Histogram" ):
					self.histoCase()
				
			
		b1 = Button( self.root, text="Confirm Filter Preferences", command=callback )
		b1.grid( row=5*(i+1), columnspan=2 )




##### Special Case 1 Functions ######################################################

	def special1Case( self ):
		self.root = Tk()
		self.root.title('Choose Filter Options')

		filterCount = 2
		
		winHeight = str(30+(130*filterCount))
		self.root.geometry('500x'+winHeight+'-80+80')
		
		self.main.filterList = None
		
		subjectHeader = StringVar( self.root )
		subjectHeader.set( "SubjectID" )
		subjectField = StringVar( self.root )
		imageHeader = StringVar( self.root )
		imageHeader.set( "Image" )
		imageField = StringVar( self.root )
		
		self.main.colorUse = StringVar( self.root )
		self.main.colorUse.set( "Number" )
		self.main.sizeUse = StringVar( self.root )
		self.main.sizeUse.set( "Duration" )
		
		self.main.filterUse = StringVar( self.root )
		self.main.filterUse.set( "Two" )
		
		emptyFilter = StringVar( self.root )
		
		self.main.axesToPlot = [ None, None ]
		self.main.axesToPlot[0] = StringVar( self.root )
		self.main.axesToPlot[0].set( "x" )
		self.main.axesToPlot[1] = StringVar( self.root )
		self.main.axesToPlot[1].set( "y" )
		
		Label(self.root, text="Choose a subject and image to view fixation results.").grid(row=0, columnspan=2)
		Label(self.root, text="Subject:").grid(row=1, column=0, sticky=tk.W)
		Label(self.root, text="Image:").grid(row=2, column=0, sticky=tk.W)

		subjectText = Entry( self.root, textvariable=subjectField )
		subjectText.grid(row=1, column=1)

		imageText = Entry( self.root, textvariable=imageField )
		imageText.grid(row=2, column=1)
		
		subjectFieldList = [ subjectHeader, subjectText, emptyFilter, emptyFilter ]
		imageFieldList = [ imageHeader, imageText, emptyFilter, emptyFilter ]
			
		localFilterList = [ subjectFieldList, imageFieldList ]
			
		def callback():
			"""Handles the button press at the end of the filter function."""
			for i in range( len( localFilterList ) ):
				for j in range( len( localFilterList[0] ) ):
					localFilterList[i][j] = localFilterList[i][j].get()
			self.main.filterList = localFilterList
			self.root.destroy()
			self.scatterBuild()
			
		b1 = Button( self.root, text="View Fixation Results", command=callback )
		b1.grid( row=3, columnspan=2 )




##### Miscellaneous Functions ###########################################################
	
	def resetLegendHeaders( self ):
		"""Resets the scatterplot legends to nothing when creating a new plot."""
		self.main.xAxisHeader = None
		self.main.yAxisHeader = None
		self.main.zAxisHeader = None
		self.main.colorHeader = None
		self.main.sizeHeader  = None




class StatsBox:
		"""Manages the windows and methods for creating a box to display numerical
		   statistics."""

##### Initialization ####################################################################

		def __init__( self, main, dataInstance, stat, axes ):
			self.root = Tk()
			self.stat = stat
			self.dataInstance = dataInstance
			self.main = main
			self.statsToShow = None
			
			self.root.title( 'Choose Axis For '+str(stat) )
			self.root.geometry('250x100-80+80') 
			
			self.statsToShow = StringVar( self.root )
			self.statsToShow.set( axes[0] ) # initial value
			
			Label(self.root, text="Variable").grid(row=0)
			
			self.axesTuple = ()
			for i in range( len( axes ) ):
				self.axesTuple = self.axesTuple + ( axes[i], )
			
			w = apply( OptionMenu, (self.root, self.statsToShow) + self.axesTuple	)
			w.grid(row=0, column=1)
			
			b = Button( self.root, text="Show Statistics", command=self.showStats )
			b.grid( row=1, columnspan=2 )

			
		def showStats( self ):
			self.root.destroy()
			
			self.statWin = Tk()
			self.statWin.title( 'Showing '+str(self.stat)+' for '+str(self.statsToShow.get()) )
			self.statWin.geometry('400x150-80+80')
			
			headerList = self.dataInstance.metaData
			header = self.statsToShow.get()
		
			for i in range( len( headerList ) ):
				if header == headerList[i][0]:
					dataIndex = i
		
			varList = self.dataInstance.numbData[:,dataIndex]
			
			if self.stat == "Mean":
				Label(self.statWin, text=self.stat).grid(row=0,column=0, sticky=tk.W)
				meanString = str(self.main.mean( varList ))
				Label(self.statWin, text=meanString).grid(row=0,column=1, sticky=tk.W)
				
			elif self.stat == "Median":
				Label(self.statWin, text=self.stat).grid(row=0,column=0, sticky=tk.W)
				medianString = str(self.main.median( varList ))
				Label(self.statWin, text=medianString).grid(row=0,column=1, sticky=tk.W)
				
			elif self.stat == "Mode":
				Label(self.statWin, text=self.stat).grid(row=0,column=0, sticky=tk.W)
				modeString = str(self.main.mode( varList ))
				Label(self.statWin, text=modeString).grid(row=0,column=1, sticky=tk.W)
				
			elif self.stat == "Range":
				Label(self.statWin, text=self.stat).grid(row=0,column=0, sticky=tk.W)
				rangeString = str(self.main.range( varList ))
				Label(self.statWin, text=rangeString).grid(row=0,column=1, sticky=tk.W)
				
			elif self.stat == "Standard Deviation":
				Label(self.statWin, text=self.stat).grid(row=0,column=0, sticky=tk.W)
				stdDevString = str(self.main.stdDev( varList ))
				Label(self.statWin, text=stdDevString).grid(row=0,column=1, sticky=tk.W)
				
			elif self.stat == "All":
				Label(self.statWin, text="Mean").grid(row=0,column=0, sticky=tk.W)
				meanString = str(self.main.mean( varList ))
				Label(self.statWin, text=meanString).grid(row=0,column=1, sticky=tk.W)
				
				Label(self.statWin, text="Median").grid(row=1,column=0, sticky=tk.W)
				medianString = str(self.main.median( varList ))
				Label(self.statWin, text=medianString).grid(row=1,column=1, sticky=tk.W)
				
				Label(self.statWin, text="Mode").grid(row=2,column=0, sticky=tk.W)
				modeString = self.main.mode( varList )
				Label(self.statWin, text=modeString).grid(row=2,column=1, sticky=tk.W)
				
				Label(self.statWin, text="Range").grid(row=3,column=0, sticky=tk.W)
				rangeString = str(self.main.range( varList ))
				Label(self.statWin, text=rangeString).grid(row=3,column=1, sticky=tk.W)
				
				Label(self.statWin, text="Standard Deviation").grid(row=4,column=0, sticky=tk.W)
				stdDevString = str(self.main.stdDev( varList ))
				Label(self.statWin, text=stdDevString).grid(row=4,column=1, sticky=tk.W)



class StringDialog:

##### Initialization ####################################################################

	def __init__( self, string ):
		self.root = Tk()
		Label(self.root, text=string).grid()




class WelcomeDialog:
	"""Manages the window and initialization for creating a the V.I.O.L.A.S. welcome
	   box."""

##### Initialization ####################################################################

	def __init__( self ):
		"""Initializes the welcome window."""
		self.root = Tk()
		self.root.title('Welcome')
		self.root.geometry('515x350')
		w = tk.Message(self.root, anchor='center',
					text=	"			   Welcome to V.I.O.L.A.S.!\n\n" + 
							"		Visual Information Observation, Logging and Analysis System\n\n" +
							"  Key Features Include:\n\n" +
							"	*Ability to Read in any CSV File\n" +
							"	*Made to Order Graphical Representations\n" +
							"	*Quick and Easy Statistical Computation\n\n" +
							"  How to Use V.I.O.L.A.S:\n\n" +
							"	*Step 1: Under the file menu, use Open to import any csv file. The\n" + 
							"		data will be presented in an easy to read format in the\n" + 
							"		terminal.\n\n" +
							"	*Step 2: Under the graphs menu, one can create either a histogram, a\n" +
							"		scatterplot (4D,3D,2D), or a box plot. Each type of graphical\n" +
							"		representation takes user input in order to create the graph.\n\n" +
							"	*Step 3: Under the calculations menu, one can calculate the mean,\n" +
							"		median, mode, standard deviation, and the range depending on \n" +
							"		the user's wants. \n\n" +
							"	*Step 4: Have fun and immerse yourself in the wonders of \n" +
							"		graphical analysis that this program has to offer!\n\n",
						background='blue', foreground='white', border=0, width=550, font='courier 12 bold')
		w.pack()




class DataViewDialog:
	"""Manages the windows and initialization for creating a box to display the entire
	   data set at once."""

##### Initialization ####################################################################

	def __init__( self, filename, data ):
		"""Initializes the data view window."""
		self.root = Tk()
		self.root.title(filename)
		self.root.geometry('1024x768')
		
		# Create the scrollbar UI widgets
		scrollbarY = tk.Scrollbar(self.root)
		scrollbarY.pack(side=tk.RIGHT, fill=tk.Y)
		scrollbarX = tk.Scrollbar(self.root, orient=tk.HORIZONTAL)
		scrollbarX.pack(side=tk.BOTTOM, fill=tk.X)

		# Adds the text object to the window and makes it un-editable.
		w = tk.Text(self.root, wrap=tk.NONE, yscrollcommand=scrollbarY.set, xscrollcommand=scrollbarX.set, font='courier 12 bold')
		w.insert(tk.INSERT, data)
		w.config( state=tk.DISABLED )
		w.pack( expand=1, fill=tk.BOTH) 
		
		# Activate the scrollbars for their respective views.
		scrollbarY.config(command=w.yview)
		scrollbarX.config(command=w.xview)




class FileSaveDialog:

##### Initialization ####################################################################
	
	def __init__( self, main, dataInstance, axes ):
		"""Initializes the file saving dialog."""
		self.main = main
		self.dataInstance = dataInstance
		self.axes = axes
		
		self.root = Tk()
		self.root.title( "Save As CSV" )
		self.root.geometry( "350x200" )
		
		Label( self.root, text="Choose options for save." ).grid( row=0, columnspan=2 )
		
		Label(self.root, text="Filename").grid( row=1,column=0, sticky=tk.W )
		self.main.saveFileName = StringVar( self.root )
		fileNameField = Entry( self.root, textvariable=self.main.saveFileName )
		fileNameField.grid(row=1, column=1)
		
		Label( self.root, text="Number of Columns" ).grid( row=2,column=0, sticky=tk.W )
		self.main.numSaveCols = StringVar( self.root )
		self.main.numSaveCols.set( "All" )
		colNumTuple = ( "All", )
		for i in range( len(axes) ):
			colNumTuple += ( str(i+1), )
		w = apply( OptionMenu, ( self.root, self.main.numSaveCols ) + colNumTuple )
		w.grid( row=2, column=1 )
		
		def callback():
			self.root.destroy()
			if self.main.numSaveCols.get() == "All":
				self.main.writeCSVFile()
			else:
				self.columnChooser()
				
		b1 = Button( self.root, text="Confirm", command=callback )
		b1.grid( row=3, columnspan=2 )	
		
		
	def columnChooser( self ):
		self.root = Tk()
		self.root.title( "CSV Save Options" )
		
		choiceNum = int(self.main.numSaveCols.get())
		
		geomString = '300x'+str(30+(50*choiceNum))+'-80+80'
		self.root.geometry( geomString)
		
		Label( self.root, text="Choose the header you want in each slot.").grid( row=0, columnspan=2 )
		
		axesTuple = tuple( self.axes )
		self.main.saveChoiceList = [ None ]*choiceNum
		
		for i in range( choiceNum ):
			labelString = "Column "+str(i+1)
			rowNum = i+1
			Label( self.root, text=labelString ).grid( row=rowNum, column=0 )
			self.main.saveChoiceList[i] = StringVar( self.root )
			self.main.saveChoiceList[i].set( self.axes[i] )
			w = apply( OptionMenu, ( self.root, self.main.saveChoiceList[i] ) + axesTuple )
			w.grid( row=rowNum, column=1 )
		
		def callback():
			self.root.destroy()
			self.main.writeCSVFile()
		
		b1 = Button( self.root, text="Confirm", command=callback )
		buttonRow = choiceNum+1
		b1.grid( row=buttonRow, columnspan=2 )




class FileExportDialog:

##### Initialization ####################################################################
	
	def __init__( self, main, dataInstance, axes ):
		"""Initializes the file saving dialog."""
		self.main = main
		self.dataInstance = dataInstance
		self.axes = axes
		
		self.root = Tk()
		self.root.title( "Export As ARFF" )
		self.root.geometry( "350x100" )
		
		Label( self.root, text="Choose options for save." ).grid( row=0, columnspan=2 )
		
		Label(self.root, text="Filename").grid( row=1,column=0, sticky=tk.W )
		self.main.saveFileName = StringVar( self.root )
		fileNameField = Entry( self.root, textvariable=self.main.saveFileName )
		fileNameField.grid(row=1, column=1)
		
		def callback():
			self.root.destroy()
			self.main.writeARFFFile()
				
		b1 = Button( self.root, text="Confirm", command=callback )
		b1.grid( row=3, columnspan=2 )