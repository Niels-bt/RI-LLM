import pickle
def load_pickle(dbpedia):
    if dbpedia:
        dbfile = open('picklefile_db.pkl', 'rb')
        all_data = pickle.load(dbfile)
        return all_data
    else:
        dbfile = open('picklefile_wd.pkl', 'rb')
        all_data = pickle.load(dbfile)
        return all_data