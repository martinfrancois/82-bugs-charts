import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define output file
svg_filename = "bugs_by_employee_count.svg"

# Load the CSV file
file_path = sys.argv[1] if len(sys.argv) > 1 else "Bugs.csv"  # CSV path: first command-line argument, Bugs.csv when omitted
df = pd.read_csv(file_path)

# Clean and process the data
df["Employee Count"] = (
    df["Employee Count"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .replace({"": pd.NA, "nan": pd.NA})
)
df["Employee Count"] = pd.to_numeric(df["Employee Count"], errors="coerce")

# Drop rows where no employee count is available
df = df.dropna(subset=["Employee Count"]).copy()

# Define sensible buckets
bucket_edges = [0, 50, 250, 1000, 5000, 20000, 100000, float("inf")]
bucket_labels = [
    "1-49",
    "50-249",
    "250-999",
    "1,000-4,999",
    "5,000-19,999",
    "20,000-99,999",
    "100,000+",
]

df["Employee Count Bucket"] = pd.cut(
    df["Employee Count"],
    bins=bucket_edges,
    labels=bucket_labels,
    right=False,
    include_lowest=True,
)

# Count bugs per bucket and order from biggest to smallest bucket
value_counts = (
    df["Employee Count Bucket"]
    .value_counts(sort=False)
    .reindex(bucket_labels)
    .fillna(0)
    .astype(int)
)

# Remove empty buckets if you do not want them shown
value_counts = value_counts[value_counts > 0]

# Reverse order so biggest bucket is at the top
value_counts = value_counts.iloc[::-1]

# Create the figure
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(y=value_counts.index, x=value_counts.values, color="black", ax=ax)

# Set font size for ticks
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

# Remove decimals from scale
ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

# Display count numbers next to bars
for i, v in enumerate(value_counts.values):
    ax.text(v + 0.5, i, str(v), va="center", fontsize=14)

# Remove the top and right spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Set labels and title
ax.set_xlabel("Bug count", fontsize=15)
ax.set_ylabel("Employee count", fontsize=15)
ax.set_title("Bug Count by Company Size", fontsize=19)

# Hide tick marks on the y-axis
ax.tick_params(axis="y", which="both", length=0)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the figure
plt.savefig(svg_filename, format="svg", bbox_inches="tight")
plt.close()

print(f"Graph saved as {svg_filename}")