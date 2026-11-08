"""
Serio River - complete 1D unsteady-flow HEC-RAS post-processing.

This script reproduces the principal CSV tables and plots used for the
unsteady-flow analysis.

Expected files somewhere under the working directory:
    serio.p03.hdf  = steady benchmark, nMAX + Normal-Normal
    serio.p07.hdf  = unsteady 100 m / 10 s
    serio.p08.hdf  = unsteady 100 m / 5 s
    serio.p09.hdf  = unsteady 100 m / 2 s
    serio.p10.hdf  = unsteady 50 m / 10 s
    serio.p11.hdf  = unsteady 50 m / 5 s
    serio.p12.hdf  = unsteady 50 m / 2 s
    serio.p13.hdf  = unsteady 100 m / 1 h
    serio.p14.hdf  = unsteady 50 m / 1 h

Requires:
    h5py
    numpy
    matplotlib

Important QA rule:
    The computation step is read from the HDF result metadata, not inferred
    from the plan filename or a possibly stale .p text file.

Primary method:
    - compare maximum WSE for numerical sensitivity
    - select U50_2s as the high-resolution benchmark after convergence check
    - extract maximum WSE, flow, velocity, depth and peak times
    - compare upstream/downstream hydrographs for attenuation and celerity
    - compare unsteady maximum-water profile with steady peak-flow profile
"""

from pathlib import Path
import csv
import h5py
import numpy as np
import matplotlib.pyplot as plt

WORK = Path(__file__).resolve().parent
OUT = WORK / "postprocessed"
OUT.mkdir(exist_ok=True)

CASES = {
    "U100_10s": "serio.p07.hdf",
    "U100_5s":  "serio.p08.hdf",
    "U100_2s":  "serio.p09.hdf",
    "U50_10s":  "serio.p10.hdf",
    "U50_5s":   "serio.p11.hdf",
    "U50_2s":   "serio.p12.hdf",
    "U100_1h":  "serio.p13.hdf",
    "U50_1h":   "serio.p14.hdf",
}

ORIGINAL_XS = [
    "20","19","18","17","16","15.1","15","14","13","12.1","12","11",
    "10","9","8.2","8.1","8","7","6.15","6.05","6","5","4","3","2.1","2","1"
]

SUM_ROOT = "Results/Unsteady/Output/Output Blocks/Base Output/Summary Output/Cross Sections"
BASE_ROOT = "Results/Unsteady/Output/Output Blocks/Base Output"
TS_ROOT = BASE_ROOT + "/Unsteady Time Series/Cross Sections"
STEADY_ROOT = "Results/Steady/Output/Output Blocks/Base Output/Steady Profiles"

def dec(v):
    return v.decode().strip() if isinstance(v, (bytes, np.bytes_)) else str(v)

def find_file(name):
    matches = list(WORK.rglob(name))
    if not matches:
        raise FileNotFoundError(
            f"Could not find {name}. Put the HDF files in this folder or a subfolder."
        )
    return matches[0]

def read_case(path):
    with h5py.File(path, "r") as f:
        info = f["Plan Data/Plan Information"].attrs
        plan_title = dec(info["Plan Title"])
        geometry = dec(info["Geometry Title"])
        dt = dec(info["Computation Time Step Base"])

        xa = f["Results/Unsteady/Geometry Info/Cross Section Attributes"][:]
        stations = [dec(x["Station"]) for x in xa]
        ix = {s:i for i,s in enumerate(stations)}

        mw = np.asarray(f[SUM_ROOT + "/Maximum Water Surface"][:], float)
        mq = np.asarray(f[SUM_ROOT + "/Maximum Flow"][:], float)
        mv = np.asarray(f[SUM_ROOT + "/Maximum Channel Velocity"][:], float)

        geom = f["Geometry/Cross Sections/Attributes"][:]
        gst = [dec(x["RS"]) for x in geom]
        lengths = np.asarray([x["Len Channel"] for x in geom], float)
        cum = np.zeros(len(gst))
        for i in range(1, len(gst)):
            cum[i] = cum[i-1] + lengths[i-1]
        reach_length = float(cum[-1])

        seinfo = f["Geometry/Cross Sections/Station Elevation Info"][:]
        sevals = np.asarray(f["Geometry/Cross Sections/Station Elevation Values"][:], float)
        beds_all = np.empty(len(gst))
        for i,(start,count) in enumerate(seinfo):
            beds_all[i] = np.min(sevals[int(start):int(start+count),1])

        dist = np.array([(reach_length-cum[gst.index(s)])/1000.0 for s in ORIGINAL_XS])
        bed = np.array([beds_all[gst.index(s)] for s in ORIGINAL_XS])

        va = f["Results/Unsteady/Summary/Volume Accounting"].attrs

        tsa = f[TS_ROOT + "/Cross Section Attributes"][:]
        ts_st = [dec(x["Station"]) for x in tsa]
        tsix = {s:i for i,s in enumerate(ts_st)}
        time_h = np.asarray(f[BASE_ROOT + "/Unsteady Time Series/Time"][:], float)*24.0
        qts = np.asarray(f[TS_ROOT + "/Flow"][:], float)
        wsets = np.asarray(f[TS_ROOT + "/Water Surface"][:], float)

        bridge = np.asarray(
            f[BASE_ROOT + "/Unsteady Time Series/Bridges/serio 1-20 6.1/Bridge Variables"][:],
            float
        )

        return {
            "plan_title": plan_title,
            "geometry": geometry,
            "dt": dt,
            "stations_all": stations,
            "reach_length_m": reach_length,
            "distance_km": dist,
            "bed": bed,
            "wse_max": np.array([mw[0,ix[s]] for s in ORIGINAL_XS]),
            "t_wse_max_h": np.array([mw[2,ix[s]]*24 for s in ORIGINAL_XS]),
            "q_at_wse_max": np.array([mw[1,ix[s]] for s in ORIGINAL_XS]),
            "q_max": np.array([mq[0,ix[s]] for s in ORIGINAL_XS]),
            "t_q_max_h": np.array([mq[2,ix[s]]*24 for s in ORIGINAL_XS]),
            "wse_at_q_max": np.array([mq[1,ix[s]] for s in ORIGINAL_XS]),
            "vmax": np.array([mv[0,ix[s]] for s in ORIGINAL_XS]),
            "t_vmax_h": np.array([mv[3,ix[s]]*24 for s in ORIGINAL_XS]),
            "wse_max_all": mw[0].copy(),
            "volume_error_pct": float(va["Error Percent"]),
            "volume_error_1000m3": float(va["Error"]),
            "volume_in_1000m3": float(va["Total Boundary Flux of Water In"]),
            "volume_out_1000m3": float(va["Total Boundary Flux of Water Out"]),
            "volume_start_1000m3": float(va["Volume Starting"]),
            "volume_end_1000m3": float(va["Volume Ending"]),
            "time_h": time_h,
            "q_up": qts[:,tsix["20"]],
            "q_dn": qts[:,tsix["1"]],
            "wse_up": wsets[:,tsix["20"]],
            "wse_dn": wsets[:,tsix["1"]],
            "bridge": bridge,
        }

data = {key: read_case(find_file(filename)) for key,filename in CASES.items()}
bench = data["U50_2s"]

# ------------------------------------------------------------
# Numerical convergence
# ------------------------------------------------------------
print("\nNUMERICAL CONVERGENCE")
for spacing, refkey, k10, k5, k1h in [
    ("100 m","U100_2s","U100_10s","U100_5s","U100_1h"),
    ("50 m","U50_2s","U50_10s","U50_5s","U50_1h"),
]:
    ref = data[refkey]["wse_max_all"]
    for key in [k10,k5,k1h]:
        d = data[key]["wse_max_all"] - ref
        j = int(np.argmax(np.abs(d)))
        print(
            spacing, key,
            "mean |DeltaWSE| =", np.mean(np.abs(d)),
            "max |DeltaWSE| =", np.max(np.abs(d)),
            "at", data[refkey]["stations_all"][j]
        )

print("\nSPATIAL CONVERGENCE AT ORIGINAL XS")
for dt in ["10s","5s","2s","1h"]:
    d = data[f"U50_{dt}"]["wse_max"] - data[f"U100_{dt}"]["wse_max"]
    j = int(np.argmax(np.abs(d)))
    print(
        dt,
        "mean |50-100| =", np.mean(np.abs(d)),
        "max |50-100| =", np.max(np.abs(d)),
        "at XS", ORIGINAL_XS[j]
    )

# ------------------------------------------------------------
# Benchmark wave propagation
# ------------------------------------------------------------
qu = bench["q_max"][0]
qd = bench["q_max"][-1]
tu = bench["t_q_max_h"][0]
td = bench["t_q_max_h"][-1]
delay = td-tu
attenuation = 100*(qu-qd)/qu
celerity = bench["reach_length_m"]/(delay*3600)

twu = bench["t_wse_max_h"][0]
twd = bench["t_wse_max_h"][-1]
stage_delay = twd-twu
stage_celerity = bench["reach_length_m"]/(stage_delay*3600)

depth_max = bench["wse_max"] - bench["bed"]

print("\nBENCHMARK U50_2s")
print("Reach length:", bench["reach_length_m"], "m")
print("Upstream Qpeak:", qu, "m3/s at", tu, "h")
print("Downstream Qpeak:", qd, "m3/s at", td, "h")
print("Peak attenuation:", attenuation, "%")
print("Flow-peak delay:", delay, "h")
print("Flow-peak celerity:", celerity, "m/s")
print("Stage-peak delay:", stage_delay, "h")
print("Stage-peak celerity:", stage_celerity, "m/s")
print("Volume accounting error:", bench["volume_error_pct"], "%")

# ------------------------------------------------------------
# Export benchmark data
# ------------------------------------------------------------
with open(OUT/"benchmark_original_xs.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f)
    w.writerow([
        "XS","Distance_km_from_XS1","Bed_Min_m","Max_WSE_m","Time_Max_WSE_h",
        "Max_Q_m3s","Time_Max_Q_h","Max_Channel_Velocity_m_s","Max_Depth_m"
    ])
    for i,s in enumerate(ORIGINAL_XS):
        w.writerow([
            s,bench["distance_km"][i],bench["bed"][i],
            bench["wse_max"][i],bench["t_wse_max_h"][i],
            bench["q_max"][i],bench["t_q_max_h"][i],
            bench["vmax"][i],depth_max[i]
        ])

with open(OUT/"benchmark_hydrographs.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f)
    w.writerow(["Time_h","Q_XS20","Q_XS1","WSE_XS20","WSE_XS1"])
    for i in range(len(bench["time_h"])):
        w.writerow([bench["time_h"][i],bench["q_up"][i],bench["q_dn"][i],bench["wse_up"][i],bench["wse_dn"][i]])

with open(OUT/"benchmark_bridge_6p1.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f)
    w.writerow(["Time_h","Bridge_Q","Headwater_Stage","Tailwater_Stage","Head_Difference"])
    for i,row in enumerate(bench["bridge"]):
        w.writerow([bench["time_h"][i],row[0],row[1],row[2],row[1]-row[2]])

# ------------------------------------------------------------
# Steady vs unsteady comparison
# ------------------------------------------------------------
steady_file = find_file("serio.p03.hdf")
with h5py.File(steady_file,"r") as f:
    profiles = [dec(x) for x in f[STEADY_ROOT + "/Profile Names"][:]]
    pi = profiles.index("Peak_Q559")
    xa = f["Results/Steady/Output/Geometry Info/Cross Section Attributes"][:]
    st = [dec(x["Station"]) for x in xa]
    ix = {s:i for i,s in enumerate(st)}
    sw = np.asarray(f[STEADY_ROOT + "/Cross Sections/Water Surface"][:],float)[pi]
    sv = np.asarray(f[STEADY_ROOT + "/Cross Sections/Additional Variables/Velocity Channel"][:],float)[pi]
    steady_wse = np.array([sw[ix[s]] for s in ORIGINAL_XS])
    steady_v = np.array([sv[ix[s]] for s in ORIGINAL_XS])

steady_depth = steady_wse - bench["bed"]
delta_wse = bench["wse_max"] - steady_wse
rel_depth = 100*delta_wse/steady_depth

with open(OUT/"steady_vs_unsteady.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f)
    w.writerow([
        "XS","Distance_km_from_XS1","Bed_Min_m","Steady_WSE_m","Unsteady_Max_WSE_m",
        "Delta_WSE_m","Steady_Depth_m","Unsteady_Max_Depth_m",
        "Relative_Depth_Difference_pct","Steady_Velocity_m_s","Unsteady_Max_Velocity_m_s"
    ])
    for i,s in enumerate(ORIGINAL_XS):
        w.writerow([
            s,bench["distance_km"][i],bench["bed"][i],
            steady_wse[i],bench["wse_max"][i],delta_wse[i],
            steady_depth[i],depth_max[i],rel_depth[i],
            steady_v[i],bench["vmax"][i]
        ])

j = int(np.argmax(np.abs(delta_wse)))
print("\nSTEADY VS UNSTEADY")
print("Mean signed DeltaWSE:", np.mean(delta_wse), "m")
print("Mean absolute DeltaWSE:", np.mean(np.abs(delta_wse)), "m")
print("Max absolute DeltaWSE:", np.max(np.abs(delta_wse)), "m at XS", ORIGINAL_XS[j])

# ------------------------------------------------------------
# Plots
# ------------------------------------------------------------
order=np.argsort(bench["distance_km"])
x=bench["distance_km"][order]

def save(fig,name):
    fig.savefig(OUT/f"{name}.png",dpi=300,bbox_inches="tight")
    fig.savefig(OUT/f"{name}.pdf",bbox_inches="tight")
    plt.close(fig)

fig,ax=plt.subplots(figsize=(10,5.7))
for key in ["U50_1h","U50_10s","U50_5s","U50_2s"]:
    ax.plot(x,data[key]["wse_max"][order],marker="o",markersize=3,label=key)
ax.set_xlabel("Main channel distance from downstream XS1 (km)")
ax.set_ylabel("Maximum WSE (m)")
ax.set_title("Temporal sensitivity - 50 m spacing")
ax.grid(True,alpha=0.25); ax.legend(); fig.tight_layout(); save(fig,"temporal_sensitivity_50m")

fig,ax=plt.subplots(figsize=(10,5.7))
ax.plot(x,data["U100_2s"]["wse_max"][order],marker="o",markersize=3,label="100 m / 2 s")
ax.plot(x,data["U50_2s"]["wse_max"][order],marker="o",markersize=3,label="50 m / 2 s")
ax.set_xlabel("Main channel distance from downstream XS1 (km)")
ax.set_ylabel("Maximum WSE (m)")
ax.set_title("Spatial sensitivity at 2 s")
ax.grid(True,alpha=0.25); ax.legend(); fig.tight_layout(); save(fig,"spatial_sensitivity_2s")

fig,ax=plt.subplots(figsize=(10,5.7))
ax.plot(bench["time_h"],bench["q_up"],label="Upstream XS20")
ax.plot(bench["time_h"],bench["q_dn"],label="Downstream XS1")
ax.set_xlabel("Simulation time (h)"); ax.set_ylabel("Discharge (m3/s)")
ax.set_title("Benchmark flood-wave propagation")
ax.grid(True,alpha=0.25); ax.legend(); fig.tight_layout(); save(fig,"benchmark_hydrographs")

fig,ax=plt.subplots(figsize=(10,5.7))
ax.plot(x,steady_wse[order],marker="o",markersize=3,label="Steady Q=559.2")
ax.plot(x,bench["wse_max"][order],marker="o",markersize=3,label="Unsteady maximum WSE")
ax.set_xlabel("Main channel distance from downstream XS1 (km)")
ax.set_ylabel("Water surface elevation (m)")
ax.set_title("Steady peak vs unsteady maximum-water profile")
ax.grid(True,alpha=0.25); ax.legend(); fig.tight_layout(); save(fig,"steady_vs_unsteady_wse")

fig,ax=plt.subplots(figsize=(10,5.7))
ax.axhline(0,linewidth=1)
ax.plot(x,delta_wse[order],marker="o",markersize=3)
ax.set_xlabel("Main channel distance from downstream XS1 (km)")
ax.set_ylabel("Unsteady - steady WSE (m)")
ax.set_title("Steady/unsteady WSE difference")
ax.grid(True,alpha=0.25); fig.tight_layout(); save(fig,"steady_vs_unsteady_delta")

print("\nOutputs written to:", OUT)
