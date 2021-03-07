

Convention
===============

Convention sur les noms de fonctions pour idéntifier clairement celles qui modifie l'objet et celles qui retourne un autre objet:
"resample" et "make_resampled_copy" ou "make_resampled_version". Le mieux c'est sans doute de tout faire en version modification de l'objet, puis ensuite, dès qu'on aura une fonction copy( ) on pourra faire toutes les versions qui retournent un objet duppliqué :

def make_resampled_version(arg):
    new_track = track.copy( )
    new_track.resample(arg)
    return new_track
	
	
1) pour construire une trace de manière incrémentale
   -> addObs si les obs arrivent dans l'ordre (ajoute l'obs à la fin de la trace)
   -> insertObs (sans argument) pour ajouter l'obs à la bonne place chronologique

2) pour trier une trace par ordre chronologique
   -> sort pour des traces courtes (moins d'un millier de points)
   -> sortRadix sinon

Rq1 : si les traces ont de fortes chances d'être déjà triées, en théorie mieux vaut utiliser sort que sortRadix, bien que je n'ai pas observé de différence significative dans le temps de calcul sur des traces de tailles raisonnable.

Rq2 : pour construire une longue trace de manière incrémentale, mieux vaut construire la trace dans le désordre (1) avec addObs, puis trier (2) toute la trace d'un coup avec sort ou sortRadix.



les NAN ne sont pas des erreurs mais des trous dans les données
