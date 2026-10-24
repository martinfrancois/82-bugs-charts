import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from bugs_csv import csv_path

# Define output file
svg_filename = "severity_bug_percentage_subtype_top_15.svg"

# Load the CSV file
file_path = csv_path()
df = pd.read_csv(file_path)

# Convert Date column to datetime format
df["Date"] = pd.to_datetime(df["Date"], format="%d.%m.%Y", errors="coerce")

# Calculate total bugs per subtype
bug_subtype_counts = df["Subtype"].value_counts()

# Calculate total severe (Blocker + Critical) bugs per subtype
severe_subtype_counts = (
  df[df["Severity"].isin(["Blocker", "Critical"])]
  .groupby("Subtype")
  .size()
)

# Calculate percentage of severe bugs per subtype
severe_percentage_subtype = (
  severe_subtype_counts.div(bug_subtype_counts).mul(100).fillna(0)
)

# Combine into a DataFrame and sort by percentage descending, then subtype ascending
summary_df = pd.DataFrame({
  "Total Bugs":        bug_subtype_counts,
  "Severe Bugs":       severe_subtype_counts.fillna(0).astype(int),
  "Severe Percentage": severe_percentage_subtype
}).reset_index().rename(columns={"index": "Subtype"})

summary_df = summary_df.sort_values(
  by=["Severe Percentage", "Subtype"],
  ascending=[False, True]
)

# Limit to the top 15 subtypes and rename any overly long label
top15_df = (
  summary_df
  .head(15)
  .set_index("Subtype")
  .rename(index={
    "Missing translation with fallback to English / Incorrect Language / Inconsistent Language":
      "Translation"
  })
)

# Apply Seaborn white style
sns.set_style("white")

# Create the figure
fig, ax = plt.subplots(figsize=(12, 6))

# Plot horizontal barplot with Seaborn
sns.barplot(
  x=top15_df["Severe Percentage"],
  y=top15_df.index,
  color="black",
  ax=ax
)

# Set font size for tick labels
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

# Set axis labels
ax.set_xlabel("Percentage of Critical and Blocker Bugs (%)", fontsize=15)
ax.set_ylabel("Subtype", fontsize=15)

# Add a centered title at the figure level
fig.suptitle(
  "Top 15 Bug Subtypes with Highest Percentage of Critical and Blocker Bugs",
  y=0.97,  # bring title closer to the figure
  fontsize=19
)

# Annotate each bar with its percentage
for i, (subtype, row) in enumerate(top15_df.iterrows()):
  val = row["Severe Percentage"]
  ax.text(val + 0.5, i, f"{val:.1f}%", va="center", fontsize=14)

# Remove the top and right spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Hide tick marks on the y-axis
ax.tick_params(axis="y", which="both", length=0)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the figure
plt.savefig(svg_filename, format="svg", bbox_inches="tight")
plt.close()

print(f"Graph saved as {svg_filename}")
