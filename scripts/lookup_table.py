import re
import spacy


# This returns a hashmap of the desired lookup table
def get_lookup_hash(file):
    hashmap = {}
    for line in file:
        elements = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]
        label = elements.pop(0)
        if label not in hashmap: hashmap[label] = []
        for element in elements:
            if element != "\n": hashmap[label].append(element)
    return hashmap

def get_lookup_hash_db():
    file = open("lookup_db_to_wd.csv", mode='r', encoding='utf-8')
    return get_lookup_hash(file)

def get_lookup_hash_wd():
    file = open("lookup_wd_to_db.csv", mode='r', encoding='utf-8')
    return get_lookup_hash(file)



# This should ONLY be called manually
def create_lookup_tables():
    master_db = open("master_db.csv", mode='r', encoding='utf-8')
    master_wd = open("master_wd.csv", mode='r', encoding='utf-8')

    lookup_wd_to_db = open("lookup_wd_to_db.csv", mode='w', encoding='utf-8')
    lookup_db_to_wd = open("lookup_db_to_wd.csv", mode='w', encoding='utf-8')

    nlp = spacy.load("en_core_web_lg")

    threshold = 0.75


    # For every property, we create the token
    db_tokenized_properties = []
    wd_tokenized_properties = []
    # This is for db
    for line in master_db:
        # We extract the property, check if it's wanted and then tokenize it
        elements = line.split(",")
        if elements[1] == "True":
            db_tokenized_properties.append(nlp(elements[0]))

    # This is for wd
    for line in master_wd:
        # We extract the property, check if it's wanted and then tokenize it
        elements = line.split(",")
        if elements[1] == "True":
            wd_tokenized_properties.append(nlp(elements[0]))


    # Now, we can loop for all the properties
    db_result = {}
    wd_result = {}
    # This is for db to wd
    for db_token in db_tokenized_properties:
        db_result[db_token.text] = []
        # We loop for every property
        for wd_token in wd_tokenized_properties:
            # If the properties are similar enough, we append the property in the line
            if db_token.similarity(wd_token) > threshold:
                db_result[db_token.text].append(wd_token.text)

    # This is for wd to db
    for wd_token in wd_tokenized_properties:
        wd_result[wd_token.text] = []
        # We loop for every property
        for db_token in db_tokenized_properties:
            # If the properties are similar enough, we append the property in the line
            if wd_token.similarity(db_token) > threshold:
                wd_result[wd_token.text].append(db_token.text)


    # Here, we write the results to 2 files
    for key in db_result:
        lookup_db_to_wd.write("%s,%s\n" % (key, ",".join(db_result[key])))

    for key in wd_result:
        lookup_wd_to_db.write("%s,%s\n" % (key, ",".join(wd_result[key])))