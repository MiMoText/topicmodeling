'''
Script for calculating the average probability per novel and topic.
Takes the mastermatrix and creates a new CSV file with the average values.

Note: Assumes that the topic model is made up of 10 topics.
'''

# == Imports == 

import os
import glob
from os.path import join
from os.path import basename
import re
import pandas as pd
import xlrd


# == Files and folders ==

workdir = ".."
dataset = "rom18"
identifier = "rom18_mod200_t10_i500"
mastermatrix_file = join(workdir, "results", identifier, "mastermatrix.csv")
outpath = join(workdir,  "results", identifier, "avgtopics.csv")


# == Functions ==

def load_mastermatrix(mastermatrix_file):
    """
    Loads the mastermatrix file from disk.
    Provides it as a pandas DataFrame.
    """
    with open(mastermatrix_file, "r", encoding="utf8") as infile:
        mastermatrix = pd.read_csv(infile, sep="\t")
        try: 
            mastermatrix = mastermatrix.drop("Unnamed: 0", axis=1)
            mastermatrix = mastermatrix.drop("Unnamed: 0.1", axis=1)
        except: 
            print("nothing to delete here.")
        #print(mastermatrix.head())
        return mastermatrix
    
def make_avgmatrix(mastermatrix):
    """
    Takes the mastermatrix as DataFrame,
    calculates the average probability per novel and topic
    and writes it into a new DataFrame.
    """
       
    df_avg = pd.DataFrame(columns=['id', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])

    for column in range(10):
        column = str(column)
        id_prev = ""
        counter = 0
        score = 0
        for ind in mastermatrix.index:
            id = mastermatrix['id'][ind]
            id = re.sub(r'(_[a-zA-Z0-9]*(\[\d?\])?)(_\d{3}\.txt)', r'\1', id)
            score_add = mastermatrix[column][ind] # Achtung: Spalte muss auch noch gewechselt werden
            if ind == 0:   # Sonderfall: erste Zeile
                id_prev = id
                score = score_add
                counter +=1
                
            elif ind == mastermatrix.index[-1] or id != id_prev:  # Sonderfall: letzte Zeile oder neue ID
                avg = str(score / counter)    # Durchschnitt des Topicscore berechnen
                if column == '0':
                    add = {'id': id_prev, column: avg}
                    df_avg = df_avg.append(add, ignore_index = True)
                else:
                    key = df_avg[df_avg['id'] == id_prev].index.item()
                    df_avg.loc[key][column] = avg
                id_prev = id
                score = score_add
                counter = 1
                
            else:  #id == id_prev:
                score = score + score_add
                counter +=1
    return df_avg

    
        
def df2csv(df_avg, outpath):
    """
    Saves DataFrame to CSV.

    """
    df_avg.to_csv(outpath, sep='\t', columns=['id', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], encoding="utf-8")
    

def main(workdir, dataset, identifier, mastermatrix_file, outpath):
    mastermatrix = load_mastermatrix(mastermatrix_file)
    df_avg = make_avgmatrix(mastermatrix)
    df2csv(df_avg, outpath)
    
main(workdir, dataset, identifier, mastermatrix_file, outpath)