#!/usr/bin/env python3

"""
Doing Topic Modeling on Eighteenth-Century French Novels with gensim in the context of MiMoText.

This is the main coordination script.
It allows you to set the pipeline parameters.
It allows you to determine which components will be run. 

Calling:
- extract_metadata: extracting metadata from the overall metadata file
- split_texts: splitting novel files into smaller chunks of text
- roman18_preprocessing: lemmatizing, POS-tagging and filtering
- build_corpus
- modeling
- postprocessing
- make_overview
To be continued.
"""


# == Imports ==


from os.path import join

import helpers
import extract_metadata
import roman18_split
import roman18_preprocessing
import build_corpus
import modeling
import postprocessing
import make_overview



# == Files and folders ==

workdir = ".."            
dataset = "pilot"             
identifier = "pilot_mod200_fr_10_500_newstop"

metadata_roman18 = "roman18.csv"
metadatafile_full = join(workdir, "datasets", dataset, "metadata-full.csv")
metadatafile_split = join(workdir, "datasets", dataset, "metadata.csv")
stoplistfile = "fr.txt"


# == Parameters ==

chunksize = 1000  
lang = "fr"   # possible values: "fr" (standard French); "presto" (French of the 16th and 17th century)
numtopics = 10 
passes = 500

# == Coordinating function ==

def main(workdir, dataset, identifier, lang, metadatafile_full, metadatafile_split, stoplistfile, chunksize, numtopics):
    print("==", "starting", "==", "\n==", helpers.get_time(), "==")
    extract_metadata.main(workdir, dataset, metadata_roman18)
    helpers.make_dirs(workdir, identifier)
    split.main(workdir, dataset, metadatafile_full, metadatafile_split, chunksize)
    preprocessing.main(workdir, dataset, identifier, lang, stoplistfile)
    build_corpus.main(workdir, identifier)
    modeling.main(workdir, identifier, numtopics, passes)
    postprocessing.main(workdir, dataset, identifier, numtopics)
    make_overview.main(workdir, identifier)
    print("\n==", helpers.get_time(), "done", "==")

    
main(workdir, dataset, identifier, lang, metadatafile_full, metadatafile_split, stoplistfile, chunksize, numtopics)


