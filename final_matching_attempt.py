import pandas as pd

# Read the data files
completers_data = pd.read_csv('data/dv261-year12completersvicschools2017.csv')
school_locations = pd.read_csv('data/dv402-SchoolLocations2025.csv')

# Clean the completers data
completers_data.columns = ['VCAA_Code', 'School_Name', 'Sector', 'Locality', 'Total_Completed', 'On_Track_Consenters', 'On_Track_Respondents', 'Bachelor_Enrolled_Percent', 'Deferred_Percent', 'TAFE_VET_Enrolled_Percent', 'Apprentice_Trainee_Percent', 'Employed_Percent', 'Looking_Work_Percent', 'Other_Percent']
completers_data = completers_data.iloc[1:].reset_index(drop=True)

print("=== FINAL MATCHING ATTEMPT ===")

# Convert VCAA_Code to integer for matching
completers_data['VCAA_Code_int'] = pd.to_numeric(completers_data['VCAA_Code'], errors='coerce')

print("Sample VCAA codes (as integers):")
print(completers_data['VCAA_Code_int'].head(10))

print("\nSample School_No from locations:")
print(school_locations['School_No'].head(10))

# Try matching VCAA_Code with School_No
merged_by_number = completers_data.merge(
    school_locations[['School_No', 'LGA_TYPE', 'Education_Sector']], 
    left_on='VCAA_Code_int', 
    right_on='School_No', 
    how='left'
)

print(f"\nMatched by VCAA_Code -> School_No: {len(merged_by_number[merged_by_number['LGA_TYPE'].notna()])}")
print(f"Unknown by VCAA_Code -> School_No: {len(merged_by_number[merged_by_number['LGA_TYPE'].isna()])}")

if len(merged_by_number[merged_by_number['LGA_TYPE'].notna()]) > 0:
    print(f"\nLGA_TYPE distribution:")
    lga_dist = merged_by_number['LGA_TYPE'].value_counts()
    print(lga_dist)
    
    print(f"\nStudent totals by LGA_TYPE:")
    student_totals = merged_by_number.groupby('LGA_TYPE')['Total_Completed'].sum()
    print(student_totals)
    
    print(f"\nSample matched schools:")
    matched_schools = merged_by_number[merged_by_number['LGA_TYPE'].notna()][['School_Name', 'LGA_TYPE', 'Total_Completed']].head(10)
    print(matched_schools)
else:
    print("\nNo matches found. Let's check what VCAA codes we have:")
    print("Unique VCAA codes in completers data:")
    print(completers_data['VCAA_Code'].unique()[:20])
    
    print("\nUnique School_No in locations data:")
    print(school_locations['School_No'].unique()[:20])
    
    # Check if there's any overlap
    completers_codes = set(completers_data['VCAA_Code_int'].dropna())
    locations_codes = set(school_locations['School_No'])
    overlap = completers_codes.intersection(locations_codes)
    print(f"\nOverlapping codes: {len(overlap)}")
    if overlap:
        print(f"Sample overlapping codes: {list(overlap)[:10]}")
