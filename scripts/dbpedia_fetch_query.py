from SPARQLWrapper import SPARQLWrapper, JSON

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
        filtered_result = {}

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
                    filtered_result[prop_name]=segments[-1]
                    #return segments[-1] if segments else text
                else:
                    print(f"{prop_name}: {val}")
                    filtered_result[prop_name] = val

            else:
                not_good+=1
            total+=1

        print("total is:",total," total shitty: ",not_good," so total good: ",good_ones)
        return filtered_result

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    get_person_data("J._K._Rowling")