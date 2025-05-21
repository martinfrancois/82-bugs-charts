import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# Define output file
svg_filename = "bugs_per_month.svg"

# Load the data
file_path = "Bugs.csv"  # Update this path as needed
bugs_df = pd.read_csv(file_path)

# Ensure the date column is properly formatted
bugs_df['Date'] = pd.to_datetime(bugs_df['Date'], dayfirst=True)

# Define the start date
start_date = "2022-11-01"

# Dynamically determine the end date based on the latest date in the dataset
latest_date = bugs_df['Date'].max()
end_period = latest_date.to_period('M')           # Get the period of the latest date
end_date_filter = end_period.end_time              # Use the last day of that month for filtering

# Filter the dataframe between the start date and the dynamically determined end date
bugs_df = bugs_df[(bugs_df['Date'] >= start_date) & (bugs_df['Date'] <= end_date_filter)]

# Create a monthly period column and count bugs by month
bugs_df['Month'] = bugs_df['Date'].dt.to_period('M')
bug_counts = bugs_df.groupby('Month').size()

# Create a monthly index from start_date to the dynamically determined end period
date_range = pd.period_range(start=start_date, end=end_period, freq='M')
bug_counts = bug_counts.reindex(date_range, fill_value=0)

# Remove months where the amount of bugs is 0
bug_counts = bug_counts[bug_counts > 0]

# Plot the results
plt.figure(figsize=(12, 6))
plt.plot(bug_counts.index.astype(str), bug_counts.values, marker='o', linestyle='-', color='k')  # Line color is black

# Rotate x-axis labels to 90 degrees and set font size for ticks
plt.xticks(rotation=90, fontsize=14)
plt.yticks(fontsize=14)

ax = plt.gca()

# Set y-axis ticks in steps of 5 and start the y-axis at 0
ax.yaxis.set_major_locator(MultipleLocator(5))
ax.set_ylim(bottom=0)

# Add vertical and horizontal dashed grid lines with alpha set to 0.5
ax.grid(axis='x', linestyle='--', alpha=0.5)
ax.grid(axis='y', linestyle='--', alpha=0.5)

# Remove the top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Make January labels bold
for label in ax.get_xticklabels():
    if label.get_text().endswith('-01'):  # Identifying January months
        label.set_fontweight('bold')

# Set labels and title with larger font sizes
plt.xlabel("Month", fontsize=15)
plt.ylabel("Number of Bugs Found", fontsize=15)
# Add a centered title at the figure level
plt.suptitle(
    "Bugs Found Per Month",
    y=0.932,  # bring title closer to the figure
    fontsize=19
)

# Save the figure
plt.savefig(svg_filename, format="svg", bbox_inches="tight")
plt.close()

print(f"Graph saved as {svg_filename}")
