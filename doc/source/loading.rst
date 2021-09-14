:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 20/09/2020


Loading GPS data
====================

Many solutions exists to import or build GPS Data.


Import from a GPX File
*************************

.. code-block:: python

   import tracklib.io.GpxReader as gpx
   from tracklib.core.GPSTime import GPSTime
   
	GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2s1Z")

	cpt = 0
	pathdir = '/home/glagaffe/GPS/'
	LISTFILE = os.listdir(pathdir)
	for f in LISTFILE:
    
    	traces = gpx.GpxReader.readFromGpx(pathdir + f)
	    trace = traces[0]


Import from CSV File
***********************

TODO

.. raw:: html
   
   <p><br/><br/></p>

..
	Overall picture of selection process
	**************************************

	selection is performed by a selector object, containing an arbitrary number of constraints, combined by OR, AND or XOR operator. 

	Since only a single operator is allowed in the selector, a "global selector" is provided to the users to combine the output of several individual selectors. Again, the output may be combined with OR, AND or XOR.

	For example, given two circles C1 and C2, and two rectangles R1 and R2, to select tracks crossing either C1 or C2, and either R1 or R2, we would like to write the following combination of constraints : F = (C1 + C2).(R1 + R2), where + and . operators denote OR and AND respectively. 

	Such a constraint requires two different combination rules, and therefore cannot be expressed with a single selector. A solution is to create two disjonctive (OR) type selectors S1 and S2 with S1 = C1 + C2 and S2 = R1 + R2. Then S1 and S2 are combined in a conjunctive (AND) type global selector. 

	Note that boolean algebraic rules show that it is possible as well to combine 4 conjunctive- type selectors (C1.R1, C1.R2, C2.R1 and C2.R2) in a disjunctive-type global selector. 

	Constraints may be based on:
	- a geometrical shape (Rectangle, circle or polygon in Geometrics). This 
	#      is the standard type of constraint. Different modes are:
	#         - MODE_CROSSES: tracks crossing shape interior/boundary are selected
	#         - MODE_INSIDE : tracks remaining fully inside the shape are selected
	#         - MODE_GETS_IN: tracks getting in (at least once) shape are selected
	#         - MODE_INSIDE : tracks getting out (at least once) shape are selected
	- a track t as a reference. Available modes are:
	#         - MODE_CROSSES : tracks  intersecting t (at least once) are selected
	#         - MODE_PARALLEL: tracks  following t are selected
	#    - a "toll gate" segment, defined by two Coords objects: tracks crossing 
	#         (at least once) the toll gate are selected 
	# All these constraint may be provided with an additional time constraint, 
	# specifying the time interval (between two GPSTime dates) where crossing /
	# containing / getting in / getting out... operations are tested. 
	# Besides, there are two types of selection:
	#    - TYPE_SELECT: tracks abiding by constraints are returned as they are
	#    - TYPE_CUT_AND_SELECT: tracks abiding by constraints are cut and returned


	General constraint syntax:
	t1 = TimeConstraint(initial_date, final_date, options)
	....
	c1 = Constraint(shape, t1, options)
	c2 = TrackConstraint(track, t2, options)
	c3 = TollGateConstraint(shape, t3, options)
	...
	s1 = Selector(c1, c2, ..., options)
	s2 = Selector(c3, c4, ..., options)
	...
	selector = GlobalSelector([s1, s2, ...], options)

