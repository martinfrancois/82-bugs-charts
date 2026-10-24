import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from bugs_csv import csv_path

# --- Settings ---
svg_filename = "severity_bug_percentage_by_type.svg"
file_path    = csv_path()

# --- Load and preprocess ---
df = pd.read_csv(file_path)
df["Date"] = pd.to_datetime(df["Date"], format="%d.%m.%Y", errors="coerce")

# --- Compute totals and severes per Type of Bug ---
total_per_type = df["Type of Bug"].value_counts()
severe_per_type = (
    df[df["Severity"].isin(["Blocker", "Critical"])]
    .groupby("Type of Bug")
    .size()
)
percent_severe = (
    severe_per_type
    .div(total_per_type)
    .mul(100)
    .reindex(total_per_type.index, fill_value=0)
)

# --- Build summary and sort ---
summary = pd.DataFrame({
    "Total Bugs": total_per_type,
    "Severe %": percent_severe
}).reset_index().rename(columns={"index": "Type of Bug"})
summary = summary.sort_values(
    by=["Severe %", "Type of Bug"],
    ascending=[False, True]
).set_index("Type of Bug")

# --- Plot ---
sns.set_style("white")
fig, ax = plt.subplots(figsize=(12, 6))

sns.barplot(
    x=summary["Severe %"],
    y=summary.index,
    color="black",
    ax=ax
)

# formatting ticks and labels
ax.set_xlabel("Percentage of Critical and Blocker Bugs (%)", fontsize=15)
ax.set_ylabel("Bug Type", fontsize=15)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

# title
fig.suptitle(
    "Percentage of Critical and Blocker Bugs per Bug Type",
    y=0.96,
    fontsize=19
)

# annotate only percentage (including 0%)
for i, pct in enumerate(summary["Severe %"]):
    ax.text(
        pct + 0.5, i,
        f"{pct:.0f}%",        # round to nearest integer
        va="center",
        fontsize=14
    )

# clean up spines and ticks
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="y", which="both", length=0)

plt.tight_layout()
plt.savefig(svg_filename, format="svg", bbox_inches="tight")
plt.close()

print(f"Saved graph to {svg_filename}")
