"""Recover archived Python source files from Appendix D of the corrected Serio report.

Every recovered .py file must match its printed SHA-256. This is source
recovery, not a hydraulic rerun. Requires PyMuPDF.
Usage: python scripts/extract_archived_sources.py [path/to/report.pdf]
"""
from __future__ import annotations
import hashlib
import re
import sys
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = ROOT / "docs" / "technical-report.pdf"
OUTPUT = ROOT / "scripts" / "archived"
HASHES = {
    "serio_manning_sensitivity.py": "c53a4a6fad73e1361a92458c746a809b2ca748d7e75f572bcfe2712af2ea432c",
    "serio_boundary_condition_sensitivity.py": "99f5f9ee7dd66c5d24030ad219ec0c21edd41921c7bc4a185baaa867ea6ab26a",
    "serio_benchmark_hydraulics.py": "0623856e1efedc39389e012c0e9ac438eb0382c2a90d7c877cb09ba5a71d39d1",
    "serio_bridge_local_analysis.py": "0bf350fd94a39b9bcbd9c8f23a7436f999e8e9f92519e57d3eb37b28523e4ab9",
    "serio_unsteady_analysis.py": "dbe3b6cfe3b21b05b2a4cf1faa9db4ba13e2dfbe74f7883064e42a8f919ef0b5",
    "serio_river2d_analysis.py": "08eb376300784b8c1508f55abef3bd4a95bca1210f74604468a45cbd67a25f4d",
    "interpolate_serio_hydrograph_1h.py": "f0996977029381729b567ff18ffb8e07c8e66a48ae28c520d314d0dea9b2e271",
}
LINES = [115, 144, 117, 107, 335, 201, 26]


def recover(pdf_path: Path):
    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)
    scripts = []
    with fitz.open(pdf_path) as document:
        for page in document:
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    content = "".join(span["text"] for span in line["spans"]
                                      if "Consolas" in span["font"])
                    if not content:
                        continue
                    match = re.match(r"^(\d{4})  (.*)$", content)
                    if match:
                        line_number = int(match.group(1))
                        if line_number == 1:
                            scripts.append([])
                        if not scripts or line_number != len(scripts[-1]) + 1:
                            raise ValueError(f"Unexpected source line {line_number}")
                        scripts[-1].append(match.group(2))
                    elif scripts:
                        # Soft-wrap of the preceding physical source line.
                        scripts[-1][-1] += content
    if len(scripts) != len(HASHES):
        raise ValueError(f"Expected seven scripts, found {len(scripts)}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    recovered = []
    for (name, digest), lines, count in zip(HASHES.items(), scripts, LINES):
        if len(lines) != count:
            raise ValueError(f"{name}: expected {count} lines, got {len(lines)}")
        source = "\n".join(line.rstrip() for line in lines) + "\n"
        actual = hashlib.sha256(source.encode("utf-8")).hexdigest()
        if actual != digest:
            raise ValueError(f"{name}: SHA-256 mismatch, refusing to publish: {actual}")
        compile(source, name, "exec")
        (OUTPUT / name).write_text(source, encoding="utf-8")
        recovered.append((name, actual))
    return recovered


if __name__ == "__main__":
    pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PDF
    for filename, digest in recover(pdf):
        print(f"VERIFIED {filename} sha256={digest}")
