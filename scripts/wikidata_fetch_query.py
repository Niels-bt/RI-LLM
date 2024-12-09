import requests


def get_person_data(person, new_query=True,printing = False):

    if new_query:
        query = f"""
        SELECT DISTINCT ?propertyLabel ?valueLabel
            WHERE {{
                {{
                    wd:{person} ?p ?v .
                    ?v ?a ?value .
                    ?property wikibase:claim ?p.
                    ?property wikibase:statementProperty ?a.
                }}
                UNION {{
                    ?value ?p wd:{person} .
                    ?property wikibase:directClaim ?p
                }}
                SERVICE wikibase:label {{
                    bd:serviceParam wikibase:language "en".
                }}
            }}
            """
    else:
        query = f"""
        SELECT ?propertyLabel ?valueLabel {{
          VALUES (?entry) {{(wd:{person})}}

          ?entry ?p ?v .
          ?v ?a ?value .

          ?property wikibase:claim ?p.
          ?property wikibase:statementProperty ?a.

          SERVICE wikibase:label {{
            bd:serviceParam wikibase:language "en".
          }}
        }}
        """


    endpoint = "https://query.wikidata.org/sparql"
    headers = {
        "Accept": "application/sparql-results+json"
    }
    params = {
        "query": query
    }
    response = requests.get(endpoint, headers=headers, params=params)

    relations = {}
    clean_data = {}
    # Check if the request was successful
    i = 0
    i2 = 0
    if response.status_code == 200:
        data = response.json()  # Parse the JSON response

        for item in data['results']['bindings']:
            if " ID" in item['propertyLabel']['value']:
                i += 1
            else:
                #relations[item['propertyLabel']['value']] = ""
                if printing:
                    print(f"Item: {item['propertyLabel']['value']}, Label: {item['valueLabel']['value']}")
                clean_data[item['propertyLabel']['value']]=item['valueLabel']['value']
            i2 += 1

        print("number of ids:", i, "out of", i2, "entries")
        return clean_data

    else:
        print(f"Error: {response.status_code}")


if __name__=="__main__":
    get_person_data("Q34660",False) #this is for marie curie
    get_person_data("Q34660",True) #this is for marie curie



