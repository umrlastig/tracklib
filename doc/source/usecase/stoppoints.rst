
Stop points
===========

Comparaison de 2 méthodes pour détecter les points stops

.. figure:: ../img/Profil_vitesse_spatial_1.png
    :width: 550px
    :align: center

.. raw:: html
   
   <br/>

.. code-block:: python

    from tracklib.core.GPSTime import GPSTime
    import tracklib.algo.Interpolation as interpolation
    from tracklib.io.GpxReader import GpxReader
    import tracklib.algo.Analytics as stop
    from tracklib.algo.Segmentation import findStopsLocal

    path = './data/vincennes.gpx'
    GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
    tracks = GpxReader.readFromGpx(path, srid='ENU')
    trace = tracks[0]
    #trace.toENUCoords()
    trace.summary()
    trace.plot()

    # Interpolation spatiale
    trace.resample(5, interpolation.MODE_SPATIAL) # 5
    trace.compute_abscurv()

    # -----------------------------------------------------------------------------
    # Première méthode
    trace.createAnalyticalFeature('stop_point_with_time_window_criteria', 
	                  stop.VAL_AF_TIME_WINDOW_NONE)
    trace.addAnalyticalFeature(stop.stop_point_with_time_window_criteria, 
                     'stop_point_with_time_window_criteria')

    # -----------------------------------------------------------------------------
    # Autre méthode
    trace.addAnalyticalFeature(stop.stop_point_with_acceleration_criteria)

    # ----------------------------------------------------------------------------- 
    # Méthode 
    T = findStopsLocal(trace, 30, 40)
    print (T.size())
    print ('--')

    # -----------------------------------------------------------------------------
    # # On dessine
    TAB_AFS = ['stop_point_with_time_window_criteria', 'stop_point_with_acceleration_criteria']
    trace.plotProfil('SPATIAL_SPEED_PROFIL', TAB_AFS)

 