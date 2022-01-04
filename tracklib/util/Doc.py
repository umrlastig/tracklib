# -------------------------- Doc -------------------------------
# Functions to help in command line
#
#
#    TODO: a retester
# ----------------------------------------------------------------

import inspect

from tracklib.core.Obs import Obs
from tracklib.core.GPSTime import GPSTime
from tracklib.core.Coords import GeoCoords
from tracklib.core.Track import Track

import tracklib.io.GpxReader as gpx
import tracklib.io.FileReader as fr

import tracklib.core.Track as t
import tracklib.core.Operator as op
#import tracklib.io.PostgresReader as pg


# =============================================================================
#   Aide en mode ligne de commande
#   
# =============================================================================
def search(function_name=None, package=None):
	if package==None:
		package = [GPSTime, 
				   t.Track,
				   GeoCoords, 
				   Obs, 
				   op.Operator, 
				   fr.FileReader,
				   pg.PostgresReader,
				   gpx.GpxReader]
	else:
		if not isinstance(package, list):
			package = [package]
			
	if function_name == None:
		function_name = ""
	
	F_LIST = []
			
	for p in package:
		for f in dir(p):
			if (f[0:1] == "_"):
				continue
			
			if f.lower().find(function_name.lower()) < 0:
				continue
			F_LIST.append(p.__name__ + " " + f)
		
		
	print("-----------------------------------------------------")
	print("TRACKLIB FUNCTIONS: " + (str)(len(F_LIST)))
	print("-----------------------------------------------------")
	for f in F_LIST:
		print(f)
	print("-----------------------------------------------------")
	

def help(function_name=None, object_name=None):
	print("-----------------------------------------------------")
	print (inspect.getdoc(function_name))
	print ('\n')
	#print (inspect.getfullargspec(function_name))
	#print ('\n')
	
	print("-----------------------------------------------------")
	#print (inspect.getattr_static(object_name))
