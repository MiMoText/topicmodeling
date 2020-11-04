#!/usr/bin/env python3

"""
Doing Topic Modeling on Eighteenth-Century French Novels with gensim and mallet in the context of MiMoText.

This is the main coordination script.
It allows you to set the pipeline parameters.
It allows you to determine which components will be run. 

"""


# == Imports ==


from os.path import join
import helpers
import extract_metadata
import split
import preprocessing
import build_corpus
import modeling_gensim
import modeling_mallet
import postprocessing_gensim
import postprocessing_mallet
import make_overview_gensim
import make_overview_mallet
import make_heatmap


# == Files and folders ==

workdir = ".."            
dataset = "rom18_90"             
identifier = "rom18_90_20t_2000i_200opt"

#metadata_roman18 = "roman18.csv"
metadata_roman18 = "xml-tei_metadata.tsv"
metadatafile_full = join(workdir, "datasets", dataset, "metadata-full.csv")
metadatafile_split = join(workdir, "datasets", dataset, "metadata.csv")
stopwordsfile = "fr.txt"
namelistfile = "names.txt"

mallet_path = r'C:\mallet-2.0.8\bin\mallet'  # only necessary if modeling step with mallet is chosen


# == Parameters ==

chunksize = 1000  # splitting texts in chunks of "1000" words
lang = "fr"   # possible values: "fr" (standard French); "presto" (French of the 16th and 17th century)

numtopics = 20 # number of topics that is generated
passes = 2000 # number of iterations
modeling = "mallet"  # modeling step with "gensim" or "mallet"

# if chosen mallet:
optimize_interval = 200  # optimization of topic model every "200" iterations; for "0" alpha and beta keep their values

cats = [["id", "author", "gender", "decade"],["narration"]]  # metadata categories: exclude,include


# == Packing ==

paths = {"workdir":workdir, "dataset":dataset, "identifier":identifier, "metadata_roman18":metadata_roman18, "metadatafile_full":metadatafile_full, "metadatafile_split":metadatafile_split, "stopwordsfile":stopwordsfile, "namelistfile":namelistfile, "mallet_path":mallet_path}
params = {"chunksize":chunksize, "lang":lang, "numtopics":numtopics, "passes":passes, "modeling":modeling, "optimize_interval":optimize_interval}


# == Coordinating function ==

def main(paths, params, cats):
    print("==", "starting", "==", "\n==", helpers.get_time(), "==")
    #helpers.make_dirs(paths)
    #extract_metadata.main(paths)
    #split.main(paths, params)
    #preprocessing.main(paths, params)
    #build_corpus.main(paths)
    
  
    if modeling == "gensim":
        modeling_gensim.main(paths, params)
        postprocessing_gensim.main(paths, params)
        make_overview_gensim.main(paths)
     
    if modeling == "mallet":
        #modeling_mallet.main(paths, params)
        postprocessing_mallet.main(paths, params)
        make_overview_mallet.main(paths)
       
    make_heatmap.main(paths, cats)
    print("\n==", helpers.get_time(), "done", "==")

    
main(paths, params, cats)

