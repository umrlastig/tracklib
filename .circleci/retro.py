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
import sys
import shutil
import random
from time import sleep


if sys.argv[-1] in ["--help", "-h", "--h", "-help"]:
    print("-------------------------------------------------------------")
    print("TRACKLIB RETRO-COMPATIBILITY SCRIPT")
    print("-------------------------------------------------------------")
    print("-m  Mode: direction of transformation")
    print("    down  :   Python v3.8 to v2.7 downgrading [default] ")
    print("    up    :   Python v2.7 to v3.8 upgrading")
    print("-r  Reversibility: (for mode 'down')")
    print("    0     :   Non-reversible downgrading")
    print("    1     :   Reversible downgrading [default]") 
    print("-i  Input folder [default: 'tracklib']")    
    print("-o  Output folder [default: 'tracklib27' or 'tracklib38']")    
    print("-------------------------------------------------------------")
    sys.exit()
    
    
ARG_NAME = sys.argv[1::2]
ARG_VALUE = sys.argv[2::2]
if (not (len(ARG_NAME) == len(ARG_VALUE))) or (len(ARG_NAME) > 3):
    print("Error in arguments: see --help for usage")
    sys.exit()
    
mod = 'down'; rev = '1'; input_folder = 'tracklib'; output_folder = -1
    
for i in range(len(ARG_NAME)):    
    if ARG_NAME[i].rstrip().lstrip() == "-i":
        input_folder = ARG_VALUE[i].rstrip().lstrip()
    if ARG_NAME[i].rstrip().lstrip() == "-o":
        output_folder = ARG_VALUE[i].rstrip().lstrip()
    if ARG_NAME[i].rstrip().lstrip() == "-m":
        mod = ARG_VALUE[i].rstrip().lstrip()
    if ARG_NAME[i].rstrip().lstrip() == "-r":
        rev = ARG_VALUE[i].rstrip().lstrip()
        if (mod == 'up') and (rev == '0'):
            print("Error: upgrading is always reversible: see --help for usage")
            sys.exit()

if output_folder == -1:
    if mod == 'down':
        output_folder = 'tracklib27'
    if mod == 'up':
        output_folder = 'tracklib38'
rev = (rev == '1')
    
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
        
def upgrade(rev):

    print("-------------------------------------------------------------")
    print("Building python v3.8-compliable version of Tracklib")
    print("-------------------------------------------------------------")
    
    root = input_folder
    output_folder_temp = 'tracklib_retro'
    
    if os.path.exists(output_folder_temp):
        shutil.rmtree(output_folder_temp)
        print("Removing directory:", output_folder_temp)
    os.mkdir(output_folder_temp)
    print("Creating directory:", output_folder_temp)
    
    F1 = os.listdir(root)

    nb_lines = 0

    for f1 in F1:
        path = root + "/" + f1
        if os.path.isfile(path):
            continue
        F2 = os.listdir(path)
        os.mkdir(output_folder_temp + "/" + f1)
        for f2 in F2:
            path = root + "/" + f1 + "/" + f2
            path_output = output_folder_temp + "/" + f1 + "/" + f2
            if not os.path.isfile(path):
                continue
            if "__" in path:
                continue
            print("Creating file", path_output)
            fin = open(path, "r")
            fout = open(path_output, "w")
            L = fin.readlines()
            sleep(0.1*random.random())
            uncom = 0; rem = 0
            for line in L:
                if "#RETRO: TO UNCOMMENT" in line:
                    uncom += 1
                    line = line[1:].replace("#RETRO: TO UNCOMMENT", "")
                if "#RETRO: TO REMOVE" in line:
                    rem += 1
                    continue
                fout.write(line)
            print("  ->", len(L), "line(s) processed:")
            print("        "+str(rem)+ " line(s) removed")
            print("        "+str(uncom) + " line(s) uncommented")
            nb_lines += len(L)
            fin.close()
            fout.close()
            
         
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
        print("Removing directory:", output_folder)
    os.rename(output_folder_temp, output_folder);
    print("Renaming directory", output_folder_temp, "to", output_folder)


    print("-------------------------------------------------------------")
    print("Done: ", nb_lines, "lines processed. Folder ["+output_folder+"] created")
    print("-------------------------------------------------------------")
    
def downgrade(rev):

    print("-------------------------------------------------------------")
    print("Building python v2.7-compliable version of Tracklib")
    print("-------------------------------------------------------------")

    root = input_folder
    output_folder_temp = 'tracklib_retro'

    if os.path.exists(output_folder_temp):
        shutil.rmtree(output_folder_temp)
        print("Removing directory:", output_folder_temp)
    os.mkdir(output_folder_temp)
    print("Creating directory:", output_folder_temp)

    F1 = os.listdir(root)

    nb_lines = 0

    for f1 in F1:
        path = root + "/" + f1
        if os.path.isfile(path):
            fin = open(path, "r")
            fout = open(output_folder_temp + "/" + f1, "w")
            L = fin.readlines()
            sleep(0.1*random.random())
            for line in L:
                fout.write(line)
            fin.close()
            fout.close()
            continue
        F2 = os.listdir(path)
        os.mkdir(output_folder_temp + "/" + f1)
        for f2 in F2:
            path = root + "/" + f1 + "/" + f2
            path_output = output_folder_temp + "/" + f1 + "/" + f2
            if not os.path.isfile(path):
                continue
            #if "__" in path:
            #    continue
            print("Creating file", path_output)
            fin = open(path, "r")
            fout = open(path_output, "w")
            L = fin.readlines()
            sleep(0.1*random.random())
            for line in L:
                function_flag = False
                modif_flag = False
                import_flag = False
                saved_line =  "#" + line
                if "__future__" in line:
                    print("  Removing: import __future")
                    line = "#" + line
                    modif_flag = True
                    import_flag = True
                if "import" in line and  "typing" in line:
                    print("  Removing: import typing")
                    line = "#" + line
                    modif_flag = True
                    import_flag = True
                if "->" in line and ":" in line and ")" in line:
                    line = line.split("->")[0].rstrip()+":\n"
                    print("  Removing: function output typing")
                    function_flag = True
                    modif_flag = True
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
                        function_flag = True
                        modif_flag = True
                if modif_flag:
                    line = line[:-1] 
                    if rev:
                        if import_flag:
                            line = line + "   #RETRO: TO UNCOMMENT\n"
                        else:
                            line = line + "   #RETRO: TO REMOVE\n"
                if "Re: float =" in line:
                    line = line.replace("Re: float =", "Re = ")
                if "Fe: float =" in line:
                    line = line.replace("Fe: float =", "Fe = ")
                if "margin: float =" in line:
                    line = line.replace("margin: float =", "margin = ")
                if "verbose: bool =" in line:
                    line = line.replace("verbose: bool =", "verbose = ")
                if "collection: Union[Bbox, TrackCollection]" in line:
                    line = line.replace("collection: Union[Bbox, TrackCollection]", "collection")
                if "coord: Union[ENUCoords, ECEFCoords, GeoCoords]" in line:
                    line = line.replace("coord: Union[ENUCoords, ECEFCoords, GeoCoords]", "coord: ")
                if "-> Union[tuple[float, float], None]:" in line:
                    line = line.replace("-> Union[tuple[float, float], None]:", ": ")
                if "base: bool = True" in line:
                    line = line.replace("base: bool = True", "base = True")
                    
                fout.write(line)
                if function_flag and rev:
                    fout.write(saved_line[:-1] + "   #RETRO: TO UNCOMMENT\n")
            print("  ->", len(L), "line(s) processed")
            nb_lines += len(L)
            fin.close()
            fout.close()
        
 
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
        print("Removing directory:", output_folder)
    os.rename(output_folder_temp, output_folder);
    print("Renaming directory", output_folder_temp, "to", output_folder)


    print("-------------------------------------------------------------")
    print("Done: ", nb_lines, "lines processed. Folder ["+output_folder+"] created")
    print("-------------------------------------------------------------")
    

if mod == 'down':
    downgrade(rev)
    
if mod == 'up':
    upgrade(rev)
