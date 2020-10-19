#!/usr/bin/env python3

"""
Topic Modeling with gensim and mallet: Heatmap.

Based on a split of the data by some metadata category, 
provides a heatmap visualization of most distinctive topics for
each category.

See: https://seaborn.pydata.org/
"""

# == Imports ==

import os
from os.path import join
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


# == Functions

def load_mastermatrix(mastermatrixfile):
    """
    Loads the mastermatrix generated in postprocessing part.
    """
    with open(mastermatrixfile, "r", encoding="utf8") as infile:
        mastermatrix = pd.read_csv(infile, sep="\t")
        print(mastermatrix.head())
        try: 
            mastermatrix = mastermatrix.drop("Unnamed: 0", axis=1)
            mastermatrix = mastermatrix.drop("Unnamed: 0.1", axis=1)
        except: 
            print("nothing to delete here.")
        mastermatrix = mastermatrix.fillna("NaN")
        return mastermatrix


def group_data(mastermatrix, cats):
    """
    Discards the metadata categories that are not of interest here (drop). 
    Calculates the mean topic score for the metadata category of interest. 
    Selects the 10 most varying topics across the metadata category.
    """
    # include and exclude metadata items from metadata table.
    mastermatrix = mastermatrix.drop(cats[0], axis=1)
    data = mastermatrix.groupby(cats[1]).mean().T
    # select topics with maximum variance for visualization
    data["std"] = np.std(data, axis=1)
    data = data.sort_values(by="std", ascending=False)
    data = data.drop("std", axis=1)
    data = data.iloc[0:10,:]
    return data


def make_heatmap(data, heatmapfile, cats):
    """
    Using the seaborn library, creates a heatmap of the selected data.
    """
    
    fig, ax = plt.subplots(figsize=(20,15))
    plot = sns.heatmap(data, linewidths=.3, annot=False, annot_kws={"size": 18}, cmap="YlGnBu", ax=ax)  # annot=False|True: Werte in den Zellen
    plot.set_xticklabels(plot.get_xmajorticklabels(), fontsize = 17)  # change size of labels x-axis
    plot.set_yticklabels(plot.get_ymajorticklabels(), fontsize = 17)  # change size of labels y-axis
    
    # set xlabel and ylabel
    plot.set_ylabel("Topics",fontsize=30)
    plot.set_xlabel(cats[1],fontsize=30)
   
    plot.get_figure().savefig(heatmapfile, dpi=400)


# == Coordinating function ==

def main(paths, cats):
    print("\n== make_heatmap ==")
    workdir = paths["workdir"]
    identifier = paths["identifier"]
    mastermatrixfile = join(workdir, "results", identifier, "mastermatrix.csv")
    mastermatrix = load_mastermatrix(mastermatrixfile)
    data = group_data(mastermatrix, cats)
    heatmapfile = join(workdir, "results", identifier, "heatmap_"+cats[1][0]+".png")
    make_heatmap(data, heatmapfile, cats)
    print("done making heatmap")
