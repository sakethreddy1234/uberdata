# Uber Supply-Demand Gap Analysis in Python

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the data
df = pd.read_excel('Uber Request Data.xlsx', sheet_name='Uber Request Data')


# 2. Data Cleaning
# Convert timestamps to datetime
df['Request timestamp'] = pd.to_datetime(df['Request timestamp'], errors='coerce')
df['Drop timestamp'] = pd.to_datetime(df['Drop timestamp'], errors='coerce')

# Check for missing values
print(df.isnull().sum())

# 3. Feature Engineering
# Extract hour and create time slots
df['hour'] = df['Request timestamp'].dt.hour

def time_slot(hour):
    if 0 <= hour < 4:
        return 'Night'
    elif 4 <= hour < 8:
        return 'Early Morning'
    elif 8 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 21:
        return 'Evening'
    else:
        return 'Late Night'

df['time_slot'] = df['hour'].apply(time_slot)

# 4. Aggregation for Supply-Demand Gap
gap = df.groupby(['time_slot', 'Pickup point', 'Status']).size().reset_index(name='count')

# 5. Pivot for Visualization
pivot_gap = gap.pivot_table(index=['time_slot', 'Pickup point'], columns='Status', values='count', fill_value=0)
pivot_gap['Total Requests'] = pivot_gap.sum(axis=1)
pivot_gap['Unfulfilled'] = pivot_gap.get('Cancelled', 0) + pivot_gap.get('No Cars Available', 0)
pivot_gap['Gap %'] = (pivot_gap['Unfulfilled'] / pivot_gap['Total Requests']) * 100

print(pivot_gap)

# 6. Visualization: Supply-Demand Gap by Time Slot
plt.figure(figsize=(10,6))
sns.barplot(
    data=df[df['Status'] != 'Trip Completed'],
    x='time_slot',
    hue='Status',
    estimator=lambda x: len(x),
    ci=None
)
plt.title('Unfulfilled Requests by Time Slot')
plt.ylabel('Number of Requests')
plt.xlabel('Time Slot')
plt.legend(title='Status')
plt.tight_layout()
plt.show()

# 7. Visualization: Supply-Demand Gap by Pickup Point
plt.figure(figsize=(8,5))
sns.countplot(data=df[df['Status'] != 'Trip Completed'], x='Pickup point', hue='Status')
plt.title('Unfulfilled Requests by Pickup Point')
plt.ylabel('Number of Requests')
plt.xlabel('Pickup Point')
plt.legend(title='Status')
plt.tight_layout()
plt.show()

# 8. Hourly Analysis
hourly_gap = df.groupby(['hour', 'Status']).size().unstack(fill_value=0)
hourly_gap['Total'] = hourly_gap.sum(axis=1)
hourly_gap['Gap'] = hourly_gap.get('Cancelled', 0) + hourly_gap.get('No Cars Available', 0)
hourly_gap['Gap %'] = (hourly_gap['Gap'] / hourly_gap['Total']) * 100

plt.figure(figsize=(12,6))
hourly_gap[['Cancelled', 'No Cars Available']].plot(kind='bar', stacked=True, figsize=(12,6))
plt.title('Hourly Unfulfilled Requests')
plt.ylabel('Number of Requests')
plt.xlabel('Hour of Day')
plt.tight_layout()
plt.show()

# 9. Save summary for presentation
pivot_gap.to_excel('uber_supply_demand_gap_summary.xlsx')

# --- End of Script ---

# Insights for Presentation (to be included in slides):
# - Identify peak gap periods and locations
# - Quantify unfulfilled requests by time slot and pickup point
# - Recommend targeted interventions (incentives, shift adjustments)