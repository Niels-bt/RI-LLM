import re

import spacy

# Transforms a hash into a list
def hash_to_list(hashmap):
    return [(label, value) for label, value in hashmap.items() for value in label]

# This is the filter for DBpedia using the masterfile
# It takes a hashmap and returns a hashmap
# Bools decide whether DBpedia or WIKIDATA is used
def master_filter(hashmap, dbpedia: bool, wikidata: bool):

   # Loads the right file. Throws an exception if the bools are wrong
   # This is complicated on purpose to stop an accident with the bool
    if dbpedia and not wikidata:
        file_master = open("master_db.csv", mode='r', encoding='utf-8')
    elif wikidata and not dbpedia:
        file_master = open("master_wd.csv", mode='r', encoding='utf-8')
    else:
        raise Exception("Undefined, if DBpedia or WIKIDATA is to be used")

    # Creates a list of all included labels
    included_labels = []
    for line in file_master:
        elements = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]
        if elements[1] == "True":
            included_labels.append(elements[0])

    # Checks for each label, if it's included in the list
    return dict((label, value) for label, value in hashmap.items() if included_labels.__contains__(label))



# Very rough filter on db entries before they are transformed into readable tuples
def keep_db(string):
    if "ID" in string:
        return False
    match string:
        case "wikiPageWikiLink":
            return False
        case "wikiPageExternalLink":
            return False
        case "owl#sameAs":
            return False
        case "abstract":
            return False
        case "22-rdf-syntax-ns#type":
            return False
        case "rdf-schema#comment":
            return False
        case "rdf-schema#label":
            return False
        case "depiction":
            return False
        case "wikiPageUsesTemplate":
            return False
        case "subject":
            return False
        case "wikiPageRedirects":
            return False
        case _:
            return True


# Transforms the list into a hashmap
# Gets rid of whitespaces
def prep_db(db_hash):
    db_hash_prepared = []
    for prop in db_hash:
        db_hash_prepared.append((prop.replace(" ", ""), db_hash[prop]))
    return db_hash_prepared

# Transforms the list into a hashmap
# Gets rid of whitespaces
# If the property contains _of_, _of_ is deleted and the
# words before and after it are switched (Place of Birth -> birthplace)
def prep_wd(wd_hash):
    wd_hash_prepared = []
    for prop in wd_hash:
        if " of " in prop:
            split_prop = prop.split(" of ")
            prop = split_prop[1] + split_prop[0]
        wd_hash_prepared.append((prop.replace(" ", ""), wd_hash[prop]))
    return wd_hash_prepared




# This function takes a list of tuples with (label, value) and returns (lemmatized_label, value)
# Only label will be processed. Value is used to give the algorithm context
# This function performs better when given a big list of tuples instead of calling it for each tuple separately
def lemmatization(tuples):
    # Loads the lemmatization algorithm for english
    nlp = spacy.load('en_core_web_sm')
    # Here, we will store all the transformed tuples
    processed_data = []
    # This creates the lemmatized labels and stores them in the list
    lemmatized_tuples = nlp.pipe(tuples, as_tuples=True, disable="parser")
    for label, value in lemmatized_tuples:
        processed_data.append((label.doc[0].lemma_.lower(), value))

    return processed_data