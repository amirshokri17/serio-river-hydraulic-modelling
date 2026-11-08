# Reproducibility and code use

## What is independently executable in the public repository

The public summary charts can be regenerated from the included **rounded derived** CSV summaries with Python 3.10+ and its standard library:

    python scripts/build_summary_figures.py

The script checks the selected published 1D–2D mean absolute WSE difference (0.305 m) and writes original SVG visualizations. These are figure reconstructions from derived indicators, **not hydraulic solver runs**.

A GitHub Actions workflow checks Python source syntax and regenerates the charts, failing if the committed SVGs change.

## The seven archived analysis scripts

The [archived scripts](../scripts/archived/) include six analysis/post-processing workflows and one incomplete hydrograph interpolation fragment. All seven recovered source files matched their printed SHA-256 values in the private academic report and passed Python syntax checks. Checksum verification demonstrates code fidelity, not end-to-end results.

| File | Purpose | Inputs required locally |
|---|---|---|
| serio_manning_sensitivity.py | Steady Manning sensitivity | Matching HEC-RAS plan HDF p01–p03 |
| serio_boundary_condition_sensitivity.py | Boundary-condition checks | Steady HDF p03–p06 |
| serio_benchmark_hydraulics.py | Reference steady variables | Steady HDF p03 |
| serio_bridge_local_analysis.py | Bridge-zone diagnostics | Steady HDF p03 |
| serio_unsteady_analysis.py | Transient hydraulic extraction | Steady and unsteady plan HDF p03, p07–p14 |
| serio_river2d_analysis.py | Supplied 2D profiles and comparisons | CDG, section workbook, comparison CSV |
| interpolate_serio_hydrograph_1h.py | Archived interpolation fragment | Undefined raw_time and raw_q arrays must be supplied |

The archived analysis workflows require external Python packages such as numpy, h5py and matplotlib, as well as appropriate input layouts. Exact version compatibility is not demonstrated. The standard-library requirements.txt applies to the **public summary chart workflow only**.

A separate optional [source extraction utility](../scripts/extract_archived_sources.py) can read a legally obtained local copy of the original report when explicitly passed its file path. The report itself is **not included** in this public repository.

## Full hydraulic reproduction: excluded inputs

A truly complete rerun would require legitimately obtained original HEC-RAS project/plan/geometry/flow files, HDF and DSS outputs, River2D mesh and CDG state, section axis workbook and related reference datasets, and compatible installed versions of HEC-RAS and River2D. These course-provided materials are intentionally not shared here.

Additional CSV/XLSX diagnostic fields in the archived workflow may have been produced by intermediate script revisions, so bit-for-bit regeneration of every reported field has not been demonstrated.

No independent River2D solver rerun or observational validation is claimed. The numerical comparisons should not be used for design, hazard certification or calibration claims.
