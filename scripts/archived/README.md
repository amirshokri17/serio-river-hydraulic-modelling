# Archived analysis scripts

This folder contains the seven Python listings preserved in Appendix D of a non-public academic hydraulic modelling report. The files were recovered and checked against their reported SHA-256 digests; syntax checks passed.

The main scripts post-process **pre-existing HEC-RAS HDF or supplied River2D results**. They do not perform the underlying hydraulic calculations. No third-party model file is distributed in this repository.

| File | Function |
|---|---|
| serio_manning_sensitivity.py | Manning roughness scenario extraction and plotting |
| serio_boundary_condition_sensitivity.py | Normal/critical boundary comparison |
| serio_benchmark_hydraulics.py | Steady hydraulic variable processing |
| serio_bridge_local_analysis.py | Local bridge diagnostics |
| serio_unsteady_analysis.py | Unsteady peak, timing and numerical checks |
| serio_river2d_analysis.py | Section-based extraction and comparison of a supplied 2D result |
| interpolate_serio_hydrograph_1h.py | Original incomplete fragment, not standalone executable |

To run the analysis workflows you need the appropriate original input files, their expected local filenames, and Python scientific libraries as referenced within each script. These files are **not** part of the public release. Do not run the incomplete hydrograph fragment as a standalone utility; the original time and discharge arrays were not defined in that listing.

For a working example requiring only public data, run the separate ../build_summary_figures.py from the repository root.
