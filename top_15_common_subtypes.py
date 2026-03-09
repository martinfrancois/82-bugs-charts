import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define output file
svg_filename = "top_15_common_subtypes.svg"

# Load the CSV file
file_path = "Bugs.csv"  # Update with the correct path if necessary
df = pd.read_csv(file_path)

# Clean and process the data
subtype_counts = df["Subtype"].value_counts()

# Rename long subtype names for better readability
subtype_counts_renamed = subtype_counts.rename(
    index={"Missing translation with fallback to English / Incorrect Language / Inconsistent Language": "Translation"}
)

# Select the top 15 subtypes
top_15_subtypes = subtype_counts_renamed[:15]

# Create the figure
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(y=top_15_subtypes.index, x=top_15_subtypes.values, color="black", ax=ax)

# Set font size for ticks
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

# Remove decimals from scale
ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

# Display count numbers next to bars
for i, v in enumerate(top_15_subtypes.values):
    ax.text(v + 0.5, i, str(v), va='center', fontsize=14)

# Remove the top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Set labels and title
ax.set_xlabel("Count", fontsize=15)
ax.set_ylabel("Subtype", fontsize=15)
ax.set_title("Top 15 Most Common Bug Subtypes", fontsize=19)

# Hide tick marks on the y-axis
ax.tick_params(axis='y', which='both', length=0)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the figure
plt.savefig(svg_filename, format="svg", bbox_inches="tight")
plt.close()

print(f"Graph saved as {svg_filename}")
