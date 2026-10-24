"""Where the chart scripts read the bug list from."""

import sys

DEFAULT_CSV = "Bugs.csv"


def csv_path() -> str:
    """Return the first command-line argument, or Bugs.csv in the current directory."""
    return sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV
