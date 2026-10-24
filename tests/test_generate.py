"""Run every chart script on the synthetic CSV and check that the files appear."""

import importlib.util
import os
import shutil
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


def load_repo_module(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(args: list[str], cwd: Path, timeout: int) -> None:
    subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        env=dict(os.environ, MPLBACKEND="Agg"),
        check=True,
        timeout=timeout,
    )


@pytest.mark.parametrize("script", sorted(EXPECTED_OUTPUT))
def test_script_writes_its_files(script: str, tmp_path: Path) -> None:
    run([str(REPO / script), str(EXAMPLE_CSV)], tmp_path, timeout=300)
    for name in EXPECTED_OUTPUT[script]:
        produced = tmp_path / name
        assert produced.is_file(), f"{script} did not write {name}"
        assert produced.stat().st_size > 0, f"{name} is empty"


def test_script_without_argument_reads_default_csv(tmp_path: Path) -> None:
    default_csv = load_repo_module("bugs_csv").DEFAULT_CSV
    shutil.copy(EXAMPLE_CSV, tmp_path / default_csv)
    script = "distribution_bugs_per_type.py"
    run([str(REPO / script)], tmp_path, timeout=300)
    for name in EXPECTED_OUTPUT[script]:
        assert (tmp_path / name).is_file(), f"{script} did not write {name}"


def test_generate_all_runs_every_script(tmp_path: Path) -> None:
    run([str(REPO / "generate_all.py"), str(EXAMPLE_CSV)], tmp_path, timeout=600)
    for files in EXPECTED_OUTPUT.values():
        for name in files:
            assert (tmp_path / name).is_file(), f"generate_all.py did not write {name}"
