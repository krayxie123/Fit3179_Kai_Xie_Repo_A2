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

# Try to match by locality
merged_data = completers_data.merge(
    school_locations[['Address_Town', 'LGA_TYPE']].drop_duplicates(), 
    left_on='Locality', 
    right_on='Address_Town', 
    how='left'
)

# Fill missing LGA_TYPE with 'Unknown'
merged_data['LGA_TYPE'] = merged_data['LGA_TYPE'].fillna('Unknown')

# Create the Sankey data with Metro/Non-Metro → Education Sectors → Destinations flow
sankey_data = {
    "nodes": [
        {"category": "Metro", "stack": 1, "sort": 1, "labels": "left"},
        {"category": "Non Metro", "stack": 1, "sort": 2, "labels": "left"},
        {"category": "Unknown", "stack": 1, "sort": 3, "labels": "left"},
        {"category": "Government", "stack": 2, "sort": 1},
        {"category": "Catholic", "stack": 2, "sort": 2},
        {"category": "Independent", "stack": 2, "sort": 3},
        {"category": "Other", "stack": 2, "sort": 4},
        {"category": "University", "stack": 3, "sort": 1},
        {"category": "TAFE/VET", "stack": 3, "sort": 2},
        {"category": "Employment", "stack": 3, "sort": 3},
        {"category": "Other Destinations", "stack": 3, "sort": 4}
    ],
    "links": []
}

# Calculate totals by metro status
metro_totals = merged_data.groupby('LGA_TYPE')['Total_Completed'].sum()
print("Total students by metro status:")
print(metro_totals)

# Calculate totals by education sector
sector_totals = merged_data.groupby('Sector')['Total_Completed'].sum()
print("\nTotal students by education sector:")
print(sector_totals)

# Calculate how metro/non-metro flows into education sectors
metro_sector_flow = merged_data.groupby(['LGA_TYPE', 'Sector'])['Total_Completed'].sum().reset_index()
print("\nMetro → Education Sector flows:")
print(metro_sector_flow)

# Calculate how education sectors flow to destinations
sector_destinations = merged_data.groupby('Sector').agg({
    'Bachelor_Enrolled_Percent': 'mean',
    'TAFE_VET_Enrolled_Percent': 'mean', 
    'Employed_Percent': 'mean',
    'Other_Percent': 'mean'
}).round(1)

print("\nEducation Sector → Destination percentages:")
print(sector_destinations)

# Add flows from Metro/Non-Metro to Education Sectors
for _, row in metro_sector_flow.iterrows():
    metro_type = row['LGA_TYPE']
    sector = row['Sector']
    value = row['Total_Completed']
    
    # Map sector codes to names
    sector_names = {'G': 'Government', 'C': 'Catholic', 'I': 'Independent', 'A': 'Other'}
    sector_name = sector_names.get(sector, sector)
    
    sankey_data["links"].append({
        "source": metro_type,
        "destination": sector_name,
        "value": int(value)
    })

# Add flows from Education Sectors to Destinations
for sector in sector_destinations.index:
    sector_names = {'G': 'Government', 'C': 'Catholic', 'I': 'Independent', 'A': 'Other'}
    sector_name = sector_names.get(sector, sector)
    
    # Get total students for this sector
    total_students = sector_totals[sector]
    
    # Calculate actual numbers based on percentages
    uni_percent = sector_destinations.loc[sector, 'Bachelor_Enrolled_Percent']
    tafe_percent = sector_destinations.loc[sector, 'TAFE_VET_Enrolled_Percent']
    emp_percent = sector_destinations.loc[sector, 'Employed_Percent']
    other_percent = sector_destinations.loc[sector, 'Other_Percent']
    
    # Convert percentages to actual numbers
    uni_students = int((uni_percent / 100) * total_students)
    tafe_students = int((tafe_percent / 100) * total_students)
    emp_students = int((emp_percent / 100) * total_students)
    other_students = int((other_percent / 100) * total_students)
    
    # Add the flows
    sankey_data["links"].extend([
        {"source": sector_name, "destination": "University", "value": uni_students},
        {"source": sector_name, "destination": "TAFE/VET", "value": tafe_students},
        {"source": sector_name, "destination": "Employment", "value": emp_students},
        {"source": sector_name, "destination": "Other Destinations", "value": other_students}
    ])

print("\nGenerated Sankey flows:")
for link in sankey_data["links"]:
    print(f"{link['source']} → {link['destination']}: {link['value']} students")

# Save the data
with open('metro_education_sankey_data.json', 'w') as f:
    json.dump(sankey_data, f, indent=2)

print(f"\nMetro → Education → Destinations Sankey data saved to metro_education_sankey_data.json")
print(f"Total flows: {len(sankey_data['links'])}")
