# Nicholas Balsbaugh & Alex Swanson
# CS251 - Data Analysis and Visualization
# Professor Bruce Maxwell
# March 10th, 2011

import numpy as np
import math



class ViewRef:
	"""The ViewRef class calculates the positioning of the plot in relation to the viewer's position to create a 3D effect."""
	
	
	def __init__( self, vrp = np.matrix( [ 0.5, 0.5, 0 ] ), vpn = np.matrix( [ 0, 0, 1 ] ), vup = np.matrix( [ 0, 1, 0 ] ), u = np.matrix( [ 1, 0, 0 ] ), extent = np.array( [ 1.0, 1.0, 1.0 ] ), view = np.array( [ 400.0, 400.0 ] ), viewOffset = np.array( [ 20.0, 20.0 ]) ):
		self.vrp = vrp
		self.vpn = vpn
		self.vup = vup
		self.u = u
		self.extent = extent
		self.view = view
		self.viewOffset = viewOffset
		return

	 
	"""Reset the axes to fresh."""	 
	def reset( self ):
		self.vrp = np.matrix( [ 0.5, 0.5, 0 ] )
		self.vpn = np.matrix( [ 0, 0, 1 ] )
		self.vup = np.matrix( [ 0, 1, 0 ] )
		self.u = np.matrix( [ 1, 0, 0 ] )
		self.extent = np.array( [ 1, 1, 1 ] )
		self.view = np.array( [ 400, 400 ] )
		self.viewOffset = np.array( [ 20, 20 ] )

		
	"""Build the initial axes."""	 
	def build( self ):
		m = np.identity( 4, float )
		t1 = np.matrix( [	[ 1, 0, 0, -self.vrp[ 0, 0 ] ],
							[ 0, 1, 0, -self.vrp[ 0, 1 ] ],
							[ 0, 0, 1, -self.vrp[ 0, 2 ] ],
							[ 0, 0, 0, 1 ] ] )
		m = t1 * m
		tu = np.cross( self.vup, self.vpn )
		tvup = np.cross( self.vpn, tu )
		tvpn = self.vpn
		
		self.u = self.normalize( tu )
		self.vup = self.normalize( tvup )
		self.vpn = self.normalize ( tvpn )
		
		r1 = self.R( tu, tvup, tvpn )
		
		m = r1 * m
		m = self.T( 0.5*self.extent[0], 0.5*self.extent[1], 0 ) * m
		m = self.S( -self.view[0] / self.extent[0], -self.view[1] / self.extent[1], 1.0 / self.extent[2] ) * m
		m = self.T( self.view[0] + self.viewOffset[0], self.view[1] + self.viewOffset[1], 0 ) * m
		
		return m
	   
		   
	def normalize( self, v	):
		return v / float( np.sqrt( np.sum( np.multiply( v, v ) ) ) )
	
	
	def R( self, a, b, c ):
		return np.matrix( [[ a[0, 0], a[0, 1], a[0, 2], 0.0 ],
						   [ b[0, 0], b[0, 1], b[0, 2], 0.0 ],
						   [ c[0, 0], c[0, 1], c[0, 2], 0.0 ],
						   [ 0.0, 0.0, 0.0, 1.0 ]], float )
	
	
	def T( self, x, y, z ):
		return np.matrix( [[ 1, 0, 0, x ],
						   [ 0, 1, 0, y ],
						   [ 0, 0, 1, z ],
						   [ 0, 0, 0, 1 ]], float )
	 
		
	def S( self, x, y, z ):
		return np.matrix( [ [ x, 0, 0, 0 ],
							[ 0, y, 0, 0 ],
							[ 0, 0, z, 0 ],
							[ 0, 0, 0, 1 ] ], float )
		
		
	def rotateVRC( self, vupAngle, uAngle, vrpAngle ):
		point = self.vrp + self.vpn * self.extent[2] * 0.5
		t1 = self.T( -point[0,0], -point[0,1], -point[0,2] )
		Rxyz = self.R( self.u, self.vup, self.vpn )
		r1 = self.aboutY( vupAngle )
		r2 = self.aboutX( uAngle )
		r3 = self.aboutZ( vrpAngle )
		t2 = self.T( point[0,0], point[0,1], point[0,2] )
		tvrc = self.createTVRC()
		tvrc = (t2*Rxyz.transpose()*r3*r2*r1*Rxyz*t1*tvrc.transpose()).transpose()

		self.vrp = tvrc[0,:3]
		self.u = tvrc[1,:3]
		self.vup = tvrc[2,:3]
		self.vpn = tvrc[3,:3]
		
		self.normalize( self.u )
		self.normalize( self.vup )
		self.normalize( self.vpn )
		
		 
	# Matrix used for rotating about the x
	def aboutX( self, angle ):
		return np.matrix( 	 [[1.0, 0.0,			 0.0,				 0.0],
							  [0.0, math.cos(angle), -(math.sin(angle)), 0.0],
							  [0.0, math.sin(angle), math.cos(angle),	 0.0],
							  [0.0, 0.0,			 0.0,				 1.0]] )
	
	# Matrix used for rotating about the y
	def aboutY( self, angle ):
		return np.matrix( 	 [[math.cos(angle),	   0.0, math.sin(angle),  0.0],
							  [0.0,				   1.0, 0.0,			  0.0],
							  [-(math.sin(angle)), 0.0, math.cos(angle),  0.0],
							  [0.0,				   0.0, 0.0,			  1.0]] )
	
	# Matrix used for rotating about the z
	def aboutZ( self, angle ):
		return np.matrix( 	 [[math.cos(angle),	   -(math.sin(angle)), 0.0, 0.0],
							  [math.sin(angle),	   math.cos(angle),	   0.0, 0.0],
							  [0.0,				   0.0,				   1.0, 0.0],
							  [0.0,				   0.0,				   0.0, 1.0]] )
	
	def createTVRC( self ):
		a = np.matrix( [ self.vrp[0,0], self.vrp[0,1], self.vrp[0,2], 1 ], float )
		b = np.matrix( [ self.u[0,0], self.u[0,1], self.u[0,2], 0 ], float )
		c = np.matrix( [ self.vup[0,0], self.vup[0,1], self.vup[0,2], 0 ], float )
		d = np.matrix( [ self.vpn[0,0], self.vpn[0,1], self.vpn[0,2], 0 ], float )
		m = np.vstack( (a,b,c,d) )
		return m
	
	
	
if __name__ == "__main__":
	help(ViewRef)
	vR = ViewRef()