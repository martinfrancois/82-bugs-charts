# 82 Bugs Talk Code to generate graphs

Python scripts that generate the charts for the talk "82 Bugs" from a CSV export of the bug list.

1. Save the first sheet of `Bugs.xlsx` as `Bugs.csv` in this directory. It needs the columns listed under [CSV format](#csv-format). To try the scripts without your own data, use the synthetic `examples/bugs.csv`.
2. Run the following code:

First time setup:

```bash
git clone https://github.com/martinfrancois/82-bugs-charts.git
cd 82-bugs-charts
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

Generate diagrams:

```bash
source venv/bin/activate
python3 over_time.py
python3 distribution_bugs_per_type.py
python3 top_15_common_subtypes.py
python3 top_15_industries_sectors.py
python3 bugs_by_employee_count.py
python3 bugs_by_severity_subtype.py
python3 bugs_by_severity_type.py
python3 severity_over_time.py
python3 severity_distribution.py
python3 animation.py
```

`python3 generate_all.py` runs all of them. Every script reads `Bugs.csv` from the current directory, or the CSV path given as its first argument, for example `python3 generate_all.py examples/bugs.csv`. The SVGs land in the current directory and the GIFs from `animation.py` in `out/`. On a machine without a display, set `MPLBACKEND=Agg`.

3. Replace the SVGs in the slides

## CSV format

The first row is the header. The scripts read these columns by name and ignore any others:

| Column | Format |
| --- | --- |
| `Date` | `DD.MM.YYYY` |
| `Type of Bug` | text |
| `Subtype` | text, may be empty |
| `Severity` | `Blocker`, `Critical`, `High`, `Medium`, `Low` or empty |
| `Employee Count` | integer, `,` as thousands separator allowed |
| `Industry/Sector` | text |

## Tests

The tests run every script on `examples/bugs.csv` in a temporary directory:

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest
```

## License

MIT, see [LICENSE](LICENSE).
