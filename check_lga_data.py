import pandas as pd

# Read the school locations data
school_locations = pd.read_csv('data/dv402-SchoolLocations2025.csv')

print("=== LGA_TYPE DATA IN SCHOOL LOCATIONS ===")
print(f"Total schools: {len(school_locations)}")
print(f"LGA_TYPE column exists: {'LGA_TYPE' in school_locations.columns}")

print("\nLGA_TYPE values:")
lga_counts = school_locations['LGA_TYPE'].value_counts()
print(lga_counts)

print(f"\nSample LGA_TYPE data:")
print(school_locations[['School_Name', 'Address_Town', 'LGA_TYPE']].head(10))

print(f"\nUnique LGA_TYPE values:")
print(school_locations['LGA_TYPE'].unique())

# Check if there are any missing LGA_TYPE values
missing_lga = school_locations['LGA_TYPE'].isna().sum()
print(f"\nMissing LGA_TYPE values: {missing_lga}")

# Check the completers data
completers_data = pd.read_csv('data/dv261-year12completersvicschools2017.csv')
completers_data.columns = ['VCAA_Code', 'School_Name', 'Sector', 'Locality', 'Total_Completed', 'On_Track_Consenters', 'On_Track_Respondents', 'Bachelor_Enrolled_Percent', 'Deferred_Percent', 'TAFE_VET_Enrolled_Percent', 'Apprentice_Trainee_Percent', 'Employed_Percent', 'Looking_Work_Percent', 'Other_Percent']
completers_data = completers_data.iloc[1:].reset_index(drop=True)

print(f"\n=== COMPLETERS DATA ===")
print(f"Total schools: {len(completers_data)}")
print(f"Sample school names from completers:")
print(completers_data['School_Name'].head(10))

print(f"\nSample school names from locations:")
print(school_locations['School_Name'].head(10))

# Try matching by school name instead of locality
print(f"\n=== TRYING SCHOOL NAME MATCHING ===")
merged_by_name = completers_data.merge(
    school_locations[['School_Name', 'LGA_TYPE', 'Education_Sector']], 
    on='School_Name', 
    how='left'
)

print(f"Matched by school name: {len(merged_by_name[merged_by_name['LGA_TYPE'].notna()])}")
print(f"Unknown by school name: {len(merged_by_name[merged_by_name['LGA_TYPE'].isna()])}")

if len(merged_by_name[merged_by_name['LGA_TYPE'].notna()]) > 0:
    print(f"\nLGA_TYPE distribution from school name matching:")
    lga_dist = merged_by_name['LGA_TYPE'].value_counts()
    print(lga_dist)
    
    print(f"\nStudent totals by LGA_TYPE:")
    student_totals = merged_by_name.groupby('LGA_TYPE')['Total_Completed'].sum()
    print(student_totals)
