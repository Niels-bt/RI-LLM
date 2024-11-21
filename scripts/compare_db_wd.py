import time

import dbpedia_fetch_query
import wikidata_fetch_query
import spacy

db_hash = dbpedia_fetch_query.get_person_data("Marie_Curie")
wd_hash = wikidata_fetch_query.get_person_data("Q7186")

db_hash_lemma = []
wd_hash_lemma = []

for prop in db_hash:
    db_hash_lemma.append((prop.replace(" ",""),db_hash[prop]))

for prop in wd_hash:
    if " of " in prop:
        lst = prop.split(" of ")
        prop_rightorder = lst[1]+lst[0]
        wd_hash_lemma.append((prop_rightorder.replace(" ", ""), wd_hash[prop]))
    else:
        wd_hash_lemma.append((prop.replace(" ",""),wd_hash[prop]))

def lemmatization(words):
    nlp = spacy.load('en_core_web_sm')
    processedData = []
    leon = nlp.pipe(words, as_tuples=True,disable="parser")
    for label, value in leon:
        # processedData.append((label,label.doc[0].lemma_.lower(), value)) some tests
        processedData.append((label.doc[0].lemma_.lower(), value))

    return processedData

print("-"*90)



start = time.time()
wd_hash_lemma_done = lemmatization(wd_hash_lemma)
print("end",time.time()-start)
db_hash_lemma_done = lemmatization(db_hash_lemma)

db_hash_lemma_done_hash = {}
wd_hash_lemma_done_hash = {}
for i,i2 in db_hash_lemma_done:
    db_hash_lemma_done_hash[i]=i2

for i,i2 in wd_hash_lemma_done:
    wd_hash_lemma_done_hash[i]=i2



for prop in wd_hash_lemma_done_hash:
    if prop in db_hash_lemma_done_hash:
        print("prop is",prop,"wd_val",wd_hash_lemma_done_hash[prop],"db",db_hash_lemma_done_hash[prop])
    else:
        print("prop is", prop, "wdata", wd_hash_lemma_done_hash[prop], "wikidata", "notfound")

