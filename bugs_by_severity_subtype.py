import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = "Bugs.csv"  # Change this to the correct path of your CSV file
bugs_df = pd.read_csv(file_path)

# Convert Date column to datetime format
bugs_df["Date"] = pd.to_datetime(
  bugs_df["Date"],
  format="%d.%m.%Y",
  errors="coerce"
)

# Calculate total bugs per subtype
total_bugs_per_subtype = bugs_df["Subtype"].value_counts()

# Calculate total severe (Blocker + Critical) bugs per subtype
severe_bugs_per_subtype = (
  bugs_df[bugs_df["Severity"].isin(["Blocker", "Critical"])]
  .groupby("Subtype")
  .size()
)

# Calculate percentage of severe bugs per subtype
severe_percentage = (
        severe_bugs_per_subtype / total_bugs_per_subtype * 100
)

# Combine into a dataframe and sort by severity percentage
severity_df = pd.DataFrame({
  "Total Bugs": total_bugs_per_subtype,
  "Severe Bugs": severe_bugs_per_subtype.fillna(0).astype(int),
  "Severe Percentage": severe_percentage.fillna(0)
}).sort_values("Severe Percentage", ascending=False)

# Limit to the top 15 subtypes
top15 = severity_df.head(15).rename(index={
  "Missing translation with fallback to English / Incorrect Language / Inconsistent Language":
    "Translation"
})

# Create figure and axes
fig, ax = plt.subplots(figsize=(12, 6))

# Plot horizontal bar chart on our axes
top15["Severe Percentage"] \
  .sort_values() \
  .plot(kind="barh", color="black", width=0.7, ax=ax)

# Labels and title
ax.set_xlabel("Percentage of Critical and Blocker Bugs (%)", fontsize=15)
ax.set_ylabel("Subtype", fontsize=15)
ax.set_title(
  "Top 15 Bug Subtypes with Highest Percentage of Critical and Blocker Bugs",
  fontsize=19
)

# Grid styling
ax.grid(axis="x", linestyle="--", alpha=0.7)
ax.grid(axis="y", linestyle="", alpha=0)

# Annotate each bar with its value
for idx, val in enumerate(top15["Severe Percentage"].sort_values()):
  ax.text(val + 1, idx, f"{val:.1f}%", va="center", fontsize=14)

# Remove the top and right spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Adjust layout and save
plt.tight_layout()
fig.savefig(
  "severity_bug_percentage_subtype_top_15.svg",
  format="svg",
  bbox_inches="tight"
)

print("SVG visualization saved as: severity_bug_percentage_subtype_top_15.svg")
