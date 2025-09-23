import pandas as pd
import json

# Read the data files
vce_data = pd.read_csv('data/VCE 2024 Results.csv')
completers_data = pd.read_csv('data/dv261-year12completersvicschools2017.csv')
school_locations = pd.read_csv('data/dv402-SchoolLocations2025.csv')

# Clean the completers data - it has header issues
completers_data.columns = ['VCAA_Code', 'School_Name', 'Sector', 'Locality', 'Total_Completed', 'On_Track_Consenters', 'On_Track_Respondents', 'Bachelor_Enrolled_Percent', 'Deferred_Percent', 'TAFE_VET_Enrolled_Percent', 'Apprentice_Trainee_Percent', 'Employed_Percent', 'Looking_Work_Percent', 'Other_Percent']

# Remove the first row which is just column names
completers_data = completers_data.iloc[1:].reset_index(drop=True)

# Convert numeric columns
numeric_cols = ['Total_Completed', 'On_Track_Consenters', 'On_Track_Respondents', 'Bachelor_Enrolled_Percent', 'Deferred_Percent', 'TAFE_VET_Enrolled_Percent', 'Apprentice_Trainee_Percent', 'Employed_Percent', 'Looking_Work_Percent', 'Other_Percent']
for col in numeric_cols:
    completers_data[col] = pd.to_numeric(completers_data[col], errors='coerce')

# Get VCE enrollment data by school sector
# We need to match schools between datasets
print("VCE Data columns:", vce_data.columns.tolist())
print("Completers Data columns:", completers_data.columns.tolist())
print("School Locations columns:", school_locations.columns.tolist())

# Let's look at some sample data
print("\nVCE Data sample:")
print(vce_data[['School', 'Number of students enrolled in at least one VCE or VCE Vocational Major (VM) study or VCE VET program at Units 3 and 4 level']].head())

print("\nCompleters Data sample:")
print(completers_data[['School_Name', 'Sector', 'Total_Completed']].head())

print("\nSchool Locations sample:")
print(school_locations[['School_Name', 'Education_Sector']].head())

# Calculate totals by sector from completers data
sector_totals = completers_data.groupby('Sector')['Total_Completed'].sum()
print("\nTotal students by sector:")
print(sector_totals)

# Calculate destination percentages by sector
sector_destinations = completers_data.groupby('Sector').agg({
    'Bachelor_Enrolled_Percent': 'mean',
    'TAFE_VET_Enrolled_Percent': 'mean', 
    'Employed_Percent': 'mean',
    'Other_Percent': 'mean'
}).round(1)

print("\nAverage destination percentages by sector:")
print(sector_destinations)
