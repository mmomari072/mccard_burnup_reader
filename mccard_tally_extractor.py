# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 09:42:48 2024

@author: mohammed.omari
"""
import argparse 
import sys
import pathlib

sys.path.append("H:\MyCodes\McCARD\Flux_Extractor\venv\Lib\site-packages")

MSG="""
================================================================================\n\r
This code was developed to easly extract the flux data from McCARD burnup file
and save them into excel file

Code Name        :  McCARD Flux Extracter
Version          :  V0.1
Created on       : Feb 18 2024
Created by       : Eng. Mohammad OMARI
Department       : Nuclear Safety and Licensing
Institute        : Jordan Research and Training Reactor
===============================================================================
"""
print(MSG)
parser=argparse.ArgumentParser(epilog=MSG)
parser.add_argument("-i", "--input_file", dest="input_file",
                    #default=r"H:\SIMAULATIONS\Source_Term_Dimona\HOTSPOT\General_Explosion\Current.hot",
                    help="McCARD burnup file", metavar="FILE",
                    default="fluxinenb_0")
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
parser.add_argument("-f", "--filter",
                    #action="HotSpot Output File Name", 
                    dest="filter_val", default="*",
                    help="filter_the_needed_cells")

# parser.add_argument("-r", "--results_file",
#                     #action="HotSpot Output File Name", 
#                     dest="results_file", default="omari.csv",
#                     help="Table Contains the doses at destances")

# parser.add_argument("-hp", "--hotspot_path",
#                     #action="HotSpot Output File Name", 
#                     dest="hotspot_path", default=r"C:\Program Files (x86)\HotSpot3.1.2\HotSpot_v3_1_2.exe",
#                     help="Hotspot.exe Path")


args = parser.parse_args()

def file_extension(filename:str="omari.txt.csv"):
    return pathlib.Path(filename).suffix

def Diff(X,*VAR):
    if len(VAR)==0:
        return [X[i]-X[i-1] for i in range(1,len(X))]
    elif len(VAR)==1:
        DX=Diff(X)
        DY=Diff(VAR[0])
        return [dy/dx for dx,dy in zip(DX,DY)]
    else:
        pass

def MidPoint(X):
    return [0.5*(X[i]+X[i-1]) for i in range(1,len(X))]


class str2num:
    def __init__(self,word=None,Type=float):
        self.word= word
        self.type = Type
        self.coverted = None
    def covert(self):
        try:
            self.converted = self.type(self.word)
        except:
            self.converted = None
        return self.converted
    def isType(self,**k):
        return isinstance(self.covert(), self.type)
            
def find_value_of_x(S:str="x=1 y=2;z=3",*Vars):
    SS=S
    for c in [",",";","?","!","="]:
        SS=SS.replace(c, "  ")
    tmp=[x for x in SS.split() if x!=""]
    #print(tmp)
    A={}
    for v in Vars:
        if SS.find(v)>=0:
            A[v]=None
            tmp2=[x for x in SS.split(v) if True]
            if len(tmp2)>1:
                tmp3=[x for x in tmp2[1].split() if x!='']
                A[v]=tmp3[0] if len(tmp3)>0 else None                
            #break
    return A

class _db :
    def __init__(self):
        self.attrinutes = {}
        

class cell_tally:
    _keys_map={
        "grp":"group_id",
        "Upper energy[MeV]":"UGEnergy",
        "Flux":"Flux",
        "Rel. Err":"RelErr"
        }
    
    def __init__(self,name=None,volume=None):
        self.name:str = name
        self.volume:float = volume
        self.group_id = []
        self.UGEnergy=[]
        self.Flux = []
        self.RelErr =[]
    def append(self,line:str="               grp=  1   Upper energy[MeV]= 1.20000e-11   Flux                  = 3.91699e-13   Rel. Err =   1.00000"):
        var = find_value_of_x(line,*self._keys_map)
        for k,val in var.items():
            self[k]=self[k]+[str2num(val,float).covert() if k not in ["grp","group_id"] else 
                             str2num(val,int).covert()]
        return self
    
    def __setitem__(self, name, value):
        if name in self._keys_map:
            self.__dict__[self._keys_map[name]]=value
        elif name in self.__dict__:
            self.__dict__[name]=value
            
    def __getitem__(self, name):
        if name in self._keys_map:
            #print(name)
            return self.__dict__[self._keys_map[name]]
        elif name in self.__dict__:
            return self.__dict__[name]
        
    def get_db(self):
        
        import pandas as pd

        df = pd.DataFrame(data={k:v for k,v in self.__dict__.items() if k in self._keys_map.values()})
        E_range =[0]+ list(df.UGEnergy)

        dE,Emid = Diff(E_range),MidPoint(E_range)
        dPhi_over_dE=[dphi/de for dphi,de in zip( df["Flux"],dE)]
        df["dE"]=dE
        df["Emid"]=Emid
        df["dPhi/dE"]=dPhi_over_dE    
        return df
    def get_db_ascii(self):
        data={k:v for k,v in self.__dict__.items() if k in self._keys_map.values()}
        data["cell_name"]=[self.name  for _ in range(len(self))]
        
        A=[]
        H = ["cell_name"]+list(self._keys_map.values())
        for i in range(len(self)):
            tmp =[]
            for att in H:
                tmp.append(data[att][i])
            A.append(tmp)
        return A

                
        
            
        
    def __len__(self):
        return min([len(self.__dict__[i]) for i in self._keys_map.values()])
        
        
        
        
        

def read_file(filename="fluxinenb_0"):
    with open(filename,"r") as fid:
        A= [l.strip() for l in fid]
        print(f"{len(A)} line(s) has been read !")
        return A
    print(f"Nothning has been read !")
    return []


class mccard_tally:
    def __init__(self):
        self.filename = None
        self.cells = {}
        self.raw_data = []
        
        self.__searched_cells = []
    def get_tallies(self,output_file:list[str]=[]):
        print("Processing Data ..... ",end="")
        output_file = self.raw_data if len(self.raw_data)>0 else output_file
        CELLS = {}
        IS_FLUX_DATA_FOUND=False
        for l in output_file:
            if l.find("User-defined Tally Output")>=0 and not IS_FLUX_DATA_FOUND:
                IS_FLUX_DATA_FOUND = True
                continue
            elif l.find("* Total CPU time")>=0:
                IS_FLUX_DATA_FOUND = False
            if len(l.strip())==0:
                continue
                pass
            if IS_FLUX_DATA_FOUND:
                if l.find("Cell Name")>=0:
                    tmp=[x.strip() for x in l.split()]
                    cell_name = tmp[2]
                    cell_volume = tmp[4]
                    cell = cell_tally(cell_name,cell_volume)
                    CELLS[cell_name]=cell
                    continue
                #print(all([l.find(w)>=0 for w in cell_tally._keys_map.keys() ]),l,cell_tally._keys_map.keys())
                if all([l.find(w)>=0 for w in cell_tally._keys_map.keys() ]):
                    CELLS[cell_name].append(l)
        self.cells=CELLS
        print("[DONE]")
        return self
    
    def read_file(self,filename=""):
        print(f"Reading file [FILENAME = {filename}] ........ ",end = "")
        self.filename = filename
        self.raw_data = read_file(filename)
        print("[DONE]")
        return self
    
    def find(self,*key):
        #self.__searched_cells = []
        for c in self.cells.keys():
            for k in key:
                if c.find(k)<0:
                    continue
                if c in self.__searched_cells:
                    pass
                else:
                    self.__searched_cells.append(c)
        return self
    
    def reset_find(self):
        self.__searched_cells = []
        return self
    
    def export_to_xls(self,filename="test.xlsx",is_verbose=False):
        import pandas as pd

        print(f"Exporting to [FILENAME = {filename}] ........ ",end = "\n")

        index = self.__searched_cells if len(self.__searched_cells)>0 else list(self.cells.keys())
        cells = dict(Cell_Alias=[],RealName=[])
        writer = pd.ExcelWriter(filename,engine='xlsxwriter')   
        start_row=0
        cell_id = 0
        for i,cell in enumerate(index):
            cells["Cell_Alias"],cell_id=cells["Cell_Alias"]+[f"cell_{cell_id}"],cell_id+1
            cells[f"RealName"]+=[cell]
            tmp=self[cell].get_db()
            cols = [x for x in tmp.columns]
            #print(cols)
            tmp["Cell_Name"]=cells["Cell_Alias"][-1]
            if is_verbose:
                print(f"\rEporting .... {100*(i+1)/len(index):6.2f} % [{i+1:5}:{len(index):5}] [current cell = {cell}]",end="")
            
            tmp.to_excel(writer,"fluxes",startcol=0,startrow=start_row,
                         header=True if start_row==0 else False,
                         index=False,
                         columns=["Cell_Name"]+cols+["dE","Emid","dPhi/dE"]
                         
                         
                         )

            start_row+=len(tmp.index)+0
        print("[DONE]")

        df1 = pd.DataFrame(data=cells)
        df1.to_excel(writer,"Cell_Dict")
        print("Stroring the data ........",end="")
        writer.save()
        print("[DONE]")
        return self
    

    
    def export_to_csv(self,filename="test.csv",is_verbose=False):
        index = self.__searched_cells if len(self.__searched_cells)>0 else list(self.cells.keys())
        print(f"Exporting to [FILENAME = {filename}] ........ ",end = "\n")

        HEADER =["#","cell_name"]+ list(cell_tally._keys_map.keys())
        with open(filename,"w") as fid:
            print(",".join(HEADER),file=fid)
            j=1;
            for i,cell in enumerate(index):
                if is_verbose:
                    print(f"\rEporting .... {100*(i+1)/len(index):6.2f} % [{i+1:5}:{len(index):5}] [current cell = {cell}]",end="")
                tmp=self[cell].get_db_ascii()
                for line in tmp:
                    print(",".join([str(j)]+[str(x) for x in line]),file=fid)
                    j+=1
                
        return self
    
    def export(self,filename="test.xlsx",is_verbose=False):
        FileType = file_extension(filename)
        cases={"txt":"PASS",
               "xlsx":"export_to_xls",
               "xls":"export_to_xls",
               "csv":"export_to_csv",
               }
        for case,fun in cases.items():
            if FileType.find(case)>=0:
                print(fun,case)
                self.__getattribute__(fun)(filename,is_verbose)
                
    
    def PASS(self):
        pass
        
        
    def __getitem__(self,name):
        return self.cells[name]
        

if __name__=="__main__":
    #from matplotlib import pyplot as plt
    I_filename = args.input_file
    O_filename = args.output_file
    Is_verbose = args.is_verbose
    filter_val = args.filter_val
    
    print(I_filename,
          filter_val,
          Is_verbose,
          O_filename)
    #exit()
    
    
    #find_value_of_x("               grp=  1   Upper energy[MeV]= 1.20000e-11   Flux                  = 3.91699e-13   Rel. Err =   1.00000","Flux")
    #A=cell_tally().append()

    A=mccard_tally()
    
    A.read_file(I_filename)
    
    A.get_tallies()
    
    # A.find(filter_val) # not supported yet
    #A.export_to_csv()
    A.export(O_filename,Is_verbose)
    
    # #aa=A.cells["AsmA3>Hole>capsule>capsule3>hol_inter>hol_inter6"].get_db()
    
    # index=aa["dPhi/dE"]>1e-10
    # plt.loglog(aa["Emid"][index],aa["dPhi/dE"][index]),plt.grid(True, which="both", ls="-")
    # plt.show()