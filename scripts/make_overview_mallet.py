'''
Doing Topic Modeling on Eighteenth-Century French Novels with mallet in the context of MiMoText:

Overview visualization.

Using the pyLDAvis library, provides an interactive overview 
visualisation of the topic model.

See: https://pyldavis.readthedocs.io/en/latest/

The script largely follows the elaboration for converting the MALLET output for visualization with pyLDAVis
(designed for the modeling results from gensim) of Jeri E. Wieringa,
see: https://jeriwieringa.com/2018/07/17/pyLDAviz-and-Mallet/
and its implementation by Viola Kämmer,
see: https://github.com/syna22/MA_thesis/blob/master/10)_mallet_to_pyldavis.py.

'''

# == Imports ==

from os.path import join
import csv
import gzip
import matplotlib.pyplot as plt
import os
import pandas as pd
import pyLDAvis
import shutil
import sklearn.preprocessing


# == Functions ==

def extract_params(statefilepath):
    '''
    Extract the alpha and beta values from the statefile.
    Returns a tuple: alpha (list), beta
    '''
    with gzip.open(statefilepath, "r") as state:                                   
        params = [x.decode("utf8").strip() for x in state.readlines()[1:3]]           
        print(params)
    return (list(params[0].split(":")[1].split(" ")), float(params[1].split(":")[1]))


#modell-datei (state-file) in df konvertieren, modell-datei ist tab-separated, die ersten zwei zeilen enthalten alpha u. beta hyperparams
def state_to_df(statefilepath):
    '''
    Transforms state file into pandas dataframe.
    The MALLET statefile is tab-separated, and the first two rows contain the alpha and beta hypterparamters.
    Returns dataframe: topic assignment for each token in each document of the model.
    '''
    df = pd.read_csv(statefilepath, compression="gzip", sep=" ", skiprows=[1,2])
    df["type"] = df.type.astype(str)   # make sure, there is no "nan" in type-column
    return df   


def pivot_and_smooth(df, smooth_value, rows_variable, cols_variable, values_variable):
    """
    Turns the pandas dataframe into a data matrix.
    Args:
        df (dataframe): aggregated dataframe 
        smooth_value (float): value to add to the matrix to account for the priors
        rows_variable (str): name of dataframe column to use as the rows in the matrix
        cols_variable (str): name of dataframe column to use as the columns in the matrix
        values_variable(str): name of the dataframe column to use as the values in the matrix
    Returns:
        dataframe: pandas matrix that has been normalized on the rows.
    """
    matrix = df.pivot(index=rows_variable, columns=cols_variable, values=values_variable).fillna(value=0)
    matrix = matrix.values + smooth_value
    
    normed = sklearn.preprocessing.normalize(matrix, norm='l1', axis=1)
    
    return pd.DataFrame(normed)


# == Coordinating function ==

def main(paths):
    # paths and folders
    workdir = paths["workdir"]
    identifier = paths["identifier"]
    statefile = identifier + "_state.mallet.gz"
    statefilepath = join(workdir, "results", identifier, statefile)
    
    # alpha- und beta-values
    params = extract_params(statefilepath)
    alpha = [float(x) for x in params[0][1:]]
    beta = params[1]
    # conversion state file into df
    df = state_to_df(statefilepath)
    # get lengths of documents
    docs = df.groupby("#doc")["type"].count().reset_index(name="doc_length")  
    # Get vocab and term frequencies from statefile
    vocab = df['type'].value_counts().reset_index()
    vocab.columns = ['type', 'term_freq']
    vocab = vocab.sort_values(by='type', ascending=True)
    #get the number of topic assignments for each word in the documents
    phi_df = df.groupby(["topic", "type"])["type"].count().reset_index(name ="token_count")     
    phi_df = phi_df.sort_values(by="type", ascending=True)
    # normalizing df
    phi = pivot_and_smooth(phi_df, beta, "topic", "type", "token_count")
    # generate the theta document-topic matrix
    theta_df = df.groupby(['#doc', 'topic'])['topic'].count().reset_index(name ='topic_count')
    theta = pivot_and_smooth(theta_df, alpha, "#doc", "topic", "topic_count")
    # pass data to pyLDAVis
    data = {'topic_term_dists': phi, 
        'doc_topic_dists': theta,
        'doc_lengths': list(docs['doc_length']),
        'vocab': list(vocab['type']),
        'term_frequency': list(vocab['term_freq'])
       }    
    vis_data = pyLDAvis.prepare(**data, sort_topics=False)
    vizfile = join(workdir, "results", identifier, "visualization.html")
    pyLDAvis.save_html(vis_data, vizfile)

      