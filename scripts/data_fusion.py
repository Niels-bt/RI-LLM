import dbpedia_fetch_query
import wikidata_fetch_query
from scripts.data_cleaning import master_filter_db, master_filter_wd, data_cleaning
from scripts.lookup_table import get_lookup_hash_db, get_lookup_hash_wd


def data_fusion(db_string, wd_string):
    # Fetches the hashmaps for DBpedia and WIKIDATA
    db_hash = dbpedia_fetch_query.get_person_data(db_string)
    wd_hash = wikidata_fetch_query.get_person_data(wd_string)

    # Filters the tuples using the master_filter
    db_hash = master_filter_db(db_hash)
    wd_hash = master_filter_wd(wd_hash)

    # Cleans the data and applies lemmatization
    db_hash = data_cleaning(db_hash)
    wd_hash = data_cleaning(wd_hash)

    # Fetches the lookup hashes for db and wd
    db_lookup_hash = get_lookup_hash_db()
    wd_lookup_hash = get_lookup_hash_wd()

    finished_data = []
    for db_label in list(db_hash.keys()):
        # Adding the first label from DBpedia
        labels = [db_label]

        # Adding the first values from DBpedia
        values = []
        matched_values = []
        append_values(values, matched_values, db_hash[db_label])

        # Removing the dict entry to avoid duplicates and for faster runtime
        del db_hash[db_label]

        # We check WIKIDATA for all similar labels
        wd_labels = []
        for wd_label in db_lookup_hash[db_label]:
            if wd_label in wd_hash:
                # Adding all labels from WIKIDATA
                wd_labels.append(wd_label)

                # Adding all values from WIKIDATA
                append_values(values, matched_values, wd_hash[wd_label])

                # Removing the dict entry for faster runtime
                del wd_hash[wd_label]

        # We check DBpedia again like WIKIDATA to get both directions
        for wd_label in wd_labels:
            for db_label_2 in wd_lookup_hash[wd_label]:
                if db_label_2 in db_hash:
                    # Adding all labels from DBpedia
                    labels.append(db_label_2)

                    # Adding all values from DBpedia
                    append_values(values, matched_values, db_hash[db_label_2])

                    # Removing the dict entry to avoid duplicates and for faster runtime
                    del db_hash[db_label_2]

        labels.extend(wd_labels)

        # All labels and values are appended to the ultimate data_fusion list in this form ((label, label,...), (matched_value, matched_value,...), (value, value,...))
        finished_data.append((labels, matched_values, values))

    return finished_data



def append_values(base, matches, values):
    if isinstance(values, str):
        if base.__contains__(values):
            base.remove(values)
            matches.append(values)
        elif not matches.__contains__(values):
            base.append(values)
    else:
        for value in values:
            if base.__contains__(value):
                base.remove(value)
                matches.append(value)
            elif not matches.__contains__(values):
                base.append(value)



if __name__ == "__main__":
    data_fusion = data_fusion("Coldplay", "Q45188")
    print("--------------------------------------------------")
    print("data fusion:")
    for tuple in data_fusion:
        for label in tuple[0]:
            print(label)
        for matched_value in tuple[1]:
            print("--*--" + matched_value)
        for value in tuple[2]:
            print("     " + value)
    print("--------------------------------------------------")
    matched_labels = 0
    matched_values = 0
    unmatched_labels = 0
    unmatched_values = 0
    for tuple in data_fusion:
        if tuple[1]: matched_labels += len(tuple[0])
        else: unmatched_labels += len(tuple[0])
        matched_values += len(tuple[1])
        unmatched_values += len(tuple[2])
    print("matched labels: " + str(matched_labels))
    print("unmatched labels: " + str(unmatched_labels))
    print("matched values: " + str(matched_values))
    print("unmatched values: " + str(unmatched_values))