

Interpolation 
==============

Interpolation : toutes les méthodes qui sous-échantillonnent ou sur-échantillonnent la trace sans changement de coordonnées sur les points conservés.
    - LINEAR
    - THIN SPLINE
    - GAUSSIAN  PROCESS
La fonction "mère" de interpolation pourrait être resample(track, delta, algo, mode) avec :
   - track : la trace à traiter
   - delta : la résolution spatiale ou temporelle souhaitée en sortie du traitement
   - algo : l'un des 3 algos ci-dessus
   - mode : comme d'habitude, SPATIAL ou TEMPORAL

