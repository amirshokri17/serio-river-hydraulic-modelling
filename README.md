# Lower Serio River Hydraulic Modelling

**1D steady and unsteady HEC-RAS analysis · Python post-processing · comparison with supplied River2D results**

An engineering study of approximately **14.3 km of the lower Serio River**, downstream of Crema, Italy. The project examines how roughness, boundary conditions and numerical discretization affect predicted water levels, and how steady 1D, unsteady 1D and spatially distributed 2D results complement one another.

The authoritative technical source is the [corrected 77-page report](docs/technical-report.pdf). This repository presents its findings and an independently runnable summary-figure workflow. It is **not yet an end-to-end reproducible hydraulic simulation package**.

## Selected findings

| Finding | Reported result | Interpretation |
|---|---:|---|
| Modelled channel length | 14,329 m | Base HEC-RAS geometry: 27 cross sections |
| Steady flood discharge | 559.2 m³/s | Supplied 200-year scenario, not an observed event |
| Mean peak-flow roughness WSE envelope | 0.524 m | nMAX minus nMIN; maximum 0.850 m at XS6 |
| Unsteady downstream peak | 533.14 m³/s | U50_2s benchmark; upstream peak 559.17 m³/s |
| Simulated peak attenuation / delay | 4.65% / 5.96 h | Flood routing over the modelled reach |
| Mean absolute 1D–2D WSE difference | 0.305 m | Five representative sections; model comparison |
| River2D displayed boundary-flow discrepancy | **3.53%** | Outflow exceeds inflow; cause unverified |

![Steady 1D versus supplied 2D water levels](figures/wse-comparison.svg)

*Fresh plot of report Table 5.2, using its published signed differences. Differences are not errors against observations. Small rounding differences occur between displayed WSE values and reported differences.*

## Methodology

1. **Steady HEC-RAS:** evaluate 25 m³/s ordinary flow and 559.2 m³/s peak flow; test section-specific minimum, nominal and maximum Manning roughness and normal/critical boundary conditions. Adopt nMAX with Normal–Normal boundaries as the study benchmark.
2. **Unsteady HEC-RAS:** route the supplied flood hydrograph through interpolated 100 m and 50 m geometries; compare 10 s, 5 s and 2 s time steps, with 1 h cases as stress tests. Select **U50_2s** after numerical convergence checks. Downstream normal-depth slope: 0.0015.
3. **Supplied River2D solution:** post-process the existing 6,761-node / 13,187-element solution. Sample S08, S10, S12, S16 and S18 at 2 m intervals; retain wet samples with h > 0.02 m. Compare mean wet 2D WSE with steady peak 1D WSE.

See [methodology](docs/methodology.md), [results](docs/results.md), [limitations](docs/limitations.md) and [reproducibility](docs/reproducibility.md).

## Scope and technical honesty

The study developed and assessed the 1D models. **River2D results were supplied and post-processed; they were not independently re-simulated, calibrated or field-validated.** The displayed River2D flows are Qin = 559.000 and Qout = 578.730 m³/s, a difference of +19.730 m³/s (3.53% of Qin). Its cause is not established.

Numerical convergence and extraction checks support implementation consistency, not predictive accuracy. The comparison is not a validated flood map, erosion assessment or design certification. S08 crosses an internal mesh gap; its integrated discharge is omitted. The 2D footprint does not cover the entire 1D reach.

## Run the public summary workflow

Python 3.10 or newer; **no external packages**:

```sh
python scripts/build_summary_figures.py
```

This regenerates the two SVG charts from the small, attributed CSV tables in `data/processed/`. It does not run HEC-RAS or River2D and does not reconstruct a hydrograph from peak statistics. Read [reproducibility notes](docs/reproducibility.md) before attempting to use the report's archived code listings.

## Repository structure

```text
docs/                 Technical report, methods, results and release notes
data/processed/       Selected rounded report-table values and provenance
figures/              Original SVG summary charts generated from those values
scripts/              Portable summary-figure generation
outreach/             LinkedIn announcement draft and carousel plan
CITATION.cff          Repository citation metadata
LICENSE               MIT license for project-owned code only
THIRD_PARTY_NOTICES.md Attribution and rights boundaries
```

## Attribution and citation

Maintained by [Amir Shokri](https://github.com/amirshokri17). The project uses supplied course geometry, hydrograph and River2D results; their provision is acknowledged without implying authorship of those inputs. The repository owner confirmed redistribution permission for supplied course models/data and report images on 8 November 2026. This permission does not assign them an MIT license.

The corrected report has no named author or publication date on its title page; repository attribution does not establish sole authorship of every input or report component. See [rights and attribution](THIRD_PARTY_NOTICES.md) and [citation metadata](CITATION.cff). No DOI or formal release is claimed.

Technical references, as cited in report §7.1: Chow (1959), *Open-Channel Hydraulics*; Brunner (2020), *HEC-RAS Hydraulic Reference Manual*, Version 6.0 Beta; USACE HEC-RAS online user documentation; Steffler and Blackburn (2002), *River2D: Introduction to Depth Averaged Modeling and User's Manual*. These references do not establish the software versions used for the project.
