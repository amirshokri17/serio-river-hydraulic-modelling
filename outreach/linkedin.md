# LinkedIn project announcement — publication copy

**Suggested post:**

How much can hydraulic modelling assumptions change a river's predicted flood response?

I recently completed a computational hydraulic analysis of approximately 14.3 km of the lower Serio River in Italy, combining 1D steady and unsteady HEC-RAS modelling, numerical sensitivity studies, Python post-processing, and comparison with a supplied River2D solution.

Three engineering findings stood out:

• Manning roughness had a measurable effect on modelled flood stages: a mean 0.524 m WSE envelope between the tested minimum and maximum scenarios under peak flow.
• The selected unsteady simulation predicted 4.65% downstream flood-peak attenuation and a 5.96-hour peak delay.
• Comparing steady 1D and supplied 2D results at five sections revealed a 0.305 m mean absolute WSE difference and important lateral velocity variations.

The most useful lesson was methodological: numerical consistency is not the same as field validation, and 1D and 2D outputs must be compared using clearly defined metrics.

I have shared the analysis scripts, derived summary graphics, technical methodology and limitations on GitHub. Original course-provided geometry, hydrographs, model files and data are deliberately not redistributed.

Explore the project:
https://github.com/amirshokri17/serio-river-hydraulic-modelling

#HydraulicModelling #HECRAS #FloodModelling #WaterResourcesEngineering #Python #CivilEngineering

---

## Recommended six-slide document carousel

1. **Title / engineering question:** Lower Serio River — computational hydraulics and model intercomparison. Use a new abstract river schematic, not provided course maps.
2. **Workflow / responsibilities:** 1D steady → parameter and boundary sensitivity → 1D unsteady → supplied 2D post-processing. Clearly distinguish developed and supplied elements.
3. **Roughness sensitivity:** Original figure from figures/roughness-envelope.svg, with the 0.524 m flood-stage envelope.
4. **Flood routing:** 559.17 m³/s upstream vs 533.14 m³/s downstream; 4.65% attenuation and 5.96 h delay. No invented hydrograph or observational claim.
5. **1D–2D comparison:** Original figure from figures/wse-comparison.svg; report 0.305 m mean absolute WSE difference over five sections, with S16 the largest discrepancy.
6. **Takeaways and public code:** Each modeling dimension answers a different question; numerical quality limits remain. QR or plain GitHub URL.

**Publication status:** This file is a prepared draft, not evidence that a LinkedIn post has been sent.
