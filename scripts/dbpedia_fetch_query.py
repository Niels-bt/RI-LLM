from SPARQLWrapper import SPARQLWrapper, JSON

import spacy

def keep(string):
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




def get_person_data(person):
    not_good = 0
    total =0
    good_ones = 0

    # Initialize SPARQLWrapper with DBpedia endpoint
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")

    # SPARQL query
    query = f"""
            SELECT ?property ?value
            WHERE {{
                <http://dbpedia.org/resource/{person}> ?property ?value .
            }}
            """

    query_more_results = """
    SELECT ?property ?value
    WHERE {
    {
        <http://dbpedia.org/resource/Marie_Curie> ?property ?value .
    }
    UNION
    {
        ?value ?property <http://dbpedia.org/resource/Marie_Curie> .
    }
    }
    """ #wont be used discussed with acosta


    # Configure the query
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        # results to JSON
        results = sparql.query().convert()

        # Process and print results
        print(f"{person} - DBpedia Properties:")
        print("-" * 50)

        for result in results["results"]["bindings"]:
            prop = result["property"]["value"]
            val = result["value"]["value"]

            # Clean up the property name by removing the URI prefix
            prop_name = prop.split("/")[-1]
            if keep(prop_name):
                good_ones += 1
                if val.startswith('http'):
                    # Split the URL by '/' and get the last non-empty element
                    segments = [seg for seg in val.split('/') if seg]
                    print(f"{prop_name}: {segments[-1]}")
                    #return segments[-1] if segments else text
                else:
                    print(f"{prop_name}: {val}")

            else:
                not_good+=1
            total+=1

        print("total is:",total," total shitty: ",not_good," so total good: ",good_ones)

    except Exception as e:
        print(f"An error occurred: {e}")



# This function takes a list of tuples with (label, value) and returns (lemmatized_label, value)
# Only label will be processed. Value is used to give the algorithm context
# This function performs better when given a big list of tuples instead of calling it for each tuple separately
def lemmatization(words):
    # Loads the lemmatization algorithm for english
    nlp = spacy.load('en_core_web_sm')

    # Here, we will store all the transformed tuples
    processed_data = []

    # This creates the lemmatized labels and stores them in the list
    for label, value in nlp.pipe(words, as_tuples=True):
        processed_data.append((label.doc[0].lemma_, value))

    return processed_data



if __name__ == "__main__":
    #get_person_data("Marie_Curie")
    for word in lemmatization([("child", "running"), ("children", "walking"), ("doctoralStudent", "Leon"), ("doctoralStudents", "Niels"), ("birthDate", "12.12.2001")]):
        print(word)