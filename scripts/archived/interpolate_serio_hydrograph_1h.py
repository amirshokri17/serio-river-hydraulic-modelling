"""
Linear interpolation of the professor-provided Serio 200-year hydrograph
to a constant 60-minute interval.

Input workbook:
    200-year hydrograph.xlsx

Output:
    integer-hour data from 1 h through 98 h.
"""
from pathlib import Path
import math
import numpy as np

# Paste/import the original time and discharge arrays from the source workbook.
# Then:
hourly_time = np.arange(math.ceil(raw_time.min()), math.floor(raw_time.max()) + 1, dtype=float)
hourly_q = np.interp(hourly_time, raw_time, raw_q)

peak_i = int(np.argmax(hourly_q))
print("Hourly peak:", hourly_q[peak_i], "m3/s at", hourly_time[peak_i], "h")

with open("Serio_200yr_Hydrograph_1h.csv", "w", encoding="utf-8") as f:
    f.write("time_h,discharge_m3s\\n")
    for t, q in zip(hourly_time, hourly_q):
        f.write(f"{t:.0f},{q:.6f}\\n")
