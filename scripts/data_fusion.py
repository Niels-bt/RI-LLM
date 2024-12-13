import dbpedia_fetch_query
import wikidata_fetch_query
from scripts.data_cleaning import master_filter_db, master_filter_wd, hashmap_values_lower
from scripts.lookup_table import get_lookup_hash_db, get_lookup_hash_wd

db_hash = dbpedia_fetch_query.get_person_data("Coldplay")
wd_hash = wikidata_fetch_query.get_person_data("Q45188")

# Filters the tuples using the master_filter
db_hash = master_filter_db(db_hash)
wd_hash = master_filter_wd(wd_hash)

# Applies .lower() to all values in the hashmaps
db_hash = hashmap_values_lower(db_hash)
wd_hash = hashmap_values_lower(wd_hash)

# Fetches the lookup hashes for db and wd
db_lookup_hash = get_lookup_hash_db()
wd_lookup_hash = get_lookup_hash_wd()

data_fusion = []
for db_label in db_hash:
    # Adding the first label from DBpedia
    labels = [db_label]

    # Adding the first values from DBpedia
    values = []
    db_values = db_hash[db_label]
    if isinstance(db_values, str): values.append(db_values)
    else:
        for db_value in db_values:
            values.append(db_value)

    # We check WIKIDATA for all similar labels
    wd_labels = []
    for wd_label in db_lookup_hash[db_label]:
        if wd_label in wd_hash:
            # Adding all labels from WIKIDATA
            wd_labels.append(wd_label)

            # Adding all values from WIKIDATA
            wd_values = wd_hash[wd_label]
            if isinstance(wd_values, str): values.append(wd_values)
            else:
                for wd_value in wd_values:
                    values.append(wd_value)

            # Removing the dict entry for faster runtime
            del wd_hash[wd_label]

    # We check DBpedia again like WIKIDATA to get both directions
    for wd_label in wd_labels:
        for db_label_2 in wd_lookup_hash[wd_label]:
            if db_label_2 in db_hash:
                # Adding all labels from DBpedia
                labels.append(db_label_2)

                # Adding all values from DBpedia
                db_values_2 = db_hash[db_label_2]
                if isinstance(db_values_2, str): values.append(db_values_2)
                else:
                    for db_value_2 in db_values_2:
                        values.append(db_value_2)

                # Removing the dict entry to avoid duplicates and for faster runtime
                del db_hash[db_label_2]

    labels.extend(wd_labels)

    # All labels and values are appended to the ultimate data_fusion list in this form ((label, label,...), (value, value,...))
    data_fusion.append((labels, values))

for tuples in data_fusion:
    for label in tuples[0]:
        print(label)
    for value in tuples[1]:
        print("     " + value)

'''
print("db to wd fusion:")
print("----------------------------------------------")
# Looping for all labels
for db_label in db_hash:
    print(db_label)
    db_values = db_hash[db_label]

    # Printing all values. We need check if the values is a single string or else the string will be split into chars
    if isinstance(db_values, str):
        print("          " + db_values)
    else:
        for db_value in db_values:
            print("          " + db_value)

    # Checking for matches
    for wd_label in db_lookup_hash[db_label]:
        if wd_label in wd_hash:
            print("-> " + wd_label)
            wd_values = wd_hash[wd_label]

            # Printing all values. We need check if the values is a single string or else the string will be split into chars
            if isinstance(wd_values, str):
                print("          " + wd_values)
            else:
                for wd_value in wd_values:
                    print("          " + wd_value)
print("----------------------------------------------")
print("wd to db fusion:")
print("----------------------------------------------")
# Looping for all labels
for wd_label in wd_hash:
    print(wd_label)
    wd_values = wd_hash[wd_label]

    # Printing all values. We need check if the values is a single string or else the string will be split into chars
    if isinstance(wd_values, str):
        print("          " + wd_values)
    else:
        for wd_value in wd_values:
            print("          " + wd_value)

    # Checking for matches
    for db_label in wd_lookup_hash[wd_label]:
        if db_label in db_hash:
            print("-> " + db_label)
            db_values = db_hash[db_label]

            # Printing all values. We need check if the values is a single string or else the string will be split into chars
            if isinstance(db_values, str):
                print("          " + db_values)
            else:
                for db_value in db_values:
                    print("          " + db_value)
print("----------------------------------------------")
'''



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