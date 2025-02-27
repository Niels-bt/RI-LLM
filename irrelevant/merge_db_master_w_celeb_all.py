import pandas as pd

db_master = pd.read_csv('../scripts/master_db.csv')
dbpedia_celeb = pd.read_csv('../topics/celebrities/dbpedia_celeb_all_properties.csv')

print("db_master columns:", db_master.columns)
print("dbpedia_celeb columns:", dbpedia_celeb.columns)


# merge the two dataFrames on the 'Property_Name' column
merged_df = pd.merge(db_master, dbpedia_celeb, on=' Property_Name', how='left')

# save to csv file
merged_df.to_csv('corrected_master_db.csv', index=False)

print("Merge completed. The result is saved in 'corrected_master_db.csv'.")
