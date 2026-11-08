"""Redraw selected rounded report findings; does not run a hydraulic solver.

Python >=3.10, standard library only. Paths are relative to this script.
"""
import csv
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"


def read(name):
    with (ROOT / "data" / "processed" / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def label(x, y, value, size=18, color="#183247"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" '
            f'fill="{color}">{escape(str(value))}</text>')


def chart(title, subtitle, rows, maximum, unit, footer):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="560" '
             'viewBox="0 0 1000 560" role="img" aria-labelledby="title desc">',
             f'<title id="title">{escape(title)}</title>',
             f'<desc id="desc">{escape(subtitle)}. '
             + escape('; '.join(f'{name}: {value:+.3f} {unit}' for name, value in rows))
             + '</desc>',
             '<rect width="1000" height="560" fill="#f6f9fb"/>',
             '<g font-family="Arial, sans-serif">',
             label(48, 54, title, 28), label(48, 88, subtitle, 17),
             label(48, 124, f"Unit: {unit}", 15)]
    zero, scale = 530, 350 / maximum
    parts.append(f'<line x1="{zero}" y1="145" x2="{zero}" y2="435" stroke="#8096a6"/>')
    for i, (name, value) in enumerate(rows):
        y = 165 + i * 53
        end = zero + value * scale
        color = "#087e8b" if value >= 0 else "#375b83"
        parts += [label(48, y + 23, name),
                  f'<rect x="{min(zero, end):.2f}" y="{y}" '
                  f'width="{abs(end-zero):.2f}" height="30" rx="3" fill="{color}"/>',
                  label(max(zero, end) + 14, y + 23, f"{value:+.3f}")]
    parts += [label(48, 478, footer, 16),
              label(48, 509, "Source: corrected Serio River report | Rounded published table values", 15),
              label(48, 536, "Model results; no independent field validation claimed.", 15),
              '</g></svg>']
    return '\n'.join(parts) + '\n'


def main():
    wse = read("wse_comparison.csv")
    if [r["section"] for r in wse] != ["S08", "S10", "S12", "S16", "S18"]:
        raise ValueError("Expected the five report comparison sections")
    rows = []
    for r in wse:
        delta = float(r["reported_delta_2d_minus_1d_m"])
        rounded_delta = float(r["river2d_mean_wet_wse_m"]) - float(r["hec_ras_steady_wse_m"])
        if abs(delta - rounded_delta) > 0.0011:
            raise ValueError("Difference exceeds documented table rounding")
        rows.append((r["section"], delta))
    mae = sum(abs(v) for _, v in rows) / len(rows)
    if round(mae, 3) != 0.305:
        raise ValueError("Summary no longer matches report MAE")
    OUT.mkdir(exist_ok=True)
    (OUT / "wse-comparison.svg").write_text(chart(
        "Steady 1D versus supplied River2D", "Signed WSE difference: River2D mean wet samples minus HEC-RAS steady peak",
        rows, 0.8, "m", "Table 5.2 | Mean absolute difference: 0.305 m | S08 has an internal mesh gap"), encoding="utf-8")
    rough = read("roughness_envelope.csv")
    envelope = [(r["scenario"], float(r["mean_wse_envelope_m"])) for r in rough]
    if len(envelope) != 2 or any(v <= 0 for _, v in envelope):
        raise ValueError("Expected two positive roughness envelopes")
    (OUT / "roughness-envelope.svg").write_text(chart(
        "Sensitivity to Manning roughness", "Mean water-surface envelope across the adopted nMIN and nMAX scenarios",
        envelope, 0.6, "m", "Table 3.3 | Ordinary: 25 m3/s | Peak: 559.2 m3/s | Scenario range, not uncertainty bounds"), encoding="utf-8")
    print(f"Wrote two SVG charts. Published-difference MAE: {mae:.4f} m.")


if __name__ == "__main__":
    main()
