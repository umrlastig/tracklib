:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 07/03/2021


Core concept
============

.. container:: centerside
  
   .. figure:: ../img/dc_track.png
      :width: 700px
      :align: center
		
      Diagramme de classe de Track
		

**TODO**


Obs
***

Les coordonnées peuvent être sphériques ou cartésiennes


Track
*****

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


.. figure:: ../img/Profil_vitesse_spatial_temporel.png
   :width: 450px
   :align: center
		
   Figure 1 : Comparaison de profils de vitesse dans les domaines spatial (en bleu) et temporel (en rouge). On voit bien que le profil spatial est systématiquement plus contracté aux zones de faibles vitesses, et à l'inverse plus dilaté à haute vitesse.




Opérations mathématiques
------------------------

De nouvelles surcharges d'opérateurs pour Track et TrackCollection:

* + concatène 2 traces/collections
* - calcule le profil de différence entre 2 traces
* * sur-échantillonne la trace/collection du facteur voulu
* ** rééchantillonne une trace / collection au nombre de points voulu
* / divise une trace/collection en portions à peu près égales
* // rééchantillonne une trace pour faire correspondre ses timestamps à une autre trace
* % supprime des points à intervalle régulier
* <  (flèche vers la gauche) supprime les n derniers points d'une trace
* >  (flèche vers la droite) supprime les n premiers points d'une trace
* [i]  retourne ou modifie la ieme observation / trace
* len( )   nombre d'observations / traces
* le moins "unaire", abs, "!=", ">=" et "<=" restent disponibles si tu as des idées


#. Deux méthodes pour ajouter un nouvel AF de nom "new_AF_name" et affecte la valeur 2 à chaque observation ::

    # méthode 1
    track['new_AF_name'] = 2

    # méthode 2
    track['new_AF_name'] = [2] * len(track)
    

#. Pour ajouter un nouvel AF de nom "new_AF_name" et affecte à chaque observation les valeurs de 0 à n-1 ::

    track['new_AF_name'] = [i for i in range(len(track)]




Track collection
****************


.. raw:: html
   
   <p><br/><br/></p>
