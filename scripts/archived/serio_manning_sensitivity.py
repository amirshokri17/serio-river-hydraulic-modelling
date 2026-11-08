"""
Serio River Manning sensitivity extraction from HEC-RAS steady-flow HDF files.

Expected files in the same folder:
    serio.p01.hdf  = nominal
    serio.p02.hdf  = nMIN
    serio.p03.hdf  = nMAX

Requires: h5py, numpy, matplotlib
"""
from pathlib import Path
import math
import csv
import h5py
import numpy as np
import matplotlib.pyplot as plt

base = Path(__file__).resolve().parent
files = {
    "Nominal": base / "serio.p01.hdf",
    "nMIN": base / "serio.p02.hdf",
    "nMAX": base / "serio.p03.hdf",
}

root = "Results/Steady/Output/Output Blocks/Base Output/Steady Profiles"
xs_path = "Results/Steady/Output/Geometry Info/Cross Section Attributes"
additional = root + "/Cross Sections/Additional Variables"

paths = {
    "WSE": root + "/Cross Sections/Water Surface",
    "VelocityChannel": additional + "/Velocity Channel",
    "HydraulicDepthChannel": additional + "/Hydraulic Depth Channel",
    "MaximumDepth": additional + "/Maximum Depth Total",
    "Flow": root + "/Cross Sections/Flow",
}

data = {}
stations_ref = profiles_ref = None
for case, fn in files.items():
    with h5py.File(fn, "r") as f:
        profiles = [x.decode().strip() for x in f[root + "/Profile Names"][:]]
        xs = f[xs_path][:]
        stations = [x["Station"].decode().strip() for x in xs]
        if stations_ref is None:
            stations_ref, profiles_ref = stations, profiles
        else:
            assert stations == stations_ref
            assert profiles == profiles_ref
        data[case] = {k: np.asarray(f[p][:], float) for k, p in paths.items()}

with h5py.File(files["Nominal"], "r") as f:
    geom = f["Geometry/Cross Sections/Attributes"][:]
    reach_len = np.asarray([r["Len Channel"] for r in geom], float)

distance_km = np.zeros(len(stations_ref))
for i in range(1, len(distance_km)):
    distance_km[i] = distance_km[i-1] + reach_len[i-1]
distance_km /= 1000.0

for pidx, profile in enumerate(profiles_ref):
    csv_path = base / f"{profile}_Manning_Sensitivity.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "XS", "Distance_km",
            "WSE_nMIN", "WSE_Nominal", "WSE_nMAX",
            "Delta_nMIN_Nominal", "Delta_nMAX_Nominal",
            "VelocityCh_nMIN", "VelocityCh_Nominal", "VelocityCh_nMAX",
            "MaxDepth_nMIN", "MaxDepth_Nominal", "MaxDepth_nMAX",
            "FroudeCh_nMIN_derived", "FroudeCh_Nominal_derived", "FroudeCh_nMAX_derived",
        ])
        for j, rs in enumerate(stations_ref):
            froude = {}
            for case in ("nMIN", "Nominal", "nMAX"):
                v = data[case]["VelocityChannel"][pidx, j]
                d = data[case]["HydraulicDepthChannel"][pidx, j]
                froude[case] = v / math.sqrt(9.81*d) if d > 0 else float("nan")
            w.writerow([
                rs, distance_km[j],
                data["nMIN"]["WSE"][pidx,j], data["Nominal"]["WSE"][pidx,j], data["nMAX"]["WSE"][pidx,j],
                data["nMIN"]["WSE"][pidx,j]-data["Nominal"]["WSE"][pidx,j],
                data["nMAX"]["WSE"][pidx,j]-data["Nominal"]["WSE"][pidx,j],
                data["nMIN"]["VelocityChannel"][pidx,j], data["Nominal"]["VelocityChannel"][pidx,j], data["nMAX"]["VelocityChannel"][pidx,j],
                data["nMIN"]["MaximumDepth"][pidx,j], data["Nominal"]["MaximumDepth"][pidx,j], data["nMAX"]["MaximumDepth"][pidx,j],
                froude["nMIN"], froude["Nominal"], froude["nMAX"],
            ])

    fig, ax = plt.subplots(figsize=(10, 5.5))
    for case in ("nMIN", "Nominal", "nMAX"):
        ax.plot(distance_km, data[case]["WSE"][pidx], marker="o", markersize=3.5, linewidth=1.6, label=case)
    ax.set_xlabel("Distance downstream from XS20 (km)")
    ax.set_ylabel("Water surface elevation (m)")
    ax.set_title(f"Manning roughness sensitivity — {profile}")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(base / f"WSE_{profile}_Manning_Sensitivity.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.axhline(0, linewidth=1)
    ax.plot(distance_km, data["nMIN"]["WSE"][pidx]-data["Nominal"]["WSE"][pidx],
            marker="o", markersize=3.5, linewidth=1.6, label="nMIN − Nominal")
    ax.plot(distance_km, data["nMAX"]["WSE"][pidx]-data["Nominal"]["WSE"][pidx],
            marker="o", markersize=3.5, linewidth=1.6, label="nMAX − Nominal")
    ax.set_xlabel("Distance downstream from XS20 (km)")
    ax.set_ylabel("ΔWSE relative to nominal (m)")
    ax.set_title(f"WSE change from nominal Manning n — {profile}")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(base / f"DeltaWSE_{profile}_Relative_to_Nominal.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

print("Done.")
