# -*- coding: utf-8 -*-
print("""
Created on: Mon Nov  6 10:41:55 2023
Author    : Mohammed Omari
Purpose   : This codes is aimed to facilitated the data processing of McCARD
            Burnup data.
"""
)
#from glob import glob
from sys import argv
HEADER=["Nuclide","CX File",
        "Number Density","Gram Density",
        "Number","Mass"]
_Nuclide={x:None for x in HEADER}

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
        data=read_file(filename)
        STEPS[step]=extract_data_from_case(data)
        tmp_len = len(STEPS[step])
        STEPS[step]["FileName"]=filename
        print(f"\rImporting {100*(step/(number_of_steps-1)):0.2f}",end='')
    print("")
    return STEPS

def Export_data_to_CSV(filename="omari1.csv",full_data={}):
    LINES=[]
    for step,data in full_data.items():
        #print (tmp)
        src_filename = data["FileName"]
        for cell,nuclides in data.items():
            if isinstance(nuclides,str):
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
    print(argv)
    filename_prefix = argv[1] if len(argv)>1 else input("Enter the Burnup file prefix name [e.g.ag3necf_] :")
    number_of_steps = int(argv[2]) if len(argv)>2 else (input("Enter the Burnup Steps  :"))
    export_filename = argv[3] if len(argv)>3 else input("Enter the Burnup file prefix name [e.g. output.csv] :")
    c=get_data_from_all(filename_prefix,number_of_steps)
    d=Export_data_to_CSV(filename=export_filename,full_data=c)