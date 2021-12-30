# ----------------------------------------------------------------------------------------
# Script to ensure retrocompatibility of Tracklib (nominally from v3.8 to v2.7 or more)
# ----------------------------------------------------------------------------------------
# Removes Literal import from typing (python v3.8)
# Removes __future__import (python v3.7)
# Removes typing annotation in function inputs/outputs
# The main directory 'tracklib' is renames 'tracklib_old' and a new 'tracklib' directory 
# (compliable with python version 2.7 or later) is created. 
# ----------------------------------------------------------------------------------------
# Warning: all functions using typing annotations should be defined on a single line!
# ----------------------------------------------------------------------------------------


import os
import re
import shutil
import random
from time import sleep

print("------------------------------------------------------------")
print("Building python v2.7-compliable version of Tracklib")
print("------------------------------------------------------------")


root = 'tracklib'
output_folder = 'tracklib_retro'

if os.path.exists(output_folder):
	shutil.rmtree(output_folder)
	print("Removing directory:", output_folder)
os.mkdir(output_folder)
print("Creating directory:", output_folder)

F1 = os.listdir(root)

def rm_csv_quotes(chaine, char = '+'):
	boolean = 0
	string_list = list(chaine)
	for i in range(len(string_list)):
		if string_list[i] == '[':
			boolean += 1
		if string_list[i] == ']':
			boolean -= 1
		if (boolean > 0) and (string_list[i] == ','):
			string_list[i] = char
		chaine = "".join(string_list).replace("[", "").replace("]","")
	return(chaine)

nb_lines = 0

for f1 in F1:
	path = root + "/" + f1
	if os.path.isfile(path):
		continue
	F2 = os.listdir(path)
	os.mkdir(output_folder + "/" + f1)
	for f2 in F2:
		path = root + "/" + f1 + "/" + f2
		path_output = output_folder + "/" + f1 + "/" + f2
		if not os.path.isfile(path):
			continue
		if "__" in path:
			continue
		print("Creating file", path_output)
		fin = open(path, "r")
		fout = open(path_output, "w")
		L = fin.readlines()
		sleep(0.1*random.random())
		for line in L:
			if "__future__" in line:
				print("  Removing: import __future")
				line = "#" + line
			if "import" in line and  "typing" in line and "Literal" in line:
				print("  Removing: import Literal")
				line = "#" + line
			if "->" in line and ":" in line and ")" in line:
				line = line.split("->")[0].rstrip()+":\r\n"
				print("  Removing: function output typing")
			if line.lstrip().startswith("def") and "(" in line and ")" in line:
				args = line.split("(")[1].split(")")[0]
				if ":" in args:
					ARGS = rm_csv_quotes(args).split(",")
					for i in range(len(ARGS)):
						if ":" in ARGS[i]:
							part1 = ARGS[i].split(":")[0]
							part2 = ARGS[i].split(":")[1]
							ARGS[i] = part1
							if "=" in part2:
								ARGS[i] = ARGS[i] + " =" + part2.split("=")[1]
					print("  Removing: function ["+line.lstrip().split("(")[0][:]+"] input typing")
					line = line.split("(")[0]+"("+(",".join(ARGS))+")"+line.split(")")[1]
			fout.write(line)
		print("  ->", len(L), "line(s) processed")
		nb_lines += len(L)
		fin.close()
		fout.close()

		
os.rename(root, root+"_old");   print("Renaming directory", root, "to", root+"_old")
os.rename(output_folder, root); print("Renaming directory", output_folder, "to", root)

print("------------------------------------------------------------")
print("Done: ", nb_lines, "lines processed. Directory [tracklib] created")
print("------------------------------------------------------------")