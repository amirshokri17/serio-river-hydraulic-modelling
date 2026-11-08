"""
Serio River - bridge local hydraulic analysis.

Input:
    serio.p03.hdf = benchmark nMAX + Normal-Normal steady-flow plan

Requires:
    h5py, numpy, matplotlib

Bridge zone:
    XS7 -> XS6.15 -> Bridge RS6.1 -> XS6.05 -> XS6 -> XS5

Outputs:
    - local hydraulic CSV
    - WSE / energy-grade plot
    - channel-velocity plot
    - peak-flow partition plot

Important interpretation:
    XS6.15 and XS6.05 are the immediate bridge faces (~20 m apart).
    XS6 is ~842 m downstream of XS6.05, so changes between 6.05 and 6
    must not be assigned to the bridge alone.
"""
from pathlib import Path
import csv
import h5py
import numpy as np
import matplotlib.pyplot as plt

base = Path(__file__).resolve().parent
hdf_file = base / "serio.p03.hdf"

root = "Results/Steady/Output/Output Blocks/Base Output/Steady Profiles"
xs_info = "Results/Steady/Output/Geometry Info/Cross Section Attributes"
add = root + "/Cross Sections/Additional Variables"

with h5py.File(hdf_file, "r") as f:
    profiles = [x.decode().strip() for x in f[root + "/Profile Names"][:]]
    xs = f[xs_info][:]
    stations = [x["Station"].decode().strip() for x in xs]
    wse = np.asarray(f[root + "/Cross Sections/Water Surface"][:], float)
    eg = np.asarray(f[root + "/Cross Sections/Energy Grade"][:], float)
    vel = np.asarray(f[add + "/Velocity Channel"][:], float)
    qch = np.asarray(f[add + "/Flow Channel"][:], float)
    qlob = np.asarray(f[add + "/Flow Left OB"][:], float)
    qrob = np.asarray(f[add + "/Flow Right OB"][:], float)
    hyd = np.asarray(f[add + "/Hydraulic Depth Channel"][:], float)
    crit = np.asarray(f[add + "/Critical Water Surface"][:], float)

    geom = f["Geometry/Cross Sections/Attributes"][:]
    lengths = np.asarray([r["Len Channel"] for r in geom], float)

dist_up = np.zeros(len(stations))
for i in range(1, len(stations)):
    dist_up[i] = dist_up[i-1] + lengths[i-1]
distance_km = (dist_up[-1] - dist_up) / 1000.0

fr = np.where(hyd > 0, vel / np.sqrt(9.81*hyd), np.nan)
zone = ["7","6.15","6.05","6","5"]
idx = {s: stations.index(s) for s in zone}

with open(base / "Serio_Bridge_Zone_Hydraulics.csv","w",newline="",encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["Profile","XS","Distance_km","WSE_m","EG_m","Velocity_m_s",
                "Derived_Froude","Q_Channel","Q_LOB","Q_ROB","Critical_WSE_m"])
    for pidx, profile in enumerate(profiles):
        for s in zone:
            j = idx[s]
            w.writerow([
                profile,s,distance_km[j],wse[pidx,j],eg[pidx,j],vel[pidx,j],fr[pidx,j],
                qch[pidx,j],0 if np.isnan(qlob[pidx,j]) else qlob[pidx,j],
                0 if np.isnan(qrob[pidx,j]) else qrob[pidx,j],
                "" if np.isnan(crit[pidx,j]) else crit[pidx,j]
            ])

# WSE + EG
fig, ax = plt.subplots(figsize=(10,5.7))
for pidx, profile in enumerate(profiles):
    ii = [idx[s] for s in zone]
    ax.plot(distance_km[ii],wse[pidx,ii],marker="o",label=f"WSE - {profile}")
    ax.plot(distance_km[ii],eg[pidx,ii],marker="x",linestyle="--",label=f"EG - {profile}")
ax.axvspan(distance_km[idx["6.05"]],distance_km[idx["6.15"]],alpha=0.08,label="Bridge faces")
ax.set_xlabel("Main channel distance from downstream XS1 (km)")
ax.set_ylabel("Elevation (m)")
ax.set_title("Bridge-zone water surface and energy grade")
ax.grid(True,alpha=0.25)
ax.legend(fontsize=8,ncol=2)
fig.tight_layout()
fig.savefig(base/"Bridge_Zone_WSE_Energy.png",dpi=300,bbox_inches="tight")
plt.close(fig)

# Velocity
fig, ax = plt.subplots(figsize=(10,5.7))
for pidx, profile in enumerate(profiles):
    ii = [idx[s] for s in zone]
    ax.plot(distance_km[ii],vel[pidx,ii],marker="o",label=profile)
ax.axvspan(distance_km[idx["6.05"]],distance_km[idx["6.15"]],alpha=0.08,label="Bridge faces")
ax.set_xlabel("Main channel distance from downstream XS1 (km)")
ax.set_ylabel("Channel velocity (m/s)")
ax.set_title("Bridge-zone channel velocity")
ax.grid(True,alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(base/"Bridge_Zone_Channel_Velocity.png",dpi=300,bbox_inches="tight")
plt.close(fig)

print("Done.")
