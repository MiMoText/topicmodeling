#!/usr/bin/env python3

"""
Doing Topic Modeling on Eighteenth-Century French Novels with gensim using mallet in the context of MiMoText:

Modeling.

Performs the main topic modeling step using the gensim library and mallet. 
This requires properly prepared forms of the corpus to be used. 

See:
http://mallet.cs.umass.edu/
https://radimrehurek.com/gensim/
https://radimrehurek.com/gensim/models/wrappers/ldamallet.html
"""

# == Imports == 

import pickle
from os.path import join, realpath, split
from gensim import corpora
from gensim import models
from gensim.models.wrappers import LdaMallet
import shutil
import helpers


# == Functions ==

def build_model(dictcorpus, vectorcorpus, paths, params): 
    """
    Creates the actual topic model from the data. 
    Key parameters are number of topics (numtopics) 
    and number of iterations (passes). 
    Other parameters can be set here.
    It is important to specify where mallet binary is found on your computer
    """
    
    # path to mallet binary
    mallet_path = paths["mallet_path"]

    model = LdaMallet(
        mallet_path,
        corpus = vectorcorpus,
        id2word = dictcorpus,
        num_topics = params["numtopics"],
        prefix = paths["identifier"],
        optimize_interval = params["optimize_interval"],  # choosing an optimal interval alpha and beta are generated automatically
        iterations = params["passes"],
        )
    
    return model

def move_output(workdir, identifier):
    '''
    Moves mallet output from the script directory into the results directory.
    '''
    destination = join(workdir, "results", identifier)
    files = ['corpus.mallet', 'corpus.txt', 'doctopics.txt', 'inferencer.mallet', 'state.mallet.gz', 'topickeys.txt']
    full_path = realpath(__file__)
    path, filename = split(full_path)
    
    for file in files:
        name = identifier + file
        source = join(path, name)
        shutil.move(source, destination)       
    

# == Coordinating function ==

def main(paths, params):
    
    print("\n== modeling ==")
    workdir = paths["workdir"]
    identifier = paths["identifier"]
    dictcorpus = helpers.load_pickle(paths, "dictcorpus.pickle")
    vectorcorpus = helpers.load_pickle(paths, "vectorcorpus.pickle")
    model = build_model(dictcorpus, vectorcorpus, paths, params)
    helpers.save_model(paths, model)
    move_output(workdir, identifier)
    print("==", helpers.get_time(), "done modeling", "==")   
    return model