file_celeb = open("../topics/celebrities/wd_db_celeb.csv", mode='r')
file_chm = open("../topics/chemical_elements/wd_db_chemical_elements.csv", mode='r')
file_constellations = open("../topics/constellations/wd_db_constellations.csv", mode='r')
file_movies = open("../topics/movies/wd_db_movies.csv", mode='r')
file_sp500 = open("../topics/sp500/wd_db_sp500.csv", mode='r')

# These files need to be changed in case this code is used again
# They need to be empy files
new_file_celeb = open("../topics/celebrities/wd_db_celeb.csv", mode='a')
new_file_chm = open("../topics/chemical_elements/wd_db_chemical_elements.csv", mode='a')
new_file_constellations = open("../topics/constellations/wd_db_constellations.csv", mode='a')
new_file_movies = open("../topics/movies/wd_db_movies.csv", mode='a')
new_file_sp500 = open("../topics/sp500/wd_db_sp500.csv", mode='a')

files=[(file_celeb, new_file_celeb), (file_chm, new_file_chm), (file_constellations, new_file_constellations), (file_movies, new_file_movies), (file_sp500, new_file_sp500)]

for file in files:
    for old_file in file[0]:
        elements = old_file.split(",")
        elements[4] = elements[4].replace("\n","")
        file[1].write(",".join(elements) + "," + elements[4].replace("https://dbpedia.org/page/", "") + "\n")