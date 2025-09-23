import pandas as pd
import json

# Read the school locations data directly
school_locations = pd.read_csv('data/dv402-SchoolLocations2025.csv')

print("=== USING SCHOOL LOCATIONS DATA DIRECTLY ===")
print(f"Total schools: {len(school_locations)}")

# Check the data
print("\nLGA_TYPE distribution:")
lga_dist = school_locations['LGA_TYPE'].value_counts()
print(lga_dist)

print("\nEducation_Sector distribution:")
sector_dist = school_locations['Education_Sector'].value_counts()
print(sector_dist)

# Create a Sankey diagram showing Metro/Non-Metro → Education Sectors
# Since we don't have student numbers in this dataset, we'll use school counts
sankey_data = {
    "nodes": [
        {"category": "Metro", "stack": 1, "sort": 1, "labels": "left"},
        {"category": "Non Metro", "stack": 1, "sort": 2, "labels": "left"},
        {"category": "Government", "stack": 2, "sort": 1},
        {"category": "Catholic", "stack": 2, "sort": 2},
        {"category": "Independent", "stack": 2, "sort": 3}
    ],
    "links": []
}

# Calculate flows from Metro/Non-Metro to Education Sectors
metro_sector_flow = school_locations.groupby(['LGA_TYPE', 'Education_Sector']).size().reset_index(name='school_count')

print("\nMetro → Education Sector flows (school counts):")
for _, row in metro_sector_flow.iterrows():
    metro_type = row['LGA_TYPE']
    sector = row['Education_Sector']
    count = row['school_count']
    
    sankey_data["links"].append({
        "source": metro_type,
        "destination": sector,
        "value": int(count)
    })
    
    print(f"{metro_type} → {sector}: {count} schools")

# Save the data
with open('direct_sankey_data.json', 'w') as f:
    json.dump(sankey_data, f, indent=2)

print(f"\nDirect Sankey data saved to direct_sankey_data.json")
print(f"Total flows: {len(sankey_data['links'])}")

# Also create a more detailed version with all the data we have
print("\n=== DETAILED BREAKDOWN ===")
print("Metro schools by sector:")
metro_breakdown = school_locations[school_locations['LGA_TYPE'] == 'Metro']['Education_Sector'].value_counts()
print(metro_breakdown)

print("\nNon Metro schools by sector:")
non_metro_breakdown = school_locations[school_locations['LGA_TYPE'] == 'Non Metro']['Education_Sector'].value_counts()
print(non_metro_breakdown)
