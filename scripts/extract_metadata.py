#!/usr/bin/env python3

"""
Doing Topic Modeling on Eighteenth-Century French Novels with gensim in the context of MiMoText:

Extracting metadata of the texts in the corpus and saving as CSV file.

"""

# == Imports == 

import os
import glob
from os.path import join
from os.path import basename
import re
import pandas as pd

# == Functions ==

def load_metadata(metadata_roman18):
    """
    Loads the metadata file from disk.
    Provides it as a pandas DataFrame.
    """
    with open(metadata_roman18, "r", encoding="utf8") as infile:
        metadata = pd.read_csv(infile, sep="\t")
        return metadata
    
def create_df():
    """
    Creates DataFrame with metadata categories
    "id", "author", "year" and "narration".
    """
    metadata_full = pd.DataFrame(columns=['id', 'author', 'year', 'narration'])
    return metadata_full
    
def get_metadata(metadata_full, metadata, textid):
    """
    Extracts information from the metadata overview
    and writes it into the DataFrame.
    """
    author = textid.split('_')[0]
    textid = re.sub(r'\[1\]', r'', textid)
    key = metadata[metadata['dhtr-id'] == textid].index.item()
    year = metadata.loc[key, 'year-ref']
    narration = metadata.loc[key, 'Form (tei-Header)']

    metadata_full = metadata_full.append({'id': textid, 'author': author, 'year': year, 'narration': narration}, ignore_index=True)
    
    return metadata_full


def main(workdir, dataset, metadata_roman18):
    print("extract_metadata")
    textpath = join(workdir, "datasets", dataset, "full", "*.txt")
    metadata = load_metadata(metadata_roman18)
    metadata_full = create_df()
    for textfile in sorted(glob.glob(textpath)):
        textid = basename(textfile).split(".")[0]
        print(textid)
        metadata_full = get_metadata(metadata_full, metadata, textid)
    metadata_out = join(workdir, "datasets", dataset, "metadata-full.csv")
    metadata_full.to_csv(metadata_out, index=False)