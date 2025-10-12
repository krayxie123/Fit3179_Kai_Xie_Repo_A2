import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

# Melbourne CBD coordinates
melbourne_cbd_lat = -37.8136
melbourne_cbd_lon = 144.9631

# Read the data
print("Loading VCE School Results...")
vce_data = pd.read_csv('data/VCE_School_Results.csv')

print("Loading School Locations...")
school_locations = pd.read_csv('data/dv402-SchoolLocations2025.csv')

print(f"VCE data shape: {vce_data.shape}")
print(f"School locations shape: {school_locations.shape}")

# Clean and filter VCE data
print("Processing VCE data...")
vce_clean = vce_data.copy()
vce_clean['median_vce_ss'] = pd.to_numeric(vce_clean['median_vce_ss'], errors='coerce')
vce_clean = vce_clean.dropna(subset=['median_vce_ss'])
vce_clean = vce_clean[vce_clean['median_vce_ss'] > 0]

print(f"Clean VCE data shape: {vce_clean.shape}")

# Try different matching strategies
print("Attempting school name matching...")

# Strategy 1: Direct school name matching
merged1 = vce_clean.merge(
    school_locations[['School_Name', 'X', 'Y', 'Education_Sector']], 
    left_on='school', 
    right_on='School_Name', 
    how='inner'
)

print(f"Direct name matching: {merged1.shape[0]} records")

# Strategy 2: Try matching by locality
merged2 = vce_clean.merge(
    school_locations[['Address_Town', 'X', 'Y', 'Education_Sector']], 
    left_on='locality', 
    right_on='Address_Town', 
    how='inner'
)

print(f"Locality matching: {merged2.shape[0]} records")

# Use the best matching strategy
if merged1.shape[0] > merged2.shape[0]:
    merged_data = merged1
    print("Using direct school name matching")
else:
    merged_data = merged2
    print("Using locality matching")

# Calculate distance for each record
print("Calculating distances...")
merged_data['distance_km'] = merged_data.apply(
    lambda row: haversine(melbourne_cbd_lon, melbourne_cbd_lat, row['X'], row['Y']),
    axis=1
)

# Aggregate by school
print("Aggregating data by school...")
school_aggregated = merged_data.groupby(['school', 'Education_Sector']).agg({
    'median_vce_ss': 'mean',
    'distance_km': 'mean',
    'year': 'count'
}).reset_index()

school_aggregated.columns = ['school', 'education_sector', 'avg_median_score', 'avg_distance_km', 'years_of_data']

# Filter for schools with enough data
school_aggregated = school_aggregated[school_aggregated['years_of_data'] >= 2]

# Rank schools by performance
school_aggregated = school_aggregated.sort_values('avg_median_score', ascending=False)
school_aggregated['performance_rank'] = range(1, len(school_aggregated) + 1)

# Take top 100 schools
top_schools = school_aggregated.head(100)

print(f"Final dataset shape: {top_schools.shape}")
print(f"Distance range: {top_schools['avg_distance_km'].min():.1f} - {top_schools['avg_distance_km'].max():.1f} km")
print(f"Score range: {top_schools['avg_median_score'].min():.1f} - {top_schools['avg_median_score'].max():.1f}")

# Save the processed data
output_file = 'data/processed_distance_data.csv'
top_schools.to_csv(output_file, index=False)
print(f"Saved processed data to {output_file}")

# Display sample data
print("\nSample data:")
print(top_schools.head(10))
