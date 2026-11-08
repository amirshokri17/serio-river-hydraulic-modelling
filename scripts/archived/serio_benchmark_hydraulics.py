"""
Serio River — benchmark hydraulic extraction from HEC-RAS steady-flow HDF.

Benchmark:
    serio.p03.hdf = nMAX + Normal-Normal

Requires:
    h5py
    numpy
    matplotlib

Outputs:
    - CSV with all cross-section hydraulic results
    - channel velocity plot
    - maximum depth plot
    - derived Froude diagnostic plot

Note:
    Froude values are derived diagnostics:
        Fr = V / sqrt(g * hydraulic_depth)
    They are not read from a native HEC-RAS Froude dataset.
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
    flow = np.asarray(f[root + "/Cross Sections/Flow"][:], float)
    velocity_ch = np.asarray(f[add + "/Velocity Channel"][:], float)
    velocity_total = np.asarray(f[add + "/Velocity Total"][:], float)
    max_depth = np.asarray(f[add + "/Maximum Depth Total"][:], float)
    hyd_depth_ch = np.asarray(f[add + "/Hydraulic Depth Channel"][:], float)
    hyd_depth_total = np.asarray(f[add + "/Hydraulic Depth Total"][:], float)
    critical_wse = np.asarray(f[add + "/Critical Water Surface"][:], float)

    geom = f["Geometry/Cross Sections/Attributes"][:]
    lengths = np.asarray([row["Len Channel"] for row in geom], float)

dist_up = np.zeros(len(stations))
for i in range(1, len(stations)):
    dist_up[i] = dist_up[i-1] + lengths[i-1]
distance_km = (dist_up[-1] - dist_up) / 1000.0

fr_ch = np.where(hyd_depth_ch > 0, velocity_ch / np.sqrt(9.81 * hyd_depth_ch), np.nan)
fr_total = np.where(hyd_depth_total > 0, velocity_total / np.sqrt(9.81 * hyd_depth_total), np.nan)

with open(base / "Serio_Benchmark_Hydraulic_Results.csv",
          "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow([
        "Profile","XS","Distance_from_downstream_XS1_km","Flow_m3s","WSE_m",
        "Maximum_Depth_m","Velocity_Channel_ms","Velocity_Total_ms",
        "Hydraulic_Depth_Channel_m","Hydraulic_Depth_Total_m",
        "Froude_Channel_Derived","Froude_Total_Derived","Critical_WSE_m"
    ])
    for pidx, profile in enumerate(profiles):
        for j, xs_name in enumerate(stations):
            w.writerow([
                profile, xs_name, distance_km[j], flow[pidx,j], wse[pidx,j],
                max_depth[pidx,j], velocity_ch[pidx,j], velocity_total[pidx,j],
                hyd_depth_ch[pidx,j], hyd_depth_total[pidx,j],
                fr_ch[pidx,j], fr_total[pidx,j],
                "" if np.isnan(critical_wse[pidx,j]) else critical_wse[pidx,j]
            ])

q25 = profiles.index("Ordinary_Q25")
q559 = profiles.index("Peak_Q559")

for stem, values, ylabel, title in [
    ("Benchmark_Channel_Velocity", velocity_ch, "Channel velocity (m/s)",
     "Benchmark channel velocity — Ordinary vs Peak"),
    ("Benchmark_Maximum_Depth", max_depth, "Maximum water depth (m)",
     "Benchmark maximum depth — Ordinary vs Peak"),
    ("Benchmark_Derived_Froude", fr_ch, "Derived channel Froude number (-)",
     "Benchmark derived channel Froude diagnostic — Ordinary vs Peak"),
]:
    fig, ax = plt.subplots(figsize=(10,5.6))
    ax.plot(distance_km, values[q25], marker="o", markersize=3.5, linewidth=1.6, label="Ordinary Q25")
    ax.plot(distance_km, values[q559], marker="o", markersize=3.5, linewidth=1.6, label="Peak Q559")
    if stem == "Benchmark_Derived_Froude":
        ax.axhline(1.0, linewidth=1.0, linestyle="--", label="Fr = 1 diagnostic line")
    ax.set_xlabel("Main channel distance from downstream XS1 (km)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(base / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(base / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)

for pidx, profile in enumerate(profiles):
    print(f"\n{profile}")
    for label, arr in [
        ("max channel velocity", velocity_ch[pidx]),
        ("max total depth", max_depth[pidx]),
        ("max derived channel Froude", fr_ch[pidx]),
    ]:
        j = int(np.nanargmax(arr))
        print(f"{label}: {arr[j]:.3f} at XS {stations[j]}")

print("\nDone.")
