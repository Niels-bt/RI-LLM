import os
import re
import csv
from collections import Counter

directory = '../topics'
directory_celeb = '../topics/celebrities'

list_dir = ['celebrities','chemical_elements','constellations','movies','sp500']
# for later when all the data is complete
#for topic_dir in os.listdir(directory):
#    print(topic_dir)

for filetop in list_dir:
    for filename in os.listdir(f'{directory}/{filetop}/niels'):
        directory_celeb_n = f'../topics/{filetop}/niels'
        directory_celeb_l = f'../topics/{filetop}/leon'
        directory_celeb_m = f'../topics/{filetop}/manual_correction_moaaz'
        directory_final = f'../topics/{filetop}/verified'
        print(filename)
        output_file = open(f"{directory_final}/{filename}", 'w')

        temp_n = open(f'{directory_celeb_n}/{filename}', 'r')

        if os.path.isfile(f'{directory_celeb_l}/{filename}'):
            temp_l = open(f'{directory_celeb_l}/{filename}', 'r')
            temp_l_e = True

        else:
            print(f'leon has not this file: {filename}')
            temp_l_e = False

        if os.path.isfile(f'{directory_celeb_m}/{filename}'):
            temp_m = open(f'{directory_celeb_m}/{filename}', 'r')
            temp_m_e = True

            data_moaaz = {}

                #data_moaaz[i.split(',')[0]] = i.split(',')[2]
            reader = csv.reader(temp_m)
            for row in reader:
                if row[0]!="":
                    data_moaaz[row[0]] = row[2]


        else:
            print(f'moaaz has not this file: {filename}')
            temp_m_e = False


        if temp_l_e and temp_m_e:
            #for line_n,line_l,line_m in zip(temp_n, temp_l, temp_m):
            reader_n = csv.reader(temp_n)
            reader_l = csv.reader(temp_l)
            for line_n,line_l in zip(reader_n, reader_l):
                #elements: list[str] =
                #mm_n = line_n.split(',')
                #mm_n = line_n.split(',')
                mm_n =line_n
                #mm_l = line_l.split(',')
                mm_l =line_l


                if len(mm_l)<5 or len(mm_n)<5:
                    print(mm_n)
                    print(len(mm_n))
                    print(mm_l)
                    print(len(mm_l))
                    print("ok")
                    if mm_n[0] in data_moaaz:
                        if len(data_moaaz[mm_n[0]]) < 5:
                            print("ok")
                            print(data_moaaz[mm_n[0]])
                            print(len(data_moaaz[mm_n[0]]))
                #mm_m = line_m.split(',')
                #if not (mm_n[2]=='""' and mm_l[2]=='""' and mm_m[2]=='""'):
                columns = ["", "", "", "", "",""]


                if not (mm_n[2]=="" and mm_l[2]==""):

                    #print(f'values are, label {mm_n[0]}\n'
                            #f'n: {mm_n[2]}\n'
                            #f'l: {mm_l[2]}\n'
                            #f'{"moaaz has it " if mm_n[0] in data_moaaz else "moaaz not "}: {data_moaaz[mm_n[0]] if  "'" not in mm_n[0] else data_moaaz[mm_n[0].replace('"',"")]}\n')
                            #)#
                   # print( mm_n[0] in data_moaaz)
                    #print(f'{"moaaz has it "+data_moaaz[mm_n[0]] if mm_n[0] in data_moaaz else "moaaz not "}\n')
                    mm_n_val = mm_n[2].split(' | ')
                    mm_n_val = [s.removeprefix(" ").removesuffix(" ") for s in mm_n_val]
                    mm_l_val = mm_l[2].split(' | ')
                    mm_l_val = [s.removeprefix(" ").removesuffix(" ") for s in mm_l_val]



                    if mm_n[0] in data_moaaz:
                        columns[0]= f"\"{(mm_n[0])} | {mm_n[4]}\""
                        mm_m_val = data_moaaz[mm_n[0]].split(' | ')
                        mm_m_val = [s.removeprefix(" ").removesuffix(" ") for s in mm_m_val]

                        compteur = Counter(mm_n_val + mm_l_val + mm_m_val)

                        # Récupère les éléments qui apparaissent au moins dans deux listes
                        communs = [string for string, count in compteur.items() if count >= 2]
                        print(communs)
                        tempi = ""

                        tempi = " | ".join(communs)

                        resultat = " | ".join(list(set(mm_n_val) - set(mm_n_val)))

                        # Combiner avec " | "
                        chaine = " | ".join(resultat)
                        columns[1] = f'"{tempi}"'
                        columns[2] = f'"{" | ".join(list(set(mm_n_val) - set(communs)))}"'
                        columns[3] = f'"{" | ".join(list(set(mm_l_val) - set(communs)))}"'
                        columns[4] = f'"{" | ".join(list(set(mm_m_val) - set(communs)))}"'



                        columns[5] = f'"{mm_n[2]} | {mm_n[3]}"'


                    else:
                        #output_file.write(f"{mm_n[0]},'',{mm_n[2]},{mm_l[2]},'',{mm_n[1]}{mm_n[3]}\n")
                        columns[0]= f"\"{(mm_n[0])} | {mm_n[4]}\""
                        #mm_m_val = data_moaaz[mm_n[0]].split(' | ')

                        compteur = Counter(mm_n_val + mm_l_val)

                        # Récupère les éléments qui apparaissent au moins dans deux listes
                        communs = [string for string, count in compteur.items() if count >= 2]
                        tempi = ""

                        tempi = " | ".join(communs)

                        columns[1] = f'"{tempi}"'
                        columns[2] = f'"{" | ".join(list(set(mm_n_val) - set(communs)))}"'
                        columns[3] = f'"{" | ".join(list(set(mm_l_val) - set(communs)))}"'

                        columns[4] = f'""'
                        columns[5] = f'"{mm_n[2]} | {mm_n[3]}"'


                    columns[5]=columns[5].replace("\n", "")
                    output_file.write(",".join(columns) + "\n")


            temp_l.close()
            temp_m.close()

        temp_n.close()







