# -*- coding: utf-8 -*-
("""
Created on: Mon Nov  6 10:41:55 2023
Author    : Mohammed Omari
Purpose   : This codes is aimed to facilitated the data processing of McCARD
            Burnup data.
"""
)
#from glob import glob
from sys import argv,path
import argparse 
import sys
import pathlib
import os.path


HEADER=["Nuclide","CX File",
        "Number Density","Gram Density",
        "Number","Mass"]
_Nuclide={x:None for x in HEADER}

path.append("H:\MyCodes\McCARD\Flux_Extractor\venv\Lib\site-packages")

MSG="""
================================================================================\n\r
This code was developed to easly extract the isotopic envitory data from McCARD burnup 
files and save them into excel file

Code Name        : McCARD BURNUP DATA Extracter
Version          : V0.2
Created on       : Mon Nov  6 10:41:55 2023
Created by       : Eng. Mohammad OMARI
Updated on       : Mar 03 2024
Department       : Nuclear Safety and Licensing
Institute        : Jordan Research and Training Reactor
===============================================================================
"""
print(MSG)
parser=argparse.ArgumentParser(epilog=MSG)
parser.add_argument("-ip", "--input_file_prefix", dest="input_file_prefix",
                    #default=r"H:\SIMAULATIONS\Source_Term_Dimona\HOTSPOT\General_Explosion\Current.hot",
                    help="McCARD burnup file name prefix", metavar="FILE",
                    default="fluxinenb_")
parser.add_argument("-q", "--quiet",
                    #action="store_false", dest="verbose", default=True,
                    help="don't print status messages to stdout")
parser.add_argument("-o", "--output_file",
                    #action="HotSpot Output File Name", 
                    dest="output_file", default="omari.csv",
                    help="Flux Tally Output File Name")
parser.add_argument("-v","--verbose",
                    dest="is_verbose",default=True,type=bool,
                    action=argparse.BooleanOptionalAction,
                    help="Verbose Progress Report")
parser.add_argument("-n","--number_of_steps",
                    dest="number_of_steps",default=0,type=int,
                    help="Number of burnup steps. note you need to consider number <= accutal number")
parser.add_argument("-f", "--filter",
                    #action="HotSpot Output File Name", 
                    dest="filter_val", default="*",
                    help="filter_the_needed_cells: NOTE-> NOT FUNCTIONING ")
parser.add_argument("-C","--cell-file", dest="cell_file",
                    default=None,type=str,help="load options file"
                    )

args = parser.parse_args()

def import_cell_names(filename:str="cells.lst"):
    if filename is None:
        return []
    with open(filename,"r") as fid:
        return [x.strip() for x in fid]
    return ["*"]

def get_file_names():
    pass

def read_file(filename="ag3necf_0"):
    with open(filename,"r") as fid:
        return [x.strip() for x in fid]
    return None  

def extract_data_from_case(file_str_list=[]):
    cells={}
    LENGTH=len(file_str_list)
    i=0
    while i<LENGTH:
        line=file_str_list[i]
        if line.find("Flux Conversion Factor")>=0:
            break
        if line.find("Cell Name:")>=0:
            #print(line)
            cell_name=[x for x in line.strip().split() if x!=''][2]
            #print(cell_name)
            cells[cell_name]={}
            RECORDING=False
            while file_str_list[i].find("Total")<0:
                if not RECORDING:
                    if file_str_list[i].find("Nuclide")>=0:
                        RECORDING=True
                    i+=1
                    continue
                line=file_str_list[i]
                tmp = [x for x in line.split() if x!='']
                Nuclides={}
                for j,att in enumerate(HEADER):
                    Nuclides[att]=tmp[j]
                cells[cell_name][tmp[0]]=Nuclides
                i+=1
        i+=1
    return cells
            
def get_data_from_all(filename_prefix="ag3necf_", number_of_steps=25):
    STEPS={}
    for step in range(number_of_steps):
        filename=f"{filename_prefix}{step}"
        if os.path.isfile(filename):
            data=read_file(filename)
            STEPS[step]=extract_data_from_case(data)
            tmp_len = len(STEPS[step])
            STEPS[step]["FileName"]=filename
        else:
            print(f"\nWorning! this file is not found! {filename}. Skipping this file")
        print(f"\rImporting {100*(step/(number_of_steps-1)):0.2f}",end='')
    print("")
    return STEPS

def is_in(x:str,values:list[str]=[]):
    if "*" in values:
        return True
    conds=[]
    for xx in values:
        conds.append(x.find(xx)>=0)
    return sum(conds)>0
        

def Export_data_to_CSV(filename="omari1.csv",full_data={},filtered_cells:list[str]=[]):
    LINES=[]
    for step,data in full_data.items():

        #print (tmp)
        src_filename = data["FileName"]
        for cell,nuclides in data.items():
            if is_in(cell,filtered_cells):
                #print(cell,filtered_cells)
                pass
            else:
                continue
            if isinstance(nuclides,str):
                print("I forget why I added this condiction ...",nuclides)
                continue
            for nuc,info in nuclides.items():
                d=[src_filename,step,cell]
                for i,header in enumerate(HEADER):
                    d.append(info[header])
                    
                #print(d,file=fid)
                LINES.append(d)
    with open(filename,"w") as fid:
        print(f"SR_filename,step_id,Cell_Name,ZAID,XS-FILE,Number Density,Gram Density,Number,Mass",file=fid)
        i=0
        for line in LINES:
            print(",".join([str(x) for x in line]).replace("'",""),file=fid)
            i+=1
            if i%100==0:
                print(f"\rExporting {100*i/len(LINES):0.2f}",end='')
        else:
            print(f"\rExporting {100*i/len(LINES):0.2f}",end='')
                    
                        
                
        

if __name__=="__main__":
    # ###################################################
    filename_prefix=args.input_file_prefix
    if filename_prefix is None or filename_prefix=='':
        filename_prefix = input("Enter the Burnup file prefix name [e.g.ag3necf_] :")
    # ###################################################    
    number_of_steps = args.number_of_steps
    if number_of_steps<0:
        number_of_steps=int(input("Enter the Burnup Steps  :"))
    # ###################################################
    export_filename = args.output_file
    filtered_cells = import_cell_names(args.cell_file) if args.cell_file is not None else ["*"]
     
    
    if 0:
        filename_prefix=r"C:\Users\mohammed.omari\Desktop\criticatility new saftey clad\const flux\ag3necf_"
        number_of_steps=50
        export_filename = "yousef_omari.csv"
        filtered_cells=["Clad_01B"]
    c=get_data_from_all(filename_prefix,number_of_steps)
    d=Export_data_to_CSV(filename=export_filename,full_data=c,filtered_cells=filtered_cells)