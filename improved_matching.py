import pandas as pd

# Read the data files
completers_data = pd.read_csv('data/dv261-year12completersvicschools2017.csv')
school_locations = pd.read_csv('data/dv402-SchoolLocations2025.csv')

# Clean the completers data
completers_data.columns = ['VCAA_Code', 'School_Name', 'Sector', 'Locality', 'Total_Completed', 'On_Track_Consenters', 'On_Track_Respondents', 'Bachelor_Enrolled_Percent', 'Deferred_Percent', 'TAFE_VET_Enrolled_Percent', 'Apprentice_Trainee_Percent', 'Employed_Percent', 'Looking_Work_Percent', 'Other_Percent']
completers_data = completers_data.iloc[1:].reset_index(drop=True)

print("=== TRYING DIFFERENT MATCHING STRATEGIES ===")

# Strategy 1: Try matching by VCAA Code if it exists
print("\n1. CHECKING FOR VCAA CODE IN LOCATIONS DATA:")
if 'VCAA_Code' in school_locations.columns:
    print("VCAA_Code found in locations data!")
    merged_by_code = completers_data.merge(
        school_locations[['VCAA_Code', 'LGA_TYPE', 'Education_Sector']], 
        on='VCAA_Code', 
        how='left'
    )
    print(f"Matched by VCAA Code: {len(merged_by_code[merged_by_code['LGA_TYPE'].notna()])}")
else:
    print("No VCAA_Code in locations data")

# Strategy 2: Try fuzzy matching on school names
print("\n2. TRYING FUZZY MATCHING:")
from difflib import get_close_matches

# Get some sample matches
completers_names = completers_data['School_Name'].tolist()[:10]
locations_names = school_locations['School_Name'].tolist()

print("Sample fuzzy matches:")
for name in completers_names[:5]:
    matches = get_close_matches(name, locations_names, n=3, cutoff=0.6)
    print(f"'{name}' -> {matches}")

# Strategy 3: Try matching by locality and sector
print("\n3. TRYING LOCATION + SECTOR MATCHING:")
merged_by_loc_sector = completers_data.merge(
    school_locations[['Address_Town', 'Education_Sector', 'LGA_TYPE']].drop_duplicates(), 
    left_on=['Locality', 'Sector'], 
    right_on=['Address_Town', 'Education_Sector'], 
    how='left'
)

print(f"Matched by Locality + Sector: {len(merged_by_loc_sector[merged_by_loc_sector['LGA_TYPE'].notna()])}")
print(f"Unknown by Locality + Sector: {len(merged_by_loc_sector[merged_by_loc_sector['LGA_TYPE'].isna()])}")

if len(merged_by_loc_sector[merged_by_loc_sector['LGA_TYPE'].notna()]) > 0:
    print(f"\nLGA_TYPE distribution:")
    lga_dist = merged_by_loc_sector['LGA_TYPE'].value_counts()
    print(lga_dist)
    
    print(f"\nStudent totals by LGA_TYPE:")
    student_totals = merged_by_loc_sector.groupby('LGA_TYPE')['Total_Completed'].sum()
    print(student_totals)

# Strategy 4: Check if we can use the VCAA Code from completers data
print("\n4. CHECKING VCAA CODES IN COMPLETERS DATA:")
print("Sample VCAA codes from completers:")
print(completers_data['VCAA_Code'].head(10))

# Check if locations data has any identifier that might match
print("\n5. CHECKING LOCATIONS DATA COLUMNS:")
print("Available columns in locations data:")
print(school_locations.columns.tolist())

# Check if there's a school number that might match VCAA code
if 'School_No' in school_locations.columns:
    print(f"\nSchool_No in locations data:")
    print(school_locations['School_No'].head(10))
    
    # Try matching VCAA_Code with School_No
    merged_by_number = completers_data.merge(
        school_locations[['School_No', 'LGA_TYPE', 'Education_Sector']], 
        left_on='VCAA_Code', 
        right_on='School_No', 
        how='left'
    )
    print(f"Matched by VCAA_Code -> School_No: {len(merged_by_number[merged_by_number['LGA_TYPE'].notna()])}")
    
    if len(merged_by_number[merged_by_number['LGA_TYPE'].notna()]) > 0:
        print(f"\nLGA_TYPE distribution from number matching:")
        lga_dist = merged_by_number['LGA_TYPE'].value_counts()
        print(lga_dist)
        
        print(f"\nStudent totals by LGA_TYPE:")
        student_totals = merged_by_number.groupby('LGA_TYPE')['Total_Completed'].sum()
        print(student_totals)
