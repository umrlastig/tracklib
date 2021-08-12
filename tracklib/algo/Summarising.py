# ---------------------------- Cell Operator ----------------------------------
# Operator to aggregate features:
#  - 
# -----------------------------------------------------------------------------

import tracklib.core.Utils as utils

def co_sum(tarray):
	tarray = utils.listify(tarray)
	somme = 0
	for i in range(len(tarray)):
		val = tarray[i]
		if utils.isnan(val):
			continue
		somme += val
	return somme

def co_min (tarray):
	tarray = utils.listify(tarray)
	if len(tarray) <= 0:
		return utils.NAN
	min = tarray[0]
	for i in range(1, len(tarray)):
		val = tarray[i]
		if utils.isnan(val):
			continue
		if val < min:
			min = val
	return min
	
def co_max (tarray):
	tarray = utils.listify(tarray)
	if len(tarray) <= 0:
		return utils.NAN
	max = tarray[0]
	for i in range(1, len(tarray)):
		val = tarray[i]
		if utils.isnan(val):
			continue
		if val > max:
			max = val
	return max

def co_count(tarray):
	tarray = utils.listify(tarray)
	count = 0
	for i in range(len(tarray)):
		val = tarray[i]
		if utils.isnan(val):
			continue
		count += 1
	return count

def co_avg (tarray):
	tarray = utils.listify(tarray)
	if len(tarray) <= 0:
		return utils.NAN
	mean = 0		
	count = 0
	for i in range(len(tarray)):
		val = tarray[i]
		if utils.isnan(val):
			continue
		count += 1
		mean += val
	if count == 0:
		return utils.NAN
	return mean/count

def co_dominant(tarray):
	tarray = utils.listify(tarray)
	''' Most frequent value '''
	if len(tarray) <= 0:
		return utils.NAN
	
	# Dico : clé - nb occurence
	cles_count_dictionnary = {}
	
	# On alimente le dictionnaire
	for val in tarray:
		if val not in cles_count_dictionnary:
			cles_count_dictionnary[val] = 1
		else:
			cles_count_dictionnary[val] += 1

	# On cherche le plus fréquent i.e. celui qui a le max d'occurence 
	nbocc = 0
	dominant_value = ''
	for val in cles_count_dictionnary:
		if cles_count_dictionnary[val] > nbocc:
			nbocc = cles_count_dictionnary[val]
			dominant_value = val
	return dominant_value
					
def co_median (tarray):
	tarray = utils.listify(tarray)
	if len(tarray) <= 0:
		return utils.NAN
	
	n = len(tarray)
	# on tri le tableau pour trouver le milieu
	tab_sort = []
	for i in range(n):
		valmin = tarray[0]
		# Recherche du min
		for val in tarray:
			if val <= valmin:
				valmin = val
		tarray.remove(valmin);
		tab_sort.append(valmin);
        
	# Gestion n pair/impair  
	if n%2 == 1:
		mediane = tab_sort[(n-1)/2]
	else:
		mediane = 0.5*(tab_sort[n/2]+tab_sort[n/2-1])
        
	return mediane



def summarize(grid):
    
    print ('TODO')


