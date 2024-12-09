import dbpedia_fetch_query as db_f_q
import requests as req

file_celeb = open("../topics/celebrities/wd_db_celeb.csv",mode='r')
file_chm = open("../topics/chemical_elements/wd_db_chemical_elements.csv",mode='r')
file_constellations = open("../topics/constellations/wd_db_constellations.csv",mode='r')
file_movies = open("../topics/movies/wd_db_movies.csv",mode='r')
file_sp500 = open("../topics/sp500/wd_db_sp500.csv",mode='r')

files=[file_sp500,file_celeb,file_chm,file_constellations,file_movies]


file_master = open("db_wrong_correct_please.csv", mode="w")





wrong=0
good=0
wrong_articles = []

for f in files:
    print("checking file")
    for i in f:
        elems = i.split(",")
        #problem elems 4 needs the person but its the page link corrected
        without_n = elems[5].replace("\n","")
        r = req.get(f"https://dbpedia.org/resource/{without_n}")
        r2 = req.get(elems[4])

        #if r.url != elems[4]: # old one used before but doesnt check if the page link is also redirected
        if r.url != r2.url:
            print("wrong found",elems[5])
            wrong+=1
            wrong_articles.append(without_n)

        good+=1

print("wrong nb",wrong,"out of",good)
new_ct = 1
for i in wrong_articles:
    towrite = str(new_ct)+","+i+"\n"
    file_master.write(towrite)
    new_ct+=1