import re

import load_data_pickle
from scripts.data_cleaning import master_filter_db, master_filter_wd, data_cleaning
from scripts.lookup_table import get_lookup_hash_db, get_lookup_hash_wd

all_data_db = load_data_pickle.load_pickle(dbpedia=True)
all_data_wd = load_data_pickle.load_pickle(dbpedia=False)

# Creates data fusion tables
# start_row is an int >= 0
# end_row is an int >= start_row
# domain is between 0 and 4, where 0 = celebrities, 1 = chemical_elements, 2 = constellations, 3 = movies, 4 = sp500
def fusion_table(start_row: int, end_row: int, domain: int, multiple_lines = True):

    # This string is used for file-paths
    match domain:
        case 0:
            file_path = "celebrities"
        case 1:
            file_path = "chemical_elements"
        case 2:
            file_path = "constellations"
        case 3:
            file_path = "movies"
        case 4:
            file_path = "sp500"
        case _:
            raise Exception("domain out of bounds")

    # Opens the file containing all entity ids
    property_file = open(f"../topics/{file_path}/wd_db_{file_path}.csv", mode='r', encoding='utf-8')

    line_counter = 0
    for line in property_file:
        # Only the specified lines are processed
        if start_row <= line_counter <= end_row:

            # All desired information is collected from the wd_db file
            elements: list[str] = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]
            wd_id: str = elements[3]
            db_id: str = elements[5].removesuffix("\n")
            file_name: str = elements[1].removeprefix(" ").replace(" ", "_").replace(":" ,"").lower()

            output_file = open(f"../topics/{file_path}/entities/{file_name}.csv",mode='w+', encoding='utf-8')

            fusion_list: list[[str], [str], [str], [str], [str]] = data_fusion(db_id, wd_id, file_path)

            for property in fusion_list:
                db_labels: list[str] = property[0]
                wd_labels: list[str] = property[1]
                db_values: list[str] = property[2]
                wd_values: list[str] = property[3]
                matched_values: list[str] = property[4]

                # The columns are in this form:
                # db_labels | db_value | matched_value | wd_value | wd_labels
                # multiple_lines decides, if all values are put in one line and seperated by | or if they are split up into many lines
                columns = ["", "", "", "", ""]
                columns[0] = f"\"{" | ".join(db_labels)}\""
                columns[4] = f"\"{" | ".join(wd_labels)}\""
                if multiple_lines:
                    for matched_value in matched_values:
                        columns[2] = f"\"{matched_value[1].replace("\"", "")}\""
                        output_file.write(",".join(columns) + "\n")
                    columns[2] = ""
                    for db_value in db_values:
                        columns[1] = f"\"{db_value[1].replace("\"", "")}\""
                        output_file.write(",".join(columns) + "\n")
                    columns[1] = ""
                    for wd_value in wd_values:
                        columns[3] = f"\"{wd_value[1].replace("\"", "")}\""
                        output_file.write(",".join(columns) + "\n")
                else:
                    db_values = [db_value[1] for db_value in db_values]
                    wd_values = [wd_value[1] for wd_value in wd_values]
                    matched_values = [matched_value[1] for matched_value in matched_values]
                    columns[1] = f"\"{" | ".join(db_values).replace("\"", "")}\""
                    columns[2] = f"\"{" | ".join(matched_values).replace("\"", "")}\""
                    columns[3] = f"\"{" | ".join(wd_values).replace("\"", "")}\""
                    output_file.write(",".join(columns) + "\n")

        line_counter += 1

# Returns a list in this form [[db_labels], [wd_labels], [(db_value, db_original_value)], [(wd_value, wd_original_value)], [(matched_value, matched_original_value)]]
# Takes the DBpedia and WIKIDATA id of the entity and the name of the domain (e.g. celebrities, movies)
def data_fusion(db_id: str, wd_id: str, file_path: str):

    # Fetches the hashmaps for DBpedia and WIKIDATA
    db_hash = all_data_db[file_path][db_id]
    wd_hash = all_data_wd[file_path][wd_id]

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
        # Needed, in case an entry was deleted by the second check of DBpedia in a previous run
        if db_label in db_hash:
            # Initiating the label lists and adding the first DBpedia label
            db_labels: list[str] = [db_label]
            wd_labels: list[str] = []

            # Initiating the value lists
            db_values: list[str] = []
            wd_values: list[str] = []
            matched_values: list[str] = []

            # Adding all values from DBpedia
            for value in db_hash[db_label]:
                db_values.append(value)

            # Removing the dict entry to avoid duplicates and for faster runtime
            del db_hash[db_label]

            # We check WIKIDATA for all similar labels
            for wd_label in db_lookup_hash[db_label]:
                if wd_label in wd_hash:
                    # Adding all labels from WIKIDATA
                    wd_labels.append(wd_label)

                    # Adding all values from WIKIDATA
                    for value in wd_hash[wd_label]:
                        if any(value[0] == db_value[0] for db_value in db_values):
                            db_values = [db_value for db_value in db_values if db_value[0] != value[0]]
                            matched_values.append(value)
                        elif not any(value[0] == matched_value[0] for matched_value in matched_values):
                            wd_values.append(value)

                    # Removing the dict entry to avoid duplicates and for faster runtime
                    del wd_hash[wd_label]

            # We check DBpedia again like WIKIDATA to get both directions
            for wd_label in wd_labels:
                for db_label_2 in wd_lookup_hash[wd_label]:
                    if db_label_2 in db_hash:
                        # Adding all labels from DBpedia
                        db_labels.append(db_label_2)

                        # Adding all values from DBpedia
                        for value in db_hash[db_label_2]:
                            if any(value[0] == wd_value[0] for wd_value in wd_values):
                                wd_values = [wd_value for wd_value in wd_values if wd_values[0] != value[0]]
                                matched_values.append(value)
                            elif not any(value[0] == matched_value[0] for matched_value in matched_values):
                                db_values.append(value)

                        # Removing the dict entry to avoid duplicates and for faster runtime
                        del db_hash[db_label_2]

            # All labels and values are appended to the ultimate data_fusion list
            finished_data.append((db_labels, wd_labels, db_values, wd_values, matched_values))

    # We collect the remaining WIKIDATA labels and their values
    # We don't need to check anything, as there can't be any matches left
    for wd_label in wd_hash:
        wd_values = wd_hash[wd_label]
        finished_data.append(([], [wd_label], [], wd_values, []))

    return finished_data


if __name__ == "__main__":
    fusion_table(start_row=0, end_row=9, domain=0, multiple_lines=False)
    fusion_table(start_row=0, end_row=9, domain=1, multiple_lines=False)
    fusion_table(start_row=0, end_row=9, domain=2, multiple_lines=False)
    fusion_table(start_row=0, end_row=9, domain=3, multiple_lines=False)
    fusion_table(start_row=0, end_row=9, domain=4, multiple_lines=False)

    '''
    data_fusion = data_fusion("Coldplay", "Q45188", "celebrities")
    print("--------------------------------------------------")
    for tuple in data_fusion:
        if isinstance(tuple[0], str): print(tuple[0])
        else:
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
    '''