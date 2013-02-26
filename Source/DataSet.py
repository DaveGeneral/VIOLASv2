# Nicholas Balsbaugh & Alex Swanson
# CS251 - Data Analysis and Visualization
# Project 6 - Visualization II
# Professor Bruce Maxwell
# April 9th, 2011


# Imports
import numpy
import csv


class DataSet:
	"""Creates a class, DataSet, that holds data and enables the
	   user to do simple data manipulation and transformations."""

##### Initialization ####################################################################

	def __init__( self, viewer, filename=None, passData=None ):
		print "Beginning File Reading"
		#The main program
		self.viewer = viewer
		#List of the headers in the data set
		self.headers = []
		#List of all the types in the data set
		self.types = []
		#Tuple of both headers and types which comprise the meta-data
		self.metaData = []
		#List of tuples that contains all information in data set
		self.rawData = []
		#A numpy matrix only containing numeric data
		self.numbData = []
		#A numpy matrix containing only the prescaled numeric data
		self.preData = []
		#The data that has been filtered.
		self.filteredData = None
		# A list of data indices.
		self.dataIdx = []
		#File name can be hard coded in
		if passData != None:
			self.install( passData )
		
		if filename != None:
			self.read( filename )
		
		#Set up of Filtering System Variables
		self.filter1 = None
		self.filter2 = None
		self.filteredMatrix = None




##### I/O Functions #####################################################################

	def read( self, filename ):
		# Read the file and import into rawData list
		fp = file( filename, 'rU' )
		info = csv.reader( fp )
		self.dataIter = csv.reader( fp )
		print "File Data Imported"
		for i in info:
			self.rawData.append(i)
		print "Raw Data Array Created"
		self.prepareData()
		
		
	def install( self, passData ):
		self.rawData = passData
		self.prepareData()
		
		
	def prepareData( self ):

		# Append headers and types to lists
		self.headers = self.rawData[0]
		print "Data Header List Created"
		self.types = self.rawData[1]
		print "Data Type List Created"
		print "Preparing to create meta-data list, please stand by..."
		for i in range( len( self.headers )):
			print "Adding Column",i+1,"of",len( self.headers )
			self.metaData.append( (self.headers[i].lstrip(), self.types[i].lstrip() ) )
		print "Meta-data list completed."
			
		# Append numeric data to numbData matrix
		print "Preparing to create numeric data matrix, please stand by..."
		numbers = []
		dataCount = len(self.rawData)
		for i in range(2, dataCount):
			print "Beginning Row",i+1,"of",dataCount
			numPoint = []
			for j in range( len(self.rawData[0]) ):
				if self.rawData[1][j].lstrip() == 'numeric':
					numPoint.append( float( self.rawData[i][j] ) )
					if j not in self.dataIdx:
						self.dataIdx.append(j)
			numbers.append(numPoint)
		
		print "Creating final numerical data matrix, please stand by..."
		self.numbData = numpy.matrix(numbers)
		print "Done creating numerical data matrix."
		print "Copying data to build pre-scaled data matrix."
		self.preData = numpy.matrix(numbers)
		print "Copy complete. Building pre-scaled data matrix, please stand by..."
		#self.prescale( self.preData )
		
		print "Creating cleaner raw data array, please stand by..."
		for i in range( len( self.rawData ) ):
			for j in range( len( self.rawData[0] ) ):
				self.rawData[i][j] = self.rawData[i][j].lstrip()
		print "Done creating new raw data array."
		print "Data import completed. Enjoy V.I.O.L.A.S."
		
		
	def write( self, filename ):
		"""Writes file to output. Unused in current program."""
		file = open(filename, "wb")
		writer = csv.writer(open(filename, "wb"))
		for line in self.rawData:
			writer.writerow(line)
		file.close()
		
		
	def prescale( self, matrix ):
		"""Pre-scales the numerical data to a 0-to-1 scale."""
		print "Fetching maximums and minimums for each column."
		maximums = matrix.max(0)
		minimums = matrix.min(0)
		
		print "Beginning scaling. Please stand by. (THIS MAY TAKE A WHILE)"
		for y in range( matrix.shape[0] ):
			for x in range( matrix.shape[1] ):
				point = matrix[ y, x ]
				matrix[y,x] = ( point - minimums[0,x] )/( maximums[0,x] - minimums[0,x] )




##### Data Manipulation and Calculation #################################################

	def range( self, idx=None ):
		"""Returns the minimum and maximum of each column(variable). Optional parameter
		   if the user only wants the range of a single column (variable)."""
		minmaxList = []
		if idx == None:
			for i in range(self.numbData.shape[1]):
				min = numpy.min(self.numbData[:,i])
				max = numpy.max(self.numbData[:,i])
				minmaxList.append([min,max])
			return minmaxList
		else:
			matrixIdx = self.dataIdx.index(idx)
			min = numpy.min(self.numbData[:,matrixIdx])
			max = numpy.max(self.numbData[:,matrixIdx])
			minmaxList.append([min,max])
			return minmaxList
	

	#Returns the mean of each column(variable). Optional parameter if
	#the user only wants the mean of a single column(variable).
	def mean( self, idx=None ):
		meanList = []
		if idx == None:
			for i in range(self.numbData.shape[1]):
				mean = numpy.mean(self.numbData[:,i])
				meanList.append(mean)
			return meanList
		else:
			matrixIdx = self.dataIdx.index(idx)
			mean = numpy.mean(self.numbData[:,matrixIdx])
			meanList.append(mean)
			return meanList
	
	# Returns the standard deviation of each column(variable). Optional parameter if
	# The user only wants the standard deviation of a single column(variable).
	def stdev( self, idx=None ):
		sdList = []
		if idx == None:
			for i in range(self.numbData.shape[1]):
				SD = numpy.std(self.numbData[:,i], ddof=1)
				sdList.append(SD)
			return sdList
		else:
			matrixIdx = self.dataIdx.index(idx)
			SD = numpy.std(self.numbData[:,matrixIdx], ddof=1)
			sdList.append(SD)
			return sdList
	
	#Returns a matrix of the selected columns dicated by the user
	#Cannot pass in more than 5 indices!
	def select( self, idx ):
		if len(idx) < 1:
			print("Too Few Desired Columns! Choose a number between 1 and 5!")
		elif len(idx) > 5:
			print("Too Many Desired Columns! Choose a number equal to 5 or less!")
		else:
			selectData = []
			for i in range(len(self.rawData)):
				if ( i > 1 ):
					Dpoints = []
					for index in idx:
						Dpoints.append(self.rawData[i][int(index)])
					selectData.append(Dpoints)
			matrix = numpy.matrix(selectData)
			return matrix
		
		


##### Data Plotting #####################################################################		
				
	def prepareScatterData( self ):
		tempData = []
		self.viewer.plotMatrix = []
		
		axisHeaders = []
		for axis in self.viewer.axesToPlot:
			axisHeaders.append( axis.get() )
		
		if ( self.viewer.filterUse.get() != "None" ):
			tempData = self.filteredData
			dataHeaders = tempData[0,:]
			tempData = tempData[1:,:]
			
		else:
			tempData = numpy.copy( self.rawData )
			tempData = numpy.matrix( tempData )
			dataHeaders = tempData[0,:]
			tempData = tempData[2:,:]

		cols = []
		for k in range( len( axisHeaders ) ):
			for i in range( dataHeaders.shape[1] ):
				if axisHeaders[k] == dataHeaders[0,i]:
					addRow = tempData[:,i]
					cols.append( addRow )
		
		newMatrix = numpy.hstack( tuple(cols) )
		newMatrix = numpy.matrix( newMatrix, dtype=numpy.float32)
		
		maximums = newMatrix.max(0)
		minimums = newMatrix.min(0)
		
		for y in range( newMatrix.shape[0] ):
			for x in range( newMatrix.shape[1] ):
				point = newMatrix[ y, x ]
				newMatrix[y,x] = ( point - minimums[0,x] )/( maximums[0,x] - minimums[0,x] )
		
		self.viewer.plotMatrix = newMatrix
		
	def prepareHistoData( self ):
		self.viewer.histoCols = []
		filterList = []
		filterHead = self.viewer.histoFilterHead.get()
		for filter in self.viewer.histoFilterList:
			filterList.append( filter.get() )
			
		for filter in filterList:
			self.viewer.filterList = [ [ filterHead, filter, "", "" ] ]
			self.filteredSelect()
			data = self.getFilteredAxis( self.viewer.histoAxis.get() )
			dataTuple = [ filter, data ]
			self.viewer.histoCols.append( dataTuple )
			
			
		
		
	def filteredSelect( self ):
		
		# Create a copy of the data.
		allData = numpy.copy( self.rawData )
		allData = numpy.array( allData  )
		
		# Filter the data for each filter created.
		for filter in self.viewer.filterList:
			allData = numpy.array( allData )
			# Set up the filter parameters.
			filterHead = filter[0]
			if filter[1] != "":
				filterValue = filter[1]
			else:
				filterValue = ( filter[2], filter[3] )
			
			headIndex = 0
			for i in range( allData.shape[1] ):
				if allData[0,i] == filterHead:
					headIndex = i
					
			allData = allData[2:,:]
					
			if isinstance( filterValue, str) == True:
				allData = [ row for row in allData if row[headIndex] == filterValue ]
			else:
				allData = [ row for row in allData if float(row[headIndex]) >= float(filterValue[0]) and float(row[headIndex]) <= float(filterValue[1]) ]
			
			headers = []
			for i in range( len( self.metaData ) ):
				headers.append( self.metaData[i][0] )
			types = []
			for i in range( len( self.metaData ) ):
				types.append( self.metaData[i][1] )
			headers = numpy.matrix( headers )
			types = numpy.matrix( types )
			allData = numpy.vstack( (headers, types, allData ) )
		
		headers = allData[0,:]
		allData = allData[2:,:]
		allData = numpy.vstack( (headers, allData) )
		self.filteredData = allData
		return allData




##### Miscellaneous/Utility Functions ###################################################

	def getAxis( self, axisName ):
		"""Returns the chosen-by-header axis as a one-column matrix regardless of
		   type."""
		tempData = numpy.copy( self.rawData )
		tempData = numpy.matrix( tempData )
		dataHeaders = tempData[0,:]
		returnColumn = None
		for i in range( dataHeaders.shape[1] ):
			if axisName == dataHeaders[0,i]:
				returnColumn = tempData[:,i]
		returnColumn = numpy.matrix( returnColumn )
		return returnColumn


	def getNumericAxis( self, axisName ):
		"""Returns the chosen-by-header axis as a one-column float matrix."""
		tempData = numpy.copy( self.rawData )
		tempData = numpy.matrix( tempData )
		dataHeaders = tempData[0,:]
		tempData = tempData[2:,:]
		returnColumn = None
		for i in range( dataHeaders.shape[1] ):
			if axisName == dataHeaders[0,i]:
				returnColumn = tempData[:,i]
		returnColumn = numpy.matrix( returnColumn, dtype=numpy.float32 )
		return returnColumn
	
	
	def getFilteredAxis( self, axisName ):
		"""Returns the chosen-by-header axis from the filtered data as a one-column
		   float matrix."""
		tempData = numpy.copy( self.filteredData )
		tempData = numpy.matrix( tempData )
		dataHeaders = tempData[0,:]
		tempData = tempData[1:,:]
		returnColumn = None
		for i in range( dataHeaders.shape[1] ):
			if axisName == dataHeaders[0,i]:
				returnColumn = tempData[:,i]
		returnColumn = numpy.matrix( returnColumn, dtype=numpy.float32 )
		return returnColumn



##### PCA Functions ####################################################################

	def pca( self, matrix ):
		"""Returns all of the the eigenvectors and eigenvalues of the numeric data in 
		   sorted order"""
		tempMatx = numpy.matrix.copy( matrix )
		
		if ( self.viewer.pcaNormalize.get() == "Yes" ):
			self.prescale( tempMatx )
		
		covMatx = numpy.cov( tempMatx, rowvar=False )
		(meigval, meigvec) = numpy.linalg.eig( covMatx )
		self.meigvec = numpy.matrix( meigvec )
		
		eigSum = numpy.sum( meigval )
		
		print self.meigvec
		list = []
		total = 0
		self.viewer.numVarVecs = 0
		for i in range( len( meigval ) ):
			label = self.viewer.dataHandler.numbData[i,-1]
			list.append( (meigval[i], meigvec[:,i], label) )
			total += meigval[i]
			if ( ((total/eigSum)*100) < self.viewer.varPercent.get() ):
				self.viewer.numVarVecs += 1
		
		sortedList = sorted(list, key = lambda dup: dup[0], reverse = True)
		
		self.viewer.pcaLabelList = [ ]
		for i in range( self.viewer.numVarVecs ):
			self.viewer.pcaLabelList.append( sortedList[i][2] )
		
		self.viewer.pcaLabelList = numpy.matrix( self.viewer.pcaLabelList )
		
		self.viewer.eigenList = sortedList[:]
		print len( sortedList )
		print self.viewer.numVarVecs
		return sortedList
	
	
	def project( self, matrix, eigenStuff ):
		"""Returns a matrix that is the projection of the data set onto the set of basis
		   vectors"""
		eigenVecs = None
		for dup in eigenStuff:
			toAdd = dup[1]
			if eigenVecs != None:
				eigenVecs = numpy.vstack( ( eigenVecs, toAdd ) )
			else:
				eigenVecs = toAdd
				
		tempMatx = numpy.matrix.copy( matrix )
		#self.prescale( tempMatx )
		meanVal = tempMatx.mean( axis=0 )
		meanDiff = tempMatx.copy() 
		for i in range( meanDiff.shape[0] ):
			meanDiff[i] = meanDiff[i] - meanVal
		pdata = ( numpy.matrix( eigenVecs ) * meanDiff.T ).T

		return pdata


	def buildPCA( self, matrixIn ):
		
		matrix = matrixIn[:]
		
		if ( self.viewer.pcaCut.get() == "Yes" ):
			matrix = matrix[:-1]
	
		pcaStuff = self.pca( matrix )
		
		data = self.project( matrix, pcaStuff )
		
		finalData = []
		
		headerRow = []
		typeRow = []
		for i in range( data.shape[1] ):
			headerRow.append( "EV"+str(i+1) )
			typeRow.append( "numeric" )
			
		finalData.append( headerRow )
		finalData.append( typeRow )
		
		for i in range( data.shape[0] ):
			newRow = []
			for j in range( data.shape[1] ):
				newRow.append( str(data[i,j]) )
			finalData.append( newRow )
		
		return finalData
		
		
	def prepareClusters( self ):
		eVCols = []
		for eVector in self.viewer.axesToPlot:
			eVName = eVector.get()
			if ( self.viewer.filterUse.get() != "None" ):
				eVCols.append( self.getFilteredAxis( eVName ) )
			else:
				eVCols.append( self.getNumericAxis( eVName ) )
		
		finalMatrix = None
		
		for i in range( len( eVCols ) ):
			if finalMatrix != None:
				finalMatrix = numpy.hstack( ( finalMatrix, eVCols[i] ) )
			else:
				finalMatrix = eVCols[i]
				
		if ( self.viewer.clusterChoice.get() == "PCA" ):
			finalMatrix = self.buildPCA( finalMatrix )
			finalMatrix = numpy.matrix( finalMatrix[2:][:], dtype=numpy.float32 )
		
		finalMatrix = numpy.array( finalMatrix )
		self.viewer.plotMatrix = finalMatrix
		self.kCluster( finalMatrix, self.viewer.clusterNum.get() )
			
		
		
	def kCluster ( self, eVectors, clusters ):
		data = eVectors
		count = []
		
		newMeans = eVectors[ :clusters ]
		oldMeans = numpy.zeros( newMeans.shape )
		labels = numpy.zeros( ( data.shape[0], 1 ), dtype=numpy.int16 )
		
		while ( self.distance( newMeans, oldMeans ) > 0.001 ):
			for i in range( len( data ) ):
				curVector = data[i]
				curDist =  self.distance( curVector, newMeans[ labels[i] ] )
				
				for j in range( len( oldMeans ) ):
					tempDist = self.distance( curVector, newMeans[j] )
					if ( tempDist < curDist ):
						curDist = tempDist
						labels[i] = j
				
			oldMeans = numpy.copy( newMeans )
			
			newMeans = numpy.zeros( oldMeans.shape )
			count = numpy.zeros( oldMeans.shape[0] )
			
			for i in range( len( labels ) ):
				newMeans[ labels[i] ] += data[i]
				count[ labels[i] ] += 1
			for i in range( len( newMeans ) ):
				newMeans[i] /= count[i]
		
		self.viewer.labels = labels

	
	def distance( self, c_i, x_j ):
		return numpy.linalg.norm( c_i - x_j )



##### Classifier Functions ####################################################################



		