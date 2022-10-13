:Author: Yann Méneroux
:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 09/04/2022


Simplify, Interpolate & Filter Tracks
======================================

... Resample, interpolation and smoothing functions (1ère page de la doc)


Simplification
---------------

Reduce the number of observations in track (while preserving time stamps and other information), but in very different ways

Tous les outils qui visent globalement à simplifier une trace pour la rendre moins volumineuse ou plus lisible visuellement. 
La classe comprend donc entre autres les outils de généralisation. 


Interpolation 
-----------------

Les méthodes qui sur-échantillonnent, sous-échantillonnent ou ré-échantillonnent les traces et qui passent donc nécessairement 
par une modélisation / description complète de la trajectoire suivie. Lorsque la trace comporte des timestamps, 
on a alors suppression ou création de nouveaux timestamps. On peut donc considérer que ces méthodes modifient 
les observations, contrairement aux méthodes de lissage qui ne modifient que les géométries des observations. 
Il peut s'agir des méthodes locales (e.g. interpolation linéaire, bézier) ou globales (e.g. splines, krigeage, gaussian process...)


Ces méthodes ne sont sensées conserver les AF qui pour un sous-échantillonnage strict. La porte porte d'entrée de base 
des méthodes d'interpolation dans Track est la fonction resample. 




Filtering 
---------------

Toutes les méthodes de lissage qui modifient les points, sans changer les timestamps, sans supprimer, ni créer de nouveau points. 
Ce sont en général des méthodes locales, qui travaillent avec un voisinage (noyau). La classe comporte :
- des filtres dynamiques (qui nécessitent des informations sur la dynamique du mobile) : Kalman et Markov
- des filtres statistiques (qui étudient par "apprentissage" la distribution des données sur un jeu de données d'exemple. 
  Ici, il y aura Karhunen-Loève (ACP fonctionnelle) qui est au statut de "TO DO"
- des filtres fréquentiels, qui travaillent dans le domaine spectrale pour modifier la trace. Pour l'instant 
  il y a les passe-bas et passe-haut de Fourier et il y aura les ondelette en "TO DO".
- des filtres séquentiels (ou filtres à noyaux), qui travaillent directement dans le domaine spatial ou temporel et avec un noyau local. 


A noter que Markov n'est pas stricto sensu un filtre (en fait c'est une méthode globale donc en principe plus proche des méthodes 
de la classe Interpolation) mais de par sa similarité profonde avec Kalman, je pense que c'est plus logique de le laisser 
dans Filtering (c'est un genre de super-Kalman quand Kalman n'est pas suffisant et qu'on est prêt à consacrer plus de temps de calcul).


Certaines méthodes (en particulier toutes les méthodes d'interpolation non-exactes) permettent aussi de faire du lissage 
(par exemple les processus gaussiens ou certaines formes de splines). Dans ce cas on fait lissage et interpolation simultanées. 


Toutes les méthodes de Filtering sont sensées conserver les AF. Elles peuvent s'appliquer aux coordonnées X, Y, Z, ou aux AF. 
La porte porte d'entrée de base des méthodes de filtrage dans Track est la fonction smooth. 

