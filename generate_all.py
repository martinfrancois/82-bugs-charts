#!/usr/bin/env python3
"""Run every chart script against one CSV file.

Usage: python3 generate_all.py [path/to/Bugs.csv]

Each script writes its SVG files into the current directory and animation.py
writes its GIFs into out/. The first script that fails stops the run.
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "over_time.py",
    "distribution_bugs_per_type.py",
    "top_15_common_subtypes.py",
    "top_15_industries_sectors.py",
    "bugs_by_employee_count.py",
    "bugs_by_severity_subtype.py",
    "bugs_by_severity_type.py",
    "severity_distribution.py",
    "severity_over_time.py",
    "animation.py",
]


def main() -> None:
    here = Path(__file__).resolve().parent
    for name in SCRIPTS:
        print(f"--- {name}", flush=True)
        # Pass the arguments through so a missing one falls back to the default in bugs_csv.py.
        subprocess.run([sys.executable, str(here / name), *sys.argv[1:]], check=True)


if __name__ == "__main__":
    main()
