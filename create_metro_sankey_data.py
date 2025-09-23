import pandas as pd
import json

# Read the data files
vce_data = pd.read_csv('data/VCE 2024 Results.csv')
completers_data = pd.read_csv('data/dv261-year12completersvicschools2017.csv')
school_locations = pd.read_csv('data/dv402-SchoolLocations2025.csv')

# Clean the completers data
completers_data.columns = ['VCAA_Code', 'School_Name', 'Sector', 'Locality', 'Total_Completed', 'On_Track_Consenters', 'On_Track_Respondents', 'Bachelor_Enrolled_Percent', 'Deferred_Percent', 'TAFE_VET_Enrolled_Percent', 'Apprentice_Trainee_Percent', 'Employed_Percent', 'Looking_Work_Percent', 'Other_Percent']
completers_data = completers_data.iloc[1:].reset_index(drop=True)

# Convert numeric columns
numeric_cols = ['Total_Completed', 'Bachelor_Enrolled_Percent', 'Deferred_Percent', 'TAFE_VET_Enrolled_Percent', 'Apprentice_Trainee_Percent', 'Employed_Percent', 'Looking_Work_Percent', 'Other_Percent']
for col in numeric_cols:
    completers_data[col] = pd.to_numeric(completers_data[col], errors='coerce')

# Merge completers data with school locations to get metro/non-metro status
# We need to match schools between the datasets
merged_data = completers_data.merge(
    school_locations[['School_Name', 'Education_Sector', 'LGA_TYPE']], 
    on='School_Name', 
    how='left'
)

# Fill missing LGA_TYPE with 'Unknown'
merged_data['LGA_TYPE'] = merged_data['LGA_TYPE'].fillna('Unknown')

# Create combined categories: Sector + Metro Status
merged_data['Sector_Metro'] = merged_data['Sector'] + '_' + merged_data['LGA_TYPE']

print("Sample of merged data:")
print(merged_data[['School_Name', 'Sector', 'LGA_TYPE', 'Sector_Metro', 'Total_Completed']].head(10))

# Calculate totals by sector and metro status
sector_metro_totals = merged_data.groupby('Sector_Metro')['Total_Completed'].sum()
print("\nTotal students by sector and metro status:")
print(sector_metro_totals)

# Calculate destination percentages by sector and metro status
sector_metro_destinations = merged_data.groupby('Sector_Metro').agg({
    'Bachelor_Enrolled_Percent': 'mean',
    'TAFE_VET_Enrolled_Percent': 'mean', 
    'Employed_Percent': 'mean',
    'Other_Percent': 'mean'
}).round(1)

print("\nDestination percentages by sector and metro status:")
print(sector_metro_destinations)

# Create the Sankey data with metro/non-metro breakdown
sankey_data = {
    "nodes": [
        {"category": "Government_Metro", "stack": 1, "sort": 1, "labels": "left"},
        {"category": "Government_Non_Metro", "stack": 1, "sort": 2, "labels": "left"},
        {"category": "Catholic_Metro", "stack": 1, "sort": 3, "labels": "left"},
        {"category": "Catholic_Non_Metro", "stack": 1, "sort": 4, "labels": "left"},
        {"category": "Independent_Metro", "stack": 1, "sort": 5, "labels": "left"},
        {"category": "Independent_Non_Metro", "stack": 1, "sort": 6, "labels": "left"},
        {"category": "University", "stack": 2, "sort": 1},
        {"category": "TAFE/VET", "stack": 2, "sort": 2},
        {"category": "Employment", "stack": 2, "sort": 3},
        {"category": "Other Destinations", "stack": 2, "sort": 4}
    ],
    "links": []
}

# Add flows from each sector-metro combination to destinations
for sector_metro in sector_metro_totals.index:
    if sector_metro in sector_metro_totals.index and sector_metro in sector_metro_destinations.index:
        total_students = sector_metro_totals[sector_metro]
        
        # Calculate actual numbers based on percentages
        uni_percent = sector_metro_destinations.loc[sector_metro, 'Bachelor_Enrolled_Percent']
        tafe_percent = sector_metro_destinations.loc[sector_metro, 'TAFE_VET_Enrolled_Percent']
        emp_percent = sector_metro_destinations.loc[sector_metro, 'Employed_Percent']
        other_percent = sector_metro_destinations.loc[sector_metro, 'Other_Percent']
        
        # Convert percentages to actual numbers
        uni_students = int((uni_percent / 100) * total_students)
        tafe_students = int((tafe_percent / 100) * total_students)
        emp_students = int((emp_percent / 100) * total_students)
        other_students = int((other_percent / 100) * total_students)
        
        # Add the flows
        sankey_data["links"].extend([
            {"source": sector_metro, "destination": "University", "value": uni_students},
            {"source": sector_metro, "destination": "TAFE/VET", "value": tafe_students},
            {"source": sector_metro, "destination": "Employment", "value": emp_students},
            {"source": sector_metro, "destination": "Other Destinations", "value": other_students}
        ])

print("\nGenerated Sankey flows with metro/non-metro breakdown:")
for link in sankey_data["links"]:
    print(f"{link['source']} → {link['destination']}: {link['value']} students")

# Save the data
with open('vce_metro_sankey_data.json', 'w') as f:
    json.dump(sankey_data, f, indent=2)

print(f"\nMetro Sankey data saved to vce_metro_sankey_data.json")
print(f"Total flows: {len(sankey_data['links'])}")
