import pandas as pd
import json

# Read the data files
vce_data = pd.read_csv('data/VCE 2024 Results.csv')
completers_data = pd.read_csv('data/dv261-year12completersvicschools2017.csv')

# Clean the completers data
completers_data.columns = ['VCAA_Code', 'School_Name', 'Sector', 'Locality', 'Total_Completed', 'On_Track_Consenters', 'On_Track_Respondents', 'Bachelor_Enrolled_Percent', 'Deferred_Percent', 'TAFE_VET_Enrolled_Percent', 'Apprentice_Trainee_Percent', 'Employed_Percent', 'Looking_Work_Percent', 'Other_Percent']
completers_data = completers_data.iloc[1:].reset_index(drop=True)

# Convert numeric columns
numeric_cols = ['Total_Completed', 'Bachelor_Enrolled_Percent', 'Deferred_Percent', 'TAFE_VET_Enrolled_Percent', 'Apprentice_Trainee_Percent', 'Employed_Percent', 'Looking_Work_Percent', 'Other_Percent']
for col in numeric_cols:
    completers_data[col] = pd.to_numeric(completers_data[col], errors='coerce')

# Calculate real totals by sector
sector_totals = completers_data.groupby('Sector')['Total_Completed'].sum()
print("Real student totals by sector:")
print(sector_totals)

# Calculate average destination percentages by sector
sector_destinations = completers_data.groupby('Sector').agg({
    'Bachelor_Enrolled_Percent': 'mean',
    'TAFE_VET_Enrolled_Percent': 'mean', 
    'Employed_Percent': 'mean',
    'Other_Percent': 'mean'
}).round(1)

print("\nReal destination percentages by sector:")
print(sector_destinations)

# Create the Sankey data with real numbers
# Map sectors: G=Government, C=Catholic, I=Independent, A=Other
sector_mapping = {'G': 'Government', 'C': 'Catholic', 'I': 'Independent', 'A': 'Other'}

# Calculate flows from sectors to destinations
sankey_data = {
    "nodes": [
        {"category": "Government", "stack": 1, "sort": 1, "labels": "left"},
        {"category": "Catholic", "stack": 1, "sort": 2, "labels": "left"},
        {"category": "Independent", "stack": 1, "sort": 3, "labels": "left"},
        {"category": "Other", "stack": 1, "sort": 4, "labels": "left"},
        {"category": "University", "stack": 2, "sort": 1},
        {"category": "TAFE/VET", "stack": 2, "sort": 2},
        {"category": "Employment", "stack": 2, "sort": 3},
        {"category": "Other Destinations", "stack": 2, "sort": 4}
    ],
    "links": []
}

# Add flows from each sector to destinations
for sector_code, sector_name in sector_mapping.items():
    if sector_code in sector_totals.index:
        total_students = sector_totals[sector_code]
        if sector_code in sector_destinations.index:
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

print("\nGenerated Sankey flows:")
for link in sankey_data["links"]:
    print(f"{link['source']} → {link['destination']}: {link['value']} students")

# Save the data
with open('vce_real_sankey_data.json', 'w') as f:
    json.dump(sankey_data, f, indent=2)

print(f"\nReal Sankey data saved to vce_real_sankey_data.json")
print(f"Total flows: {len(sankey_data['links'])}")
