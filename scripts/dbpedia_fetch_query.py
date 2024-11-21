from SPARQLWrapper import SPARQLWrapper, JSON

def keep(string):
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




def get_marie_curie_data():
    a=0
    total =0
    good_ones = 0

    # Initialize SPARQLWrapper with DBpedia endpoint
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")

    # SPARQL query

    query = """
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
    """
    query_more_results ="""
    SELECT DISTINCT ?s ?p ?o
    WHERE {
        {
            <http://dbpedia.org/resource/Marie_Curie> ?p ?o .
            BIND(<http://dbpedia.org/resource/Marie_Curie> AS ?s)
        }
        UNION
        {
            ?s ?p <http://dbpedia.org/resource/Marie_Curie> .
            BIND(<http://dbpedia.org/resource/Marie_Curie> AS ?o)
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
        print("Marie Curie - DBpedia Properties:")
        print("-" * 50)

        for result in results["results"]["bindings"]:
            prop = result["property"]["value"]
            val = result["value"]["value"]

            # Clean up the property name by removing the URI prefix
            prop_name = prop.split("/")[-1]
            if keep(prop_name):
                good_ones +=1
                if val.startswith('http'):
                    # Split the URL by '/' and get the last non-empty element
                    segments = [seg for seg in val.split('/') if seg]
                    print(f"{prop_name}: {segments[-1]}")
                    #return segments[-1] if segments else text
                else:
                    print(f"{prop_name}: {val}")


            else:
                a+=1
            total+=1



        print("total is:",total," total shitty: ",a," so total good: ",good_ones)

    except Exception as e:
        print(f"An error occurred: {e}")



if __name__ == "__main__":
    get_marie_curie_data()