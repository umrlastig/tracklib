

Smoothing 
==============

Smoothing : toutes les méthodes qui sous-échantillonnent ou sur-échantillonnent (ou éventuellement conservent l'échantillonnage initial) la trace avec changement potentiel de coordonnées sur les points conservés.
    - THIN SPLINE
    - B-SPLINE
    - FILTERING
    - CONVOLUTION
    - WAVELET
    - GAUSSIAN  PROCESS
La fonction "mère" de smoothing pourrait être smooth(track, delta, algo, mode, param) avec :
   - track : la trace à traiter
   - delta : la résolution spatiale ou temporelle souhaitée en sortie du traitement
   - algo : l'un des 6 algos ci-dessus
   - mode : comme d'habitude, SPATIAL ou TEMPORAL
   - param : un paramètre de filtrage dépendant de la méthode (peut-être qu'il faudra 2 paramètres)