import pandas as pd
import json

# Read both datasets
school_locations = pd.read_csv('data/dv402-SchoolLocations2025.csv')
completers_data = pd.read_csv('data/dv261-year12completersvicschools2017.csv')

# Clean the completers data
completers_data.columns = ['VCAA_Code', 'School_Name', 'Sector', 'Locality', 'Total_Completed', 'On_Track_Consenters', 'On_Track_Respondents', 'Bachelor_Enrolled_Percent', 'Deferred_Percent', 'TAFE_VET_Enrolled_Percent', 'Apprentice_Trainee_Percent', 'Employed_Percent', 'Looking_Work_Percent', 'Other_Percent']
completers_data = completers_data.iloc[1:].reset_index(drop=True)

# Convert numeric columns
numeric_cols = ['Total_Completed', 'Bachelor_Enrolled_Percent', 'Deferred_Percent', 'TAFE_VET_Enrolled_Percent', 'Apprentice_Trainee_Percent', 'Employed_Percent', 'Looking_Work_Percent', 'Other_Percent']
for col in numeric_cols:
    completers_data[col] = pd.to_numeric(completers_data[col], errors='coerce')

print("=== CREATING COMPLETE SANKEY WITH EDUCATION SECTORS ===")

# Get school counts by metro/education sector from locations data
metro_sector_counts = school_locations.groupby(['LGA_TYPE', 'Education_Sector']).size().reset_index(name='school_count')
print("Metro → Education Sector flows (school counts):")
print(metro_sector_counts)

# Get destination percentages by education sector from completers data
sector_destinations = completers_data.groupby('Sector').agg({
    'Bachelor_Enrolled_Percent': 'mean',
    'TAFE_VET_Enrolled_Percent': 'mean', 
    'Employed_Percent': 'mean',
    'Other_Percent': 'mean'
}).round(1)

print("\nEducation Sector → Destination percentages:")
print(sector_destinations)

# Get total students by sector
sector_totals = completers_data.groupby('Sector')['Total_Completed'].sum()
print("\nTotal students by sector:")
print(sector_totals)

# Create the complete Sankey data
sankey_data = {
    "nodes": [
        {"category": "Metro", "stack": 1, "sort": 1, "labels": "left"},
        {"category": "Non Metro", "stack": 1, "sort": 2, "labels": "left"},
        {"category": "Government", "stack": 2, "sort": 1},
        {"category": "Catholic", "stack": 2, "sort": 2},
        {"category": "Independent", "stack": 2, "sort": 3},
        {"category": "University", "stack": 3, "sort": 1},
        {"category": "TAFE/VET", "stack": 3, "sort": 2},
        {"category": "Employment", "stack": 3, "sort": 3},
        {"category": "Other Destinations", "stack": 3, "sort": 4}
    ],
    "links": []
}

# Add flows from Metro/Non-Metro to Education Sectors (using school counts as proxy)
for _, row in metro_sector_counts.iterrows():
    metro_type = row['LGA_TYPE']
    sector = row['Education_Sector']
    count = row['school_count']
    
    # Scale up the school counts to represent student numbers
    # Use a multiplier to make the flows more visible
    student_estimate = count * 50  # Assume 50 students per school on average
    
    sankey_data["links"].append({
        "source": metro_type,
        "destination": sector,
        "value": int(student_estimate)
    })

# Add flows from Education Sectors to Destinations (using real student data)
sector_mapping = {'G': 'Government', 'C': 'Catholic', 'I': 'Independent', 'A': 'Other'}
for sector_code, sector_name in sector_mapping.items():
    if sector_code in sector_totals.index and sector_code in sector_destinations.index:
        total_students = sector_totals[sector_code]
        
        # Calculate actual numbers based on percentages
        uni_percent = sector_destinations.loc[sector_code, 'Bachelor_Enrolled_Percent']
        tafe_percent = sector_destinations.loc[sector_code, 'TAFE_VET_Enrolled_Percent']
        emp_percent = sector_destinations.loc[sector_code, 'Employed_Percent']
        other_percent = sector_destinations.loc[sector_code, 'Other_Percent']
        
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

print("\nGenerated complete Sankey flows:")
for link in sankey_data["links"]:
    print(f"{link['source']} → {link['destination']}: {link['value']}")

# Save the data
with open('complete_sankey_data.json', 'w') as f:
    json.dump(sankey_data, f, indent=2)

print(f"\nComplete Sankey data saved to complete_sankey_data.json")
print(f"Total flows: {len(sankey_data['links'])}")
