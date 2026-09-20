"""Run every chart script on the synthetic CSV and check that the files appear."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
EXAMPLE_CSV = REPO / "examples" / "bugs.csv"

# script name -> files it writes into the working directory
EXPECTED_OUTPUT = {
    "over_time.py": ["bugs_per_month.svg"],
    "distribution_bugs_per_type.py": ["distribution_bugs_per_type.svg"],
    "top_15_common_subtypes.py": ["top_15_common_subtypes.svg"],
    "top_15_industries_sectors.py": ["top_15_industries_sectors.svg"],
    "bugs_by_employee_count.py": ["bugs_by_employee_count.svg"],
    "bugs_by_severity_subtype.py": ["severity_bug_percentage_subtype_top_15.svg"],
    "bugs_by_severity_type.py": ["severity_bug_percentage_by_type.svg"],
    "severity_distribution.py": ["severity_distribution.svg"],
    "severity_over_time.py": [
        "bugs_severity_over_time_monthly.svg",
        "bugs_severity_over_time_quarterly.svg",
    ],
    "animation.py": [
        "out/bugs_types_transition_hbar.gif",
        "out/bugs_subtypes_transition_hbar.gif",
    ],
}


def run_script(script: str, cwd: Path) -> None:
    env = dict(os.environ, MPLBACKEND="Agg")
    subprocess.run(
        [sys.executable, str(REPO / script), str(EXAMPLE_CSV)],
        cwd=cwd,
        env=env,
        check=True,
        timeout=300,
    )


@pytest.mark.parametrize("script", sorted(EXPECTED_OUTPUT))
def test_script_writes_its_files(script: str, tmp_path: Path) -> None:
    run_script(script, tmp_path)
    for name in EXPECTED_OUTPUT[script]:
        produced = tmp_path / name
        assert produced.is_file(), f"{script} did not write {name}"
        assert produced.stat().st_size > 0, f"{name} is empty"


def test_generate_all_runs_every_script(tmp_path: Path) -> None:
    subprocess.run(
        [sys.executable, str(REPO / "generate_all.py"), str(EXAMPLE_CSV)],
        cwd=tmp_path,
        env=dict(os.environ, MPLBACKEND="Agg"),
        check=True,
        timeout=600,
    )
    for files in EXPECTED_OUTPUT.values():
        for name in files:
            assert (tmp_path / name).is_file(), f"generate_all.py did not write {name}"
