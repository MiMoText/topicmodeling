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
- make_heatmap
To be continued.
"""


# == Imports ==


from os.path import join

import helpers
import extract_metadata
import roman18_split
import roman18_preprocessing
import build_corpus
import modeling_mallet
import modeling
import postprocessing
import postprocessing_mallet
import make_overview
import make_heatmap



# == Files and folders ==

workdir = ".."            
dataset = "rom18_mod"             
identifier = "rom18_40t_2000i_200opt"

metadata_roman18 = "roman18.csv"
metadatafile_full = join(workdir, "datasets", dataset, "metadata-full.csv")
metadatafile_split = join(workdir, "datasets", dataset, "metadata.csv")
stoplistfile = "fr.txt"


# == Parameters ==

chunksize = 1000  
lang = "fr"   # possible values: "fr" (standard French); "presto" (French of the 16th and 17th century)
numtopics = 20 
passes = 2000
cats = [["id", "author", "narration", "decade"],["gender"]]  # metadata categories: exclude,include

# == Coordinating function ==
'''
Choose modeling.main() and postprocessing.main() in order to perform the modeling step with gensim;
choose modeling_mallet.main() and postprocessing_mallet.main() for the modeling step with mallet.
'''

def main(workdir, dataset, identifier, lang, metadatafile_full, metadatafile_split, stoplistfile, chunksize, numtopics):
    print("==", "starting", "==", "\n==", helpers.get_time(), "==")
    extract_metadata.main(workdir, dataset, metadata_roman18)
    helpers.make_dirs(workdir, identifier)
    split.main(workdir, dataset, metadatafile_full, metadatafile_split, chunksize)
    preprocessing.main(workdir, dataset, identifier, lang, stoplistfile)
    build_corpus.main(workdir, identifier)
    modeling.main(workdir, identifier, numtopics, passes)
    #modeling_mallet.main(workdir, identifier, numtopics, passes)
    postprocessing.main(workdir, dataset, identifier, numtopics)
    #postprocessing_mallet.main(workdir, dataset, identifier, numtopics)
    make_overview.main(workdir, identifier)
    make_heatmap.main(workdir, identifier, cats)
    print("\n==", helpers.get_time(), "done", "==")

    
main(workdir, dataset, identifier, lang, metadatafile_full, metadatafile_split, stoplistfile, chunksize, numtopics)


