# 82 Bugs Talk Code to generate graphs

1. Save the first sheet of `Bugs.xlsx` as `Bugs.csv` in this directory
2. Run the following code:

```
python3 -m venv venv  # first time only
source venv/bin/activate
python3 -m pip install pandas matplotlib pandas seaborn  # first time only
python3 over_time.py
python3 distribution_bugs_per_type.py
python3 top_15_common_subtypes.py
python3 distribution_bugs_per_type.py
python3 bugs_by_severity_subtype.py
python3 bugs_by_severity_type.py
python3 severity_over_time.py
python3 animation.py
```

3. Replace the SVGs in the slides