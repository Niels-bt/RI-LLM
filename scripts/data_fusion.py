import dbpedia_fetch_query
import wikidata_fetch_query
from scripts.data_cleaning import master_filter
from scripts.lookup_table import get_lookup_hash_db, get_lookup_hash_wd

db_hash = dbpedia_fetch_query.get_person_data("Marie_Curie")
wd_hash = wikidata_fetch_query.get_person_data("Q7186")

# Filters the tuples using the master_filter
db_hash = master_filter(db_hash, True, False)
wd_hash = master_filter(wd_hash, False, True)

# Fetches the lookup hashes for db and wd
db_lookup_hash = get_lookup_hash_db()
wd_lookup_hash = get_lookup_hash_wd()

print("db to wd fusion:")
print("----------------------------------------------")
# Looping for all labels
for db_label in db_hash:
    print(db_label)
    db_values = db_hash[db_label]

    # Printing all values. We need check if the values is a single string or else a string will be split into chars
    if isinstance(db_values, str):
        print("          " + db_values)
    else:
        for db_value in db_hash[db_label]:
            print("          " + db_value)

        # Checking for matches
        for wd_label in db_lookup_hash[db_label]:
            if wd_label in wd_hash:
                print("-> " + wd_label)
                wd_values = wd_hash[wd_label]

                # Printing all values. We need check if the values is a single string or else a string will be split into chars
                if isinstance(wd_values, str):
                    print("          " + wd_values)
                else:
                    for wd_value in wd_hash[wd_label]:
                        print("          " + wd_value)
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