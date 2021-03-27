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


Import from a PostgreSQL database
***********************************

You have to precise the connection paramaters to connect to the database and the SQL statement which returns the GPS records. 
Then the parameters of the *readFromDataBase* method correspond to the positions of the columns in the result of the query :
timestamp position, longitude or x position, latitude or y position and elevation position (-1 if not exist).

.. code-block:: python
    
   from tracklib.io.PostgresReader import PostgresReader
 
   # The SQL statement which returns the GPS records
   sql = ' Select trace, idpoint, '
   sql = sql + '    ST_X(ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 3857), 2154)) as lon, '
   sql = sql + '    ST_Y(ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 3857), 2154)) as lat, '
   sql = sql + '    timestamp as datetxt '
   sql = sql + ' From public.gpx '
   sql = sql + ' Where trace = 184626 '
   sql = sql + ' Order by timestamp '

   # Initialize parameters to connect to the database
   param = {'host':'localhost', 'database':'mabase', 'user':'glagaffe', 'password':'bubulle'}
   PostgresReader.initParam(param)

   # Read and load GPS data from the database.
   trace = PostgresReader.readFromDataBase(sql, 4, 2, 3, -1)
   
   # Display summary information of the track
   trace.summary()
	


