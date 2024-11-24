import spacy


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
        case _:
            return True


# Gets rid of whitespaces
def prep_db(db_hash):
    db_hash_prepared = []
    for prop in db_hash:
        db_hash_prepared.append((prop.replace(" ", ""), db_hash[prop]))
    return db_hash_prepared

# Gets rid of whitespaces
# If the property contains _of_, its deleted and the words before and after it are switched (Place of Birth -> birthplace)
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