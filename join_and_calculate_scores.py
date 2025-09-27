import pandas as pd
import numpy as np

print("=== JOINING VCE RESULTS WITH SCHOOL LOCATIONS ===")

# Read the datasets
vce_results = pd.read_csv('data/VCE 2024 Results.csv')
school_locations = pd.read_csv('data/dv402-SchoolLocations2025.csv')

print(f"VCE Results: {len(vce_results)} schools")
print(f"School Locations: {len(school_locations)} schools")

# Clean the VCE data - filter out invalid study scores
print("\n=== CLEANING VCE DATA ===")
print("Study score values before cleaning:")
print(vce_results['Median VCE study score'].value_counts().head(10))

# Filter out invalid study scores
valid_scores = vce_results[
    (vce_results['Median VCE study score'] != 'I/D') & 
    (vce_results['Median VCE study score'] != '-') & 
    (vce_results['Median VCE study score'].notna()) &
    (vce_results['Median VCE study score'] != '')
].copy()

print(f"\nValid study scores: {len(valid_scores)} schools")

# Convert study scores to numeric
valid_scores['Median VCE study score'] = pd.to_numeric(valid_scores['Median VCE study score'], errors='coerce')
valid_scores = valid_scores.dropna(subset=['Median VCE study score'])

print(f"After numeric conversion: {len(valid_scores)} schools")

# Clean school names for better matching
def clean_school_name(name):
    if pd.isna(name):
        return ""
    return str(name).strip().upper()

valid_scores['School_Clean'] = valid_scores['School'].apply(clean_school_name)
school_locations['School_Name_Clean'] = school_locations['School_Name'].apply(clean_school_name)

print("\n=== ATTEMPTING TO JOIN DATASETS ===")

# Try exact match first
exact_match = valid_scores.merge(
    school_locations, 
    left_on='School_Clean', 
    right_on='School_Name_Clean', 
    how='inner'
)

print(f"Exact matches: {len(exact_match)} schools")

# Show some examples of matches
print("\nSample matches:")
print(exact_match[['School', 'School_Name', 'Locality', 'Address_Town', 'Median VCE study score']].head())

# Calculate study scores by suburb
print("\n=== CALCULATING STUDY SCORES BY SUBURB ===")

# Use Address_Town as the suburb identifier
suburb_scores = exact_match.groupby('Address_Town').agg({
    'Median VCE study score': ['mean', 'median', 'count', 'std'],
    'School_Name': 'count'
}).round(2)

# Flatten column names
suburb_scores.columns = ['avg_study_score', 'median_study_score', 'school_count', 'std_study_score', 'total_schools']
suburb_scores = suburb_scores.reset_index()

# Rename Address_Town to suburb
suburb_scores = suburb_scores.rename(columns={'Address_Town': 'suburb'})

print(f"Suburbs with study score data: {len(suburb_scores)}")
print("\nTop 10 suburbs by average study score:")
top_suburbs = suburb_scores.nlargest(10, 'avg_study_score')
print(top_suburbs[['suburb', 'avg_study_score', 'school_count']])

print("\nBottom 10 suburbs by average study score:")
bottom_suburbs = suburb_scores.nsmallest(10, 'avg_study_score')
print(bottom_suburbs[['suburb', 'avg_study_score', 'school_count']])

# Save the results
suburb_scores.to_csv('data/suburb_study_scores_joined.csv', index=False)
print(f"\nSaved suburb study scores to: data/suburb_study_scores_joined.csv")

# Show summary statistics
print(f"\n=== SUMMARY STATISTICS ===")
print(f"Total suburbs with data: {len(suburb_scores)}")
print(f"Average study score across all suburbs: {suburb_scores['avg_study_score'].mean():.2f}")
print(f"Median study score across all suburbs: {suburb_scores['median_study_score'].median():.2f}")
print(f"Highest study score: {suburb_scores['avg_study_score'].max():.2f}")
print(f"Lowest study score: {suburb_scores['avg_study_score'].min():.2f}")

# Show distribution by school count
print(f"\nDistribution by number of schools per suburb:")
print(suburb_scores['school_count'].value_counts().sort_index())

# Show some detailed examples
print(f"\n=== DETAILED EXAMPLES ===")
print("Suburbs with multiple schools:")
multi_school = suburb_scores[suburb_scores['school_count'] > 1].sort_values('avg_study_score', ascending=False)
print(multi_school[['suburb', 'avg_study_score', 'school_count', 'std_study_score']].head(10))
