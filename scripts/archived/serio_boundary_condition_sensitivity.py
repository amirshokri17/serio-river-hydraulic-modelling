"""
Serio River — boundary-condition sensitivity from HEC-RAS steady-flow HDF files.

Put these files in the same folder as this script:
    serio.p03.hdf = NN (nMAX + Normal/Normal)
    serio.p04.hdf = NC (Normal/Critical)
    serio.p05.hdf = CN (Critical/Normal)
    serio.p06.hdf = CC (Critical/Critical)

Requires:
    h5py
    numpy
    matplotlib

Outputs:
    - two CSV result tables
    - WSE comparison plots for Q25 and Q559
    - Delta-WSE plots relative to NN
"""

from pathlib import Path
import csv
import h5py
import numpy as np
import matplotlib.pyplot as plt

base = Path(__file__).resolve().parent

files = {
    "NN": base / "serio.p03.hdf",
    "NC": base / "serio.p04.hdf",
    "CN": base / "serio.p05.hdf",
    "CC": base / "serio.p06.hdf",
}

root = "Results/Steady/Output/Output Blocks/Base Output/Steady Profiles"
xs_path = "Results/Steady/Output/Geometry Info/Cross Section Attributes"
wse_path = root + "/Cross Sections/Water Surface"

data = {}
stations_ref = None
profiles_ref = None

for case, fn in files.items():
    with h5py.File(fn, "r") as f:
        profiles = [x.decode().strip() for x in f[root + "/Profile Names"][:]]
        xs = f[xs_path][:]
        stations = [x["Station"].decode().strip() for x in xs]
        wse = np.asarray(f[wse_path][:], dtype=float)

        if stations_ref is None:
            stations_ref = stations
            profiles_ref = profiles
        else:
            assert stations == stations_ref, f"Cross-section mismatch: {case}"
            assert profiles == profiles_ref, f"Profile mismatch: {case}"

        data[case] = wse

# HEC-RAS style distance: 0 at downstream XS1, increasing upstream to XS20.
with h5py.File(files["NN"], "r") as f:
    geom = f["Geometry/Cross Sections/Attributes"][:]
    lengths = np.asarray([row["Len Channel"] for row in geom], dtype=float)

dist_from_upstream = np.zeros(len(stations_ref))
for i in range(1, len(stations_ref)):
    dist_from_upstream[i] = dist_from_upstream[i-1] + lengths[i-1]

distance_km = (dist_from_upstream[-1] - dist_from_upstream) / 1000.0

for pidx, profile in enumerate(profiles_ref):
    # CSV
    with open(base / f"{profile}_Boundary_Condition_Sensitivity.csv",
              "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "XS", "Distance_from_downstream_XS1_km",
            "WSE_NN_m", "WSE_NC_m", "WSE_CN_m", "WSE_CC_m",
            "Delta_NC_minus_NN_m",
            "Delta_CN_minus_NN_m",
            "Delta_CC_minus_NN_m"
        ])
        for j, xs in enumerate(stations_ref):
            w.writerow([
                xs, distance_km[j],
                data["NN"][pidx,j], data["NC"][pidx,j],
                data["CN"][pidx,j], data["CC"][pidx,j],
                data["NC"][pidx,j] - data["NN"][pidx,j],
                data["CN"][pidx,j] - data["NN"][pidx,j],
                data["CC"][pidx,j] - data["NN"][pidx,j],
            ])

    # WSE comparison
    fig, ax = plt.subplots(figsize=(10, 5.6))
    for case, marker, linestyle in [
        ("NN","o","-"), ("NC","s","-"), ("CN","^","--"), ("CC","x","--")
    ]:
        ax.plot(distance_km, data[case][pidx],
                marker=marker, markersize=3.2,
                linewidth=1.5, linestyle=linestyle, label=case)
    ax.set_xlabel("Main channel distance from downstream XS1 (km)")
    ax.set_ylabel("Water surface elevation (m)")
    ax.set_title(f"Boundary-condition sensitivity — {profile}")
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=4)
    fig.tight_layout()
    fig.savefig(base / f"BC_WSE_{profile}.png", dpi=300, bbox_inches="tight")
    fig.savefig(base / f"BC_WSE_{profile}.pdf", bbox_inches="tight")
    plt.close(fig)

    # Delta relative to NN
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.axhline(0, linewidth=1)
    for case, marker, linestyle in [
        ("NC","s","-"), ("CN","^","--"), ("CC","x","--")
    ]:
        delta = data[case][pidx] - data["NN"][pidx]
        ax.plot(distance_km, delta,
                marker=marker, markersize=3.2,
                linewidth=1.5, linestyle=linestyle,
                label=f"{case} − NN")
    ax.set_xlabel("Main channel distance from downstream XS1 (km)")
    ax.set_ylabel("Delta WSE relative to NN (m)")
    ax.set_title(f"Boundary-condition effect relative to NN — {profile}")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(base / f"BC_DeltaWSE_{profile}_Relative_to_NN.png",
                dpi=300, bbox_inches="tight")
    fig.savefig(base / f"BC_DeltaWSE_{profile}_Relative_to_NN.pdf",
                bbox_inches="tight")
    plt.close(fig)

    # Numerical diagnostic
    print(f"\n{profile}")
    for case in ("NC", "CN", "CC"):
        d = data[case][pidx] - data["NN"][pidx]
        j = int(np.argmax(np.abs(d)))
        print(
            f"{case}-NN: mean={np.mean(d):+.4f} m, "
            f"max abs={np.max(np.abs(d)):.4f} m at XS {stations_ref[j]}"
        )

print("\nDone.")
