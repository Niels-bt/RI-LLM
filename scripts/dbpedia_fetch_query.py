from SPARQLWrapper import SPARQLWrapper, JSON

from scripts.data_cleaning import keep_db


def get_person_data(person, printing = False, new_query = True):
    not_good = 0
    total = 0
    good_ones = 0

    # Initialize SPARQLWrapper with DBpedia endpoint
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")



    if new_query:
        query=f"""
        SELECT DISTINCT ?property ?value WHERE {{
        {{
        <http://dbpedia.org/resource/{person}> ?property ?value . 
        }}
        UNION 
        {{
        ?value ?property <http://dbpedia.org/resource/{person}> . 
        }}
        }}
        """
    # SPARQL query
    else :
        query = f"""
        SELECT ?property ?value
        WHERE {{
            <http://dbpedia.org/resource/{person}> ?property ?value .
        }}
        """

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

            if keep_db(prop_name):
                good_ones += 1
                if val.startswith('http'):
                    # Split the URL by '/' and get the last non-empty element
                    segments = [seg for seg in val.split('/') if seg]
                    if printing:
                        print(f"{prop_name}: {segments[-1]}")
                    filtered_result[prop_name]=segments[-1]
                    #return segments[-1] if segments else text
                else:
                    if printing:
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
    get_person_data("J._K._Rowling", True, False)
    get_person_data("J._K._Rowling",True)
