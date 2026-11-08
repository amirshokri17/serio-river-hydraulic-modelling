"""
Serio River - River2D 2D post-processing and 1D steady comparison.

Required input files (can be anywhere under the script folder):
  mesh50_sim1.CDG
  cross section data_2D new.xlsx
  Serio_Benchmark_Hydraulic_Results.csv

Optional:
  Serio_Unsteady_Analysis_Results.xlsx

Outputs:
  representative-section CSV profiles and a summary CSV.

Method:
  - exact georeferenced axes from S08/S10/S12/S16/S18 sheets
  - 2 m sampling interval
  - linear interpolation on River2D triangular mesh
  - wet point: h > 0.02 m
  - WSE = bed + h
  - V_perp = V * sin(alpha-beta)
      alpha = atan2(qy,qx)
      beta  = atan2(y2-y1,x2-x1)
"""

from pathlib import Path
import csv, math, re, zipfile
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.tri as mtri

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "postprocessed"
OUT.mkdir(exist_ok=True)

SECTIONS = ["s08","s10","s12","s16","s18"]
SPACING = 2.0
WET_DEPTH = 0.02
ACTIVE_VPERP = 0.001

def find_file(name):
    hits = list(ROOT.rglob(name))
    if not hits:
        raise FileNotFoundError(f"Could not find {name} under {ROOT}")
    return hits[0]

def read_xlsx_values(path):
    ns={"a":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as z:
        shared=[]
        if "xl/sharedStrings.xml" in z.namelist():
            root=ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("a:si",ns):
                shared.append("".join(t.text or "" for t in si.iter(
                    "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")))
        wb=ET.fromstring(z.read("xl/workbook.xml"))
        rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        relmap={r.attrib["Id"]:r.attrib["Target"] for r in rels}
        out={}
        for sh in wb.find("a:sheets",ns):
            name=sh.attrib["name"]
            rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target=relmap[rid]
            sfile=target.lstrip("/") if target.startswith("/") else "xl/"+target
            root=ET.fromstring(z.read(sfile))
            rows=[]
            for row in root.findall(".//a:sheetData/a:row",ns):
                vals={}
                for c in row.findall("a:c",ns):
                    col=re.match(r"([A-Z]+)",c.attrib["r"]).group(1)
                    typ=c.attrib.get("t"); v=c.find("a:v",ns); value=None
                    if typ=="inlineStr":
                        isel=c.find("a:is",ns)
                        if isel is not None:
                            value="".join(t.text or "" for t in isel.iter(
                                "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"))
                    elif v is not None:
                        raw=v.text
                        if typ=="s": value=shared[int(raw)]
                        elif typ=="b": value=bool(int(raw))
                        else:
                            try: value=float(raw)
                            except: value=raw
                    vals[col]=value
                rows.append((int(row.attrib["r"]),vals))
            out[name]=rows
        return out

def parse_cdg(path):
    lines=path.read_text(errors="ignore").splitlines()
    def hval(key):
        for line in lines[:60]:
            if line.strip().startswith(key):
                return float(line.split("=",1)[1].strip().split()[0])
        return None
    nn=int(hval("Number of Nodes")); ne=int(hval("Number of Elements"))
    inode=next(i for i,l in enumerate(lines) if l.strip()=="Node Information")
    ielem=next(i for i,l in enumerate(lines) if l.strip()=="Element Information")
    nodes=[]
    for line in lines[inode+4:inode+4+nn]:
        p=line.split(); j=1
        if not re.match(r"^[-+]?\d",p[j]): j+=1
        x,y,z,n,p2,h,qx,qy=map(float,p[j:j+8])
        nodes.append((x,y,z,h,qx,qy))
    elems=[]
    for line in lines[ielem+4:ielem+4+ne]:
        p=line.split(); elems.append(tuple(int(v)-1 for v in p[3:6]))
    return np.asarray(nodes,float),np.asarray(elems,int)

cdg=find_file("mesh50_sim1.CDG")
xsfile=find_file("cross section data_2D new.xlsx")
steadyfile=find_file("Serio_Benchmark_Hydraulic_Results.csv")

book=read_xlsx_values(xsfile)
N,TRI=parse_cdg(cdg)
X,Y,Z,H,QX,QY=N.T
tri=mtri.Triangulation(X,Y,TRI)
finder=tri.get_trifinder()

node_v=np.zeros_like(H)
m=H>WET_DEPTH
node_v[m]=np.hypot(QX[m],QY[m])/H[m]

def interp(px,py,values):
    px=np.asarray(px,float); py=np.asarray(py,float)
    tind=finder(px,py)
    out=np.full(px.shape,np.nan,float)
    for t in np.unique(tind[tind>=0]):
        mask=tind==t; ids=TRI[t]
        x1,y1=X[ids[0]],Y[ids[0]]
        x2,y2=X[ids[1]],Y[ids[1]]
        x3,y3=X[ids[2]],Y[ids[2]]
        det=(y2-y3)*(x1-x3)+(x3-x2)*(y1-y3)
        l1=((y2-y3)*(px[mask]-x3)+(x3-x2)*(py[mask]-y3))/det
        l2=((y3-y1)*(px[mask]-x3)+(x1-x3)*(py[mask]-y3))/det
        l3=1-l1-l2
        out[mask]=l1*values[ids[0]]+l2*values[ids[1]]+l3*values[ids[2]]
    return out,tind

def endpoints(sheet):
    a=book[sheet][0][1]; b=book[sheet][1][1]
    return float(a["A"]),float(a["B"]),float(b["A"]),float(b["B"])

def survey(sheet):
    s=[]; z=[]
    for rn,v in book[sheet]:
        if rn>=3 and isinstance(v.get("A"),(int,float)) and isinstance(v.get("B"),(int,float)):
            s.append(float(v["A"])); z.append(float(v["B"]))
    return np.asarray(s),np.asarray(z)

def section(sheet):
    x1,y1,x2,y2=endpoints(sheet)
    L=math.hypot(x2-x1,y2-y1)
    st=np.arange(int(math.floor(L/SPACING))+1)*SPACING
    ux,uy=(x2-x1)/L,(y2-y1)/L
    px,py=x1+st*ux,y1+st*uy
    bed,ti=interp(px,py,Z); h,_=interp(px,py,H)
    qx,_=interp(px,py,QX); qy,_=interp(px,py,QY)
    v,_=interp(px,py,node_v)
    valid=ti>=0; wet=valid&(h>WET_DEPTH)
    v=np.where(wet,v,0.0)
    beta=math.atan2(y2-y1,x2-x1)
    alpha=np.arctan2(qy,qx)
    vp=np.where(wet,v*np.sin(alpha-beta),0.0)
    qp=np.where(wet,qx*(-math.sin(beta))+qy*math.cos(beta),0.0)
    ps,pz=survey(sheet)
    return dict(st=st,x=px,y=py,valid=valid,wet=wet,bed=bed,h=h,wse=bed+h,
                qx=qx,qy=qy,v=v,vp=vp,qp=qp,survey=np.interp(st,ps,pz,left=np.nan,right=np.nan))

steady={}
with open(steadyfile,newline="",encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["Profile"]=="Peak_Q559": steady[row["XS"]]=row

summary=[]
for sh in SECTIONS:
    d=section(sh); wet=d["wet"]; active=wet&(np.abs(d["vp"])>ACTIVE_VPERP)
    xs=str(int(float(sh[1:])))
    row=dict(
        Section=sh.upper(),
        River2D_Mean_WSE_m=float(np.mean(d["wse"][wet])),
        River2D_Mean_Abs_Vperp_ms=float(np.mean(np.abs(d["vp"][wet]))),
        River2D_Active_Mean_Abs_Vperp_ms=float(np.mean(np.abs(d["vp"][active]))) if np.any(active) else None,
        River2D_Max_Abs_Vperp_ms=float(np.max(np.abs(d["vp"][wet]))),
        HECRAS_Steady_WSE_m=float(steady[xs]["WSE_m"]),
        HECRAS_Steady_Channel_V_ms=float(steady[xs]["Velocity_Channel_ms"]),
    )
    row["Delta_WSE_2D_minus_1D_m"]=row["River2D_Mean_WSE_m"]-row["HECRAS_Steady_WSE_m"]
    summary.append(row)
    with open(OUT/f"{sh.upper()}_profile.csv","w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["Station_m","X_m","Y_m","Mesh_Valid","Wet","Survey_Bed_m","River2D_Bed_m","Depth_m","WSE_m","qx_m2s","qy_m2s","Vmag_ms","Vperp_ms","qperp_m2s"])
        for i in range(len(d["st"])):
            w.writerow([d["st"][i],d["x"][i],d["y"][i],int(d["valid"][i]),int(d["wet"][i]),d["survey"][i],d["bed"][i],d["h"][i],d["wse"][i],d["qx"][i],d["qy"][i],d["v"][i],d["vp"][i],d["qp"][i]])

with open(OUT/"section_summary.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(summary[0].keys()))
    w.writeheader(); w.writerows(summary)

for r in summary:
    print(r)
