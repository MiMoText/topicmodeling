#!/usr/bin/env python3

"""
Doing Topic Modeling on Eighteenth-Century French Novels with gensim and mallet in the context of MiMoText.
Script for building the corpus for the following modelling step.

"""


import os
import glob
import pickle
from os.path import join
from os.path import basename
from collections import defaultdict
from gensim import corpora
import helpers


      
def build_vectorcorpus(allprepared):
    dictcorpus = corpora.Dictionary(allprepared)
    vectorcorpus = [dictcorpus.doc2bow(text) for text in allprepared]
    print("number of types in corpus:", len(dictcorpus))
    return dictcorpus, vectorcorpus



def main(paths):
    print("\n== text2corpus ==")
    allprepared = helpers.load_pickle(paths, "allprepared.pickle")
    dictcorpus, vectorcorpus = build_vectorcorpus(allprepared)
    helpers.save_pickle(dictcorpus, paths, "dictcorpus.pickle")
    helpers.save_pickle(vectorcorpus, paths, "vectorcorpus.pickle")
    print("==", helpers.get_time(), "done building corpus", "==")   

