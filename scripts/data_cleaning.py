import re
import spacy



# This is a filter using a file
# It takes a hashmap and returns a hashmap
def master_filter(hashmap, file):

    # Creates a list of all included labels
    included_labels = []
    for line in file:
        elements = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]
        if elements[1] == "True":
            included_labels.append(elements[0])

    # Checks for each label, if it's included in the list
    return dict((label, value) for label, value in hashmap.items() if included_labels.__contains__(label))

def master_filter_db(hashmap):
    file = open("master_db.csv", mode='r', encoding='utf-8')
    return master_filter(hashmap, file)

def master_filter_wd(hashmap):
    file = open("master_wd.csv", mode='r', encoding='utf-8')
    return master_filter(hashmap, file)

def data_cleaning(hashmap, lemmatization: bool = True):
    # The input is parsed to a list
    tuples = hash_to_list(hashmap)
    # All empty values are removed
    tuples = remove_empty_values(tuples)
    # All - and _ are removed
    tuples = remove_minus_and_underscore(tuples)
    # Duplicates are removed
    tuples = remove_duplicates(tuples)

    if lemmatization:
        # Label and value are inverted
        inverted_tuples = [(value, label) for label, value in tuples]
        tuples = tuple_lemmatization(inverted_tuples)
    else:
        tuples = lower_values(tuples)

    # Duplicates are removed again and then the list is returned as a dict
    tuples = remove_duplicates(tuples)
    new_hashmap = {}
    for label, value in tuples: new_hashmap.setdefault(label, []).append(value)
    return new_hashmap



# Applies .lower() to all values in a list of tuples
def lower_values(tuples):
    new_list = []
    for tuple in tuples:
        if isinstance(tuple[1], str): new_list.append((tuple[0], tuple[1].lower()))
        else:
            for value in tuple[1]:
                new_list.append((tuple[0], value.lower()))
    return new_list

# Applies lemmatization to all values from a list of tuples in this form [(value, label), (value, label)]
# Additionally, applies .lower() to all values
# Returns a list of tuples
def tuple_lemmatization(inverted_tuples):
    # The language pack is loaded and all values are lemmatized
    nlp = spacy.load('en_core_web_lg')
    lemmatized_inverted_tuples = nlp.pipe(inverted_tuples, as_tuples=True, disable="parser")

    # The docs are put into a new list and all values are transformed to lowercase
    new_tuples = []
    for lemmatized_value, label in lemmatized_inverted_tuples:
        new_tuples.append((label, " ".join([doc.lemma_ for doc in lemmatized_value.doc]).lower()))

    return new_tuples

# Transforms a hash into a list
def hash_to_list(hashmap):
    new_list = []
    for label, values in hashmap.items():
        if isinstance(values, str): new_list.append((label, values))
        else:
            for value in values:
                new_list.append((label, value))
    return new_list

# Removes all - and _ from a list of tuples in the form of (label, value)
def remove_minus_and_underscore(tuples):
    return [(tuple[0], tuple[1].replace("-", " ").replace("_", " ")) for tuple in tuples]

# Removes all duplicates in a list of tuples
def remove_duplicates(tuples):
    return list(set(tuples))

# Removes all empty values
def remove_empty_values(tuples):
    return [tuple for tuple in tuples if tuple[1]]


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