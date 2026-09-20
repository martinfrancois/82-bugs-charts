import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the CSV file
file_path = sys.argv[1] if len(sys.argv) > 1 else "Bugs.csv"  # CSV path: first command-line argument, Bugs.csv when omitted
df = pd.read_csv(file_path)

# Convert Date column to datetime
df["Date"] = pd.to_datetime(df["Date"], format="%d.%m.%Y")

# Fill missing values
df["Subtype"] = df["Subtype"].fillna("Unknown")
df["Severity"] = df["Severity"].fillna("Unknown")

# Rename "Unknown" to "Below Critical"
df["Severity"] = df["Severity"].replace("Unknown", "Below Critical")

# Create severity distribution by bug type
severity_counts = df.groupby(["Type of Bug", "Severity"]).size().unstack().fillna(0)

# Compute sorting priority:
# - Sort first by total (Blocker + Critical) count (descending)
# - If equal, sort by number of Blocker bugs (descending)
severity_counts["Severe Total"] = severity_counts.get("Blocker", 0) + severity_counts.get("Critical", 0)
severity_counts["Blocker Count"] = severity_counts.get("Blocker", 0)
severity_counts = severity_counts.sort_values(by=["Severe Total", "Blocker Count"], ascending=[False, False])
severity_counts = severity_counts.drop(columns=["Severe Total", "Blocker Count"])

# Reverse order for better visualization
severity_counts = severity_counts.iloc[::-1]

# Define distinct hatch patterns
hatch_patterns = {
    "Below Critical": "",  # Empty
    "Critical": "XX",  # Double cross for critical
    "Blocker": "//",  # Single hatch for blocker
    "High": "xxxx",
    "Medium": "--",
    "Low": "\\\\\\",
}

# Plot severity distribution
fig, ax = plt.subplots(figsize=(14, 8))

# Plot each severity level with distinct shading
bottom_values = np.zeros(len(severity_counts))
for column in severity_counts.columns:
    hatch_style = hatch_patterns.get(column, "||")  # Default for unknown labels
    bars = ax.barh(
        severity_counts.index,
        severity_counts[column],
        left=bottom_values,
        label=column,
        color="white",
        edgecolor="black",
        hatch=hatch_style,
    )
    bottom_values += severity_counts[column].values

# Formatting
ax.set_xlabel("Number of Bugs", fontsize=16)
ax.set_ylabel("Bug Type", fontsize=16, labelpad=20)  # Ensure it is not cut off
# Add a centered title at the figure level
plt.suptitle(
    "Severity Distribution by Bug Type",
    y=0.97,  # bring title closer to the figure
    fontsize=19
)
ax.legend(title="Severity", fontsize=14, title_fontsize=14)
ax.tick_params(axis="both", labelsize=14)

# Remove horizontal grid lines and add vertical ones
ax.grid(axis="y", linestyle="", linewidth=0)
ax.grid(axis="x", linestyle="--", linewidth=0.7)

# Save the figure as an SVG file
svg_path = "severity_distribution.svg"  # Change the path if needed
plt.savefig(svg_path, format="svg", bbox_inches="tight")

print(f"Graph saved as: {svg_path}")