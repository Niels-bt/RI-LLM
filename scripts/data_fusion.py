import dbpedia_fetch_query
import wikidata_fetch_query
from scripts.data_cleaning import hash_to_list, master_filter

db_hash = dbpedia_fetch_query.get_person_data("Marie_Curie")
wd_hash = wikidata_fetch_query.get_person_data("Q7186")

# Filters the tuples using the master_filter
db_hash = master_filter(db_hash, True, False)
wd_hash = master_filter(wd_hash, False, True)



# Creates lists of (label, value) from the hashmap
db_list = hash_to_list(db_hash)
wd_list = hash_to_list(wd_hash)
'''
# prepares the tuples and transforms them into lists
db_list = prep_db(db_hash)
wd_list = prep_wd(wd_hash)


# replaces the properties by their lemmas
wd_list = lemmatization(wd_list)
db_list = lemmatization(db_list)


# transforms the tuples into a hashmap
db_hash_new = {}
wd_hash_new = {}
for i,i2 in db_list:
    db_hash_new[i]=i2

for i,i2 in wd_list:
    wd_hash_new[i]=i2


# simple property comparison
print("-"*90)
for prop in wd_hash_new:
    if prop in db_hash_new:
        print("prop is", prop,"wd_val", wd_hash_new[prop], "db", db_hash_new[prop])
    else:
        print("prop is", prop, "wdata", wd_hash_new[prop], "wikidata", "notfound")
'''