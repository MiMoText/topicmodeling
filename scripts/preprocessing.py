#!/usr/bin/env python3

"""
Doing Topic Modeling on Eighteenth-Century French Novels with gensim and mallet in the context of MiMoText:

Preprocessing.

Provides preprocessing for the input text files. 
Adds linguistic annotation using TreeTagger.
Works for modern French as well as French of 16th and 17th century.
Uses this information to filter the tokens in the documents.

References to used POS-Tagsets:
- TreeTagger for modern french: https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/french-tagset.html
- Presto language model: http://presto.ens-lyon.fr/wp-content/uploads/2014/05/%C3%89tiquettes_Presto-2014-10-13.pdf

"""

# == Imports ==

import os
import glob
from os.path import join
from os.path import basename
import treetaggerwrapper as ttw
import pprint
import helpers
import re


# == Functions ==

def load_text(textfile):
    """
    Loads a single plain text file. 
    Provides the content as a string.
    """
    with open(textfile, "r", encoding="utf8") as infile:
        text = infile.read()
        return text
    
    
def load_stoplists(paths):
    """
    Loads a language-specific list of stopwords and a list of names from the stoplists folder.
    Returns a complete list of stopwords.
    """
    try:
        slfile = join("stoplists", paths["stopwordsfile"])
        with open(slfile, "r", encoding="utf8") as infile:
            stoplist = infile.read().split("\n")
    except:
        stoplist = []
        print("Warning. No stoplist has been found.")
        print("Please consider adding a stoplist to the stoplist folder.")
    
    try:
        namefile = join("stoplists", paths["namelistfile"])
        with open(namefile, "r", encoding="utf8") as infile:
            namelist = infile.read().split("\n")
    except:
        namelist = []
        print("Warning. No namelist has been found.")

    return stoplist + namelist
    

def prepare_text(text, params, stoplist):
    """
    Adds the linguistic annotation to the text: part of speech. 
    Uses the linguistic annotation to filter out certain tokens.
    Nouns, verbs, adjectives and adverbs are retained.
    Also uses a stoplist and a minimum word length criterion to further filter tokens.
    Returns the single text as a list of lower-cased lemmas.
    """
    lang = params["lang"]
    if lang == "fr":  # treetagger laguage model for modern French
        tagger = ttw.TreeTagger(TAGLANG='fr') 
        text = tagger.tag_text(text)
        text = ttw.make_tags(text)
        #pprint.pprint(text)
        poslist = ["NOM", "ADJ", "ADV", "VER:cond", "VER:futu", "VER:impe", "VER:impf","VER:infi", "VER:pper", "VER:ppre", "VER:pres", "VER:simp", "VER:subi","VER:subp"] 
        prepared = [item.lemma.lower() for item in text if item.pos in poslist] 
        prepared = [item for item in prepared if len(item) > 1 and item not in stoplist]
        return prepared
    elif lang == "presto": # presto language model for French of 16th/17th century
        tagger = ttw.TreeTagger(TAGLANG='presto') 
        text = tagger.tag_text(text)
        text = ttw.make_tags(text)
        #pprint.pprint(text)
        poslist = ["Nc", "Ag", "Rg", "Vvn", "Vvc", "Vun", "Vuc", "Ge", "Ga"]
        prepared = [item.lemma.lower() for item in text if item.pos in poslist] 
        prepared = [item for item in prepared if len(item) > 1 and item not in stoplist]
        return prepared
    else:
        print("Sorry, the language code you supplied does not refer to a supported language (fr, presto).")
    
        
    

# == Coordinating function ==

def main(paths, params): 
    print("\n== preprocessing ==")
    alltextids = []
    allprepared = []
    stoplist = load_stoplists(paths)
    textpath = join(paths["workdir"], "datasets", paths["dataset"], "txt", "*.txt")
    for textfile in sorted(glob.glob(textpath)):
        textid = basename(textfile).split(".")[0]
        print(textid)
        alltextids.append(textid)
        text = load_text(textfile)
        prepared = prepare_text(text, params, stoplist)
        print(prepared)
        allprepared.append(prepared)
        helpers.save_pickle(allprepared, paths, "allprepared.pickle")
    print("files processed:", len(allprepared))
    print("==", helpers.get_time(), "done preprocessing", "==")   
    