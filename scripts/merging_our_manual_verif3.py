import os
import csv
from collections import Counter

directory = '../topics'
directory_celeb = '../topics/celebrities'

list_dir = ['celebrities','chemical_elements','constellations','movies','sp500']


for filetop in list_dir:
    for filename in os.listdir(f'{directory}/{filetop}/niels'):
        directory_n = f'../topics/{filetop}/niels'
        directory_l = f'../topics/{filetop}/leon'
        directory_m = f'../topics/{filetop}/manual_correction_moaaz'
        directory_final = f'../topics/{filetop}/verified'
        print(filename)

        output_file = open(f"{directory_final}/{filename}", 'w')
        temp_n = open(f'{directory_n}/{filename}', 'r')

        if os.path.isfile(f'{directory_l}/{filename}'):
            temp_l = open(f'{directory_l}/{filename}', 'r')
            temp_l_e = True

        else:
            print(f'leon has not this file: {filename}')
            temp_l_e = False

        if os.path.isfile(f'{directory_m}/{filename}'):
            temp_m = open(f'{directory_m}/{filename}', 'r')
            temp_m_e = True

            data_moaaz = {}

            reader = csv.reader(temp_m)
            for row in reader:
                if row[0]!="":
                    data_moaaz[sorted(row[0].split(" | "))[0]] = row[2]


        else:
            print(f'moaaz has not this file: {filename}')
            temp_m_e = False


        if temp_l_e and temp_m_e:
            #for line_n,line_l,line_m in zip(temp_n, temp_l, temp_m):
            reader_n = csv.reader(temp_n)
            reader_l = csv.reader(temp_l)
            for line_n,line_l in zip(reader_n, reader_l):

                mm_n =line_n
                mm_l =line_l


                if len(mm_l)<5 or len(mm_n)<5:
                    print(mm_n)
                    print(len(mm_n))
                    print(mm_l)
                    print(len(mm_l))
                    print("ok")
                    if sorted(mm_n[0].split(" | "))[0] in data_moaaz:
                        if len(data_moaaz[sorted(mm_n[0].split(" | "))[0]]) < 5:
                            print("ok")
                            print(data_moaaz[sorted(mm_n[0].split(" | "))[0]])
                            print(len(data_moaaz[sorted(mm_n[0].split(" | "))[0]]))


                columns = ["", "", "", "", "",""]


                if not (mm_n[2]=="" and mm_l[2]==""):

                    mm_n_val = mm_n[2].split(' | ')
                    mm_n_val = [s.removeprefix(" ").removesuffix(" ") for s in mm_n_val]
                    mm_l_val = mm_l[2].split(' | ')
                    mm_l_val = [s.removeprefix(" ").removesuffix(" ") for s in mm_l_val]



                    if sorted(mm_n[0].split(" | "))[0] in data_moaaz:
                        columns[0]= f"\"{(mm_n[0])} | {mm_n[4]}\""
                        mm_m_val = data_moaaz[sorted(mm_n[0].split(" | "))[0]].split(' | ')
                        mm_m_val = [s.removeprefix(" ").removesuffix(" ") for s in mm_m_val]

                        compteur = Counter(mm_n_val + mm_l_val + mm_m_val)


                        communs = [string for string, count in compteur.items() if count >= 2]


                        tempi = " | ".join(communs)

                        resultat = " | ".join(list(set(mm_n_val) - set(mm_n_val)))


                        chaine = " | ".join(resultat)
                        columns[1] = f'"{tempi}"'
                        columns[2] = f'"{" | ".join(list(set(mm_n_val) - set(communs)))}"'
                        columns[3] = f'"{" | ".join(list(set(mm_l_val) - set(communs)))}"'
                        columns[4] = f'"{" | ".join(list(set(mm_m_val) - set(communs)))}"'

                        columns[5] = f'"{mm_n[2]} | {mm_n[3]}"'


                    else:
                        #output_file.write(f"{mm_n[0]},'',{mm_n[2]},{mm_l[2]},'',{mm_n[1]}{mm_n[3]}\n")
                        columns[0]= f"\"{(mm_n[0])} | {mm_n[4]}\""

                        compteur = Counter(mm_n_val + mm_l_val)


                        communs = [string for string, count in compteur.items() if count >= 2]

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







