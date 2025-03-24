import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define output file
svg_filename = "distribution_bugs_per_type.svg"

# Load the CSV file
file_path = "Bugs.csv"  # Update with the correct path if necessary
df = pd.read_csv(file_path)

# Count of bugs per type
bug_type_counts = df["Type of Bug"].value_counts()

# Create the figure
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(y=bug_type_counts.index, x=bug_type_counts.values, color="black", ax=ax)

# Set font size for ticks
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

# Set title and labels
ax.set_ylabel("Bug Type", fontsize=15)
ax.set_xlabel("Count", fontsize=15)
ax.set_title("Distribution of Bugs by Type", fontsize=19)

# Display count numbers next to bars
for i, v in enumerate(bug_type_counts.values):
    ax.text(v + 0.5, i, str(v), va='center', fontsize=14)

# Remove the top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Hide tick marks on the y-axis
ax.tick_params(axis='y', which='both', length=0)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the figure
plt.savefig(svg_filename, format="svg", bbox_inches="tight")
plt.close()

print(f"Graph saved as {svg_filename}")