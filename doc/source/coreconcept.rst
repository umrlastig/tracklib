

Core concept
=================

.. container:: centerside
  
   .. figure:: ./img/dc_track.png
      :width: 700px
      :align: center
		
      Diagramme de classe de Track
		

**TODO**


Obs
*****

Les coordonnées peuvent être sphériques ou cartésiennes

Track
*******

Les attributs *speed* et *abs_curv* ne sont pas calculés. Ils le seront automatiquement en appelant les fonctions:
* getAbsCurv
* getSpeed

Ces 2 attributs font partie des AF de Track. Il faut lancer le calcul si on veut les utiliser pour d'autres calculs d'AF.


.. * extract
.. * split 
.. * Resample
.. * Segmentation
.. * Comparaison de 2 traces
.. * randomizer, noise


.. figure:: ./img/Profil_vitesse_spatial_temporel.png
   :width: 450px
   :align: center
		
   Figure 1 : Comparaison de profils de vitesse dans les domaines spatial (en bleu) et temporel (en rouge). On voit bien que le profil spatial est systématiquement plus contracté aux zones de faibles vitesses, et à l'inverse plus dilaté à haute vitesse.





