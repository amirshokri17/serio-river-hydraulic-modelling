# Methodology

This page summarizes the analysis approach without redistributing the original course datasets, geometry, model files, or academic report.

## 1D steady hydraulic modelling

The 14.329 km base HEC-RAS reach contained 27 cross sections, numbered from downstream RS1 to upstream RS20. The left overbank, main channel and right overbank were parameterized separately. The geometry included a bridge at RS6.1 and adopted levee markers at RS12.1 (left) and RS8.1 (right). These geometric controls were not investigated through isolated with/without-structure experiments.

The studied discharges were 25 m³/s (ordinary) and 559.2 m³/s (peak). A one-factor-at-a-time sensitivity matrix examined minimum/nominal/maximum section-specific Manning roughness, and separately evaluated normal/critical boundary depths. The reference steady configuration selected maximum adopted roughness and normal-depth boundary formulations. This selection was conservative within the adopted scenarios; it was not an independently calibrated model.

## 1D unsteady routing and numerical checks

The supplied 200-year hydrograph was the upstream discharge boundary; the downstream boundary used normal depth with slope 0.0015. Interpolated 100 m and 50 m geometries were evaluated with 10, 5 and 2 s time steps, plus 1 h coarse stress tests. The U50_2s benchmark was selected after maximum-WSE and volume-accounting checks.

The published metrics are downstream peak attenuation, peak travel-time delay, numerical volume accounting, and steady-versus-unsteady water-surface difference. The 1 h cases serve as a demonstration of coarse-step numerical diffusion rather than an accepted benchmark. Calendar dates in the model files are synthetic computational indexing, not an observed flood date.

## Supplied River2D solution: extraction and intercomparison

A steady River2D result comprising 6,761 nodes and 13,187 triangles was used as supplied. Five section axes (S08, S10, S12, S16, S18) were sampled every 2 m, which is **post-processing spacing, not element size**. Linear interpolation within mesh triangles was used; outside-mesh values remained missing. Wet samples were defined by h > 0.02 m.

Water-surface elevation was calculated as bed elevation plus depth. The existing nodal velocity magnitude field and discharge components were interpolated separately, and the section-normal velocity component was evaluated with the section-axis orientation. The supplementary filtered wet mean omitted normal-speed values <= 0.001 m/s, without redefining physical wetness.

The direct water-level comparison uses the steady HEC-RAS peak case and River2D mean wet WSE at each section. The 1D channel-mean velocity and 2D section-normal velocity metrics are **not the same statistic**. A manual River2D export was compared with the automated extraction at S08 as an implementation check, not an observed-data validation.

## Boundaries of interpretation

No new River2D run, River2D calibration, field validation, or independent with/without-bridge experiment is claimed. The supplied 2D model showed a 3.53% inlet/outlet flow discrepancy, with no established explanation. See [limitations](limitations.md).
