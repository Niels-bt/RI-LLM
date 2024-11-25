import dbpedia_fetch_query as db_f_q
file_celeb = open("../topics/celebrities/wd_db_celeb.csv",mode='r')
file_chm = open("../topics/chemical_elements/wd_db_chemical_elements.csv",mode='r')
file_constellations = open("../topics/constellations/wd_db_constellations.csv",mode='r')
file_movies = open("../topics/movies/wd_db_movies.csv",mode='r')
file_sp500 = open("../topics/sp500/wd_db_sp500.csv",mode='r')
files=[file_celeb,file_chm,file_constellations,file_movies,file_sp500]

file_master = open("master.csv",mode="w")


def add_in_dic(dic,toadd):
    for ii in toadd:
        dic[ii]=""



counter=0
all_prop_hash = {}
for f in files:
    for i in f:
        elems = i.split(",")
        #problem elems 4 needs the person but its the page link
        new_to_add = db_f_q.get_person_data(elems[4],False,True)
        add_in_dic(all_prop_hash,new_to_add)
        print(elems[4])
        counter+=1
