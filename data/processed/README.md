# Provenance of published summary values

This directory contains **selected rounded, derived numerical indicators** from the River Serio analysis. It does not include original model geometry, a hydrograph, raw River2D data, source course workbooks, or full-precision HEC-RAS outputs.

- wse_comparison.csv: five sampled model-comparison locations, with signed River2D mean-wet WSE minus steady HEC-RAS peak-WSE differences. Rounded source-display values may not subtract to the last printed decimal; the comparison retains the analysis's reported differences.
- roughness_envelope.csv: ordinary and peak-flow mean WSE envelopes between adopted nMIN and nMAX scenarios. They indicate sensitivity to tested assumptions, **not probability bounds**.

The original SVG charts in figures/ are drawn from these two small files, without incorporating third-party maps or photographs. Hydrodynamic computation or higher-precision reruns require private original model data that are not published.
