import spacy

master_db = open("db_master.csv", mode='r')
master_wd = open("wd_master.csv", mode='r')

master_wd_matchedw_db = open("master_wd_matched_w_db.csv", mode='w')
master_db_matchedw_wd = open("master_db_matched_w_wd.csv", mode='w')

nlp = spacy.load("en_core_web_lg")

threshold = 0.66
# ----------
db_tokenized_properties = []
wd_tokenized_properties = []

# For every property, we create the token:
for line in master_db:
    # We extract the property and format it
    prop = line.split(",")[1].replace("\n", "")
    db_tokenized_properties.append(nlp(prop))

for line in master_wd:
    # We extract the property and format it
    prop = line.split(",")[1].replace("\n", "")
    wd_tokenized_properties.append(nlp(prop))

# Now, we can loop for all the properties
db_result = {}

for token in db_tokenized_properties:

    db_result[token.text] = []

    # We loop for every property

    for token_2 in wd_tokenized_properties:
        # If the properties are similar enough, we append the property in the line
        if token.similarity(token_2) > threshold:
            db_result[token.text].append(token_2.text)

wd_result = {}

for token in wd_tokenized_properties:

    wd_result[token.text] = []

    # We loop for every property
    for token_2 in db_tokenized_properties:
        # If the properties are similar enough, we append the property in the line
        if token.similarity(token_2) > threshold:
            wd_result[token.text].append(token_2.text)
counter=0

def join_comma(lst):
    result = ''
    if lst:
        for i in lst[:-1]:
            result += i + ','
        result += lst[-1]
    else:
        result+='nothing'

    return result

for i in db_result:
    master_db_matchedw_wd.write((str(counter)+','+i+','+join_comma(db_result[i])+'\n'))
    counter+=1

counter=0

for i in wd_result:
    master_wd_matchedw_db.write((str(counter)+','+i+','+join_comma(wd_result[i])+'\n'))
    counter+=1