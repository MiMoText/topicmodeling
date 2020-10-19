#!/usr/bin/env python3

"""
Topic Modeling with gensim: helper functions.

This module provides some helper functions used by various other modules.
"""

import os
import pickle
from os.path import join
from gensim import models
from datetime import datetime



def make_dirs(paths):
    """
    Creates the folders required by the subsequent modules.
    """
    textfolder = join(paths["workdir"], "datasets", paths["dataset"], "txt", "")
    if not os.path.exists(textfolder):
        os.makedirs(textfolder)
    picklesfolder = join(paths["workdir"], "results", paths["identifier"], "pickles", "")
    if not os.path.exists(picklesfolder):
        os.makedirs(picklesfolder)
    modelsfolder = join(paths["workdir"], "results", paths["identifier"], "model", "")
    if not os.path.exists(modelsfolder):
        os.makedirs(modelsfolder)
    wordcloudsfolder = join(paths["workdir"], "results", paths["identifier"], "wordles", "")
    if not os.path.exists(wordcloudsfolder):
        os.makedirs(wordcloudsfolder)


def save_pickle(data, paths, picklename):
    """
    Save any intermediary data to the Python binary file format for retrieval later on.
    """
    picklesfile = join(paths["workdir"], "results", paths["identifier"], "pickles", picklename)
    with open(picklesfile, "wb") as filehandle:
        pickle.dump(data, filehandle)


def load_pickle(paths, picklename):
    """
    Load any intermediary data from a previous step for further processing.
    """
    picklesfile = join(paths["workdir"], "results", paths["identifier"], "pickles", picklename)
    with open(picklesfile, "rb") as filehandle:
        data = pickle.load(filehandle)
        return data


def save_model(paths, model):
    """
    Save a gensim model to file for later use.
    """
    modelfile = join(paths["workdir"], "results", paths["identifier"], "model", paths["identifier"]+".gensim")
    model.save(modelfile)


def load_model(paths): 
    """
    Load a gensim model file for further processing.
    """
    modelfile = join(paths["workdir"], "results", paths["identifier"], "model", paths["identifier"]+".gensim")
    model = models.LdaModel.load(modelfile)
    return model


def get_time(): 
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

