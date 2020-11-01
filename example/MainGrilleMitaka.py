#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import tracklib.core.Grid as g
import tracklib.io.FileReader as fileReader
import tracklib.algo.AlgoAF as algo
import tracklib.util.CellOperator as cellop


PATH = '/home/marie-dominique/PROJET/FINI/MITAKA/DATA/mitaka/extrait'
#PATH = '/home/marie-dominique/PROJET/FINI/MITAKA/DATA/mitaka/complet2'
TRACES = fileReader.FileReader.readFromFiles(PATH, 1, 2, 3)

# ============================================================================
#  Traitement sur les traces : on en supprime
for (idx, trace) in enumerate(TRACES):
	if trace.size() > 0:
		# On découpe la trace si distance entre 2 points > 1000m
		trace.addAnalyticalFeature(algo.ds)
		trace.segmentation(["ds"], "saut1000m", [1000])
		TRACES_SPLIT = trace.split_segmentation("saut1000m")
		if len(TRACES_SPLIT) <= 0:
			if trace.size() <= 10:
				TRACES.remove(trace)
		else:
			TRACES.remove(trace)
			# ajouter les traces splittees
			for split_trace in TRACES_SPLIT:
				TRACES.append(split_trace)
	else:
		TRACES.remove(trace)
		
	if idx > 50:
		break
	
	
# ============================================================================
#   Grille
Xmin = 366280.496639618
Xmax = 372810.04499373
Ymin = 3946800.20595923
Ymax = 3953500.99610818
    
XSize = Xmax - Xmin
YSize = Ymax - Ymin
PixelSize = 5

#  Construction de la grille
grille = g.Grid(Xmin, Ymin, XSize, YSize, PixelSize)

# Summarize
af_algos = [algo.speed, algo.orientation, algo.stop_point_with_acceleration_criteria]
cell_operators = [cellop.co_avg, cellop.co_dominant, cellop.co_sum]
grille.addAnalyticalFunctionForSummarize(TRACES, af_algos, cell_operators)

# Plot des indicateurs
grille.plot(algo.orientation, cellop.co_dominant)
grille.plot(algo.speed, cellop.co_avg)
grille.plot(algo.stop_point_with_acceleration_criteria, cellop.co_sum)

#  Vers un fichier ASC
path = "../data/resultat/"
#grille.exportToAsc(path, utils.orientation, utils.co_dominant)
#grille.exportToAsc(path, utils.speed, utils.co_avg)


grille.plotImage3AF(af_algos, cell_operators)
