import spacy

master_document = open("../scripts/db_master.csv", mode='r')

new_document = open("../scripts/lookup_table_db.csv", mode='a')

nlp = spacy.load("en_core_web_lg")

threshold = 0.8
# ----------
tokenized_properties = []

# For every property, we create the token:
for line in master_document:

    # We extract the property and format it
    prop = line.split(",")[1].replace("\n", "")
    tokenized_properties.append(nlp(prop))

# Now, we can loop for all the properties
for token in tokenized_properties:

    # We start a new line
    new_line = token.text
    new_properties = []

    # We loop for every property
    for token_2 in tokenized_properties:

        # If the properties are similar enough, we append the property in the line
        if token.similarity(token_2) > threshold:
            new_properties.append(token_2.text)

    # We add the line to the document
    new_document.write(new_line + ("," + ",".join(new_properties) if new_properties else "") + "\n")