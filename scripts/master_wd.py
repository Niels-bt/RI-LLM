import time

import wikidata_fetch_query as wd_f_q

file_celeb = open("../topics/celebrities/wd_db_celeb.csv",mode='r')
file_chm = open("../topics/chemical_elements/wd_db_chemical_elements.csv",mode='r')
file_constellations = open("../topics/constellations/wd_db_constellations.csv",mode='r')
file_movies = open("../topics/movies/wd_db_movies.csv",mode='r')
file_sp500 = open("../topics/sp500/wd_db_sp500.csv",mode='r')

files=[file_sp500,file_celeb,file_chm,file_movies,file_constellations]
#files=[file_constellations]


file_master = open("wd_master.csv", mode="w")
#file_master_old = open("wd_master2.csv", mode="r")



def add_in_dic(dic,toadd):
    for ii in toadd:
        if ii not in dic:
            dic[ii]=toadd[ii]





counter=0
all_prop_hash = {}
'''
for i in file_master_old:
    elems = i.split(",")
    all_prop_hash[elems[1].replace("\n",'')]=''

wait=0
'''


for f in files:
    for i in f:
        elems = i.split(",")
        if f == file_constellations:
            #for this the new query doesnt work timeout
            #can't really explain why, timeout of the sparql query not our side
            new_to_add = wd_f_q.get_person_data(elems[3],False,False)
        else:
            new_to_add = wd_f_q.get_person_data(elems[3], True, False)
        add_in_dic(all_prop_hash,new_to_add)
        print(elems[5])
        counter+=1
        time.sleep(2.01)

new_ct = 1
for i in all_prop_hash:
    towrite = str(new_ct)+","+i+"\n"
    file_master.write(towrite)
    new_ct+=1