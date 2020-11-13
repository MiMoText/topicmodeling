#!/usr/bin/env python3

"""
Doing Topic Modeling on Eighteenth-Century French Novels with mallet in the context of MiMoText.

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
import modeling
import postprocessing
import make_overview
import make_heatmap


# == Files and folders ==

workdir = ".."            
dataset = "rom18_90"             
identifier = "rom18_90_20t_2000i_200opt"

mallet_path = r'C:\mallet-2.0.8\bin\mallet' 

metadata_roman18 = "xml-tei_metadata.tsv"
metadatafile_full = join(workdir, "datasets", dataset, "metadata-full.csv")
metadatafile_split = join(workdir, "datasets", dataset, "metadata.csv")
stopwordsfile = "fr.txt"
namelistfile = "names.txt"


# == Parameters ==

chunksize = 1000  # splitting texts in chunks of "1000" words
lang = "fr"   # possible values: "fr" (standard French); "presto" (French of the 16th and 17th century)

numtopics = 20 # number of topics that is generated
passes = 2000 # number of iterations
optimize_interval = 200  # optimization of topic model every "200" iterations; for "0" alpha and beta keep their values

cats = [["id", "author", "gender", "narration"],["decade"]]  # metadata categories: exclude,include


# == Packing ==

paths = {"workdir":workdir, "dataset":dataset, "identifier":identifier, "metadata_roman18":metadata_roman18, "metadatafile_full":metadatafile_full, "metadatafile_split":metadatafile_split, "stopwordsfile":stopwordsfile, "namelistfile":namelistfile, "mallet_path":mallet_path}
params = {"chunksize":chunksize, "lang":lang, "numtopics":numtopics, "passes":passes, "optimize_interval":optimize_interval}


# == Coordinating function ==

def main(paths, params, cats):
    print("==", "starting", "==", "\n==", helpers.get_time(), "==")
    
    helpers.make_dirs(paths)
    extract_metadata.main(paths)
    split.main(paths, params)
    preprocessing.main(paths, params)
    build_corpus.main(paths)
    modeling.main(paths, params)
    postprocessing.main(paths, params)
    make_overview.main(paths)
    make_heatmap.main(paths, cats)
    
    print("\n==", helpers.get_time(), "done", "==")

    
main(paths, params, cats)

