import pandas as pd
import json

# Read the VCE 2024 Results data
vce_data = pd.read_csv('data/VCE 2024 Results.csv')

# Read the Year 12 completers data
completers_data = pd.read_csv('data/dv261-year12completersvicschools2017.csv')

# Read school locations to get education sectors
school_locations = pd.read_csv('data/dv402-SchoolLocations2025.csv')

print("VCE 2024 Results columns:")
print(vce_data.columns.tolist())
print("\nYear 12 Completers columns:")
print(completers_data.columns.tolist())
print("\nSchool Locations columns:")
print(school_locations.columns.tolist())

# Let's look at the data structure
print("\nVCE 2024 Results sample:")
print(vce_data.head())
print("\nYear 12 Completers sample:")
print(completers_data.head())
print("\nSchool Locations sample:")
print(school_locations.head())
