import pandas as pd

# Read the data files
completers_data = pd.read_csv('data/dv261-year12completersvicschools2017.csv')
school_locations = pd.read_csv('data/dv402-SchoolLocations2025.csv')

# Clean the completers data
completers_data.columns = ['VCAA_Code', 'School_Name', 'Sector', 'Locality', 'Total_Completed', 'On_Track_Consenters', 'On_Track_Respondents', 'Bachelor_Enrolled_Percent', 'Deferred_Percent', 'TAFE_VET_Enrolled_Percent', 'Apprentice_Trainee_Percent', 'Employed_Percent', 'Looking_Work_Percent', 'Other_Percent']
completers_data = completers_data.iloc[1:].reset_index(drop=True)

print("=== WHERE 'UNKNOWN' COMES FROM ===")
print("\n1. COMPLETERS DATA (Year 12 students):")
print(f"Total schools in completers data: {len(completers_data)}")
print(f"Sample localities from completers data:")
print(completers_data['Locality'].unique()[:10])

print("\n2. SCHOOL LOCATIONS DATA:")
print(f"Total schools in locations data: {len(school_locations)}")
print(f"Sample localities from school locations:")
print(school_locations['Address_Town'].unique()[:10])

# Try to match by locality
merged_data = completers_data.merge(
    school_locations[['Address_Town', 'LGA_TYPE']].drop_duplicates(), 
    left_on='Locality', 
    right_on='Address_Town', 
    how='left'
)

print(f"\n3. MATCHING RESULTS:")
print(f"Total records: {len(merged_data)}")
print(f"Successfully matched: {len(merged_data[merged_data['LGA_TYPE'].notna()])}")
print(f"Unknown metro status: {len(merged_data[merged_data['LGA_TYPE'].isna()])}")

print(f"\n4. METRO STATUS DISTRIBUTION:")
metro_dist = merged_data['LGA_TYPE'].value_counts()
print(metro_dist)

print(f"\n5. STUDENT NUMBERS BY METRO STATUS:")
metro_totals = merged_data.groupby('LGA_TYPE')['Total_Completed'].sum()
print(metro_totals)

print(f"\n6. WHY SO MANY 'UNKNOWN'?")
print("The 'Unknown' category exists because:")
print("- School names don't match exactly between datasets")
print("- Locality names are formatted differently")
print("- Some schools in the completers data aren't in the locations data")
print("- This is common when merging datasets from different sources")

print(f"\n7. BREAKDOWN OF 'UNKNOWN' STUDENTS:")
unknown_data = merged_data[merged_data['LGA_TYPE'].isna()]
unknown_by_sector = unknown_data.groupby('Sector')['Total_Completed'].sum()
print("Unknown students by education sector:")
print(unknown_by_sector)

print(f"\n8. SAMPLE UNKNOWN SCHOOLS:")
unknown_schools = unknown_data[['School_Name', 'Locality', 'Sector', 'Total_Completed']].head(10)
print(unknown_schools)
