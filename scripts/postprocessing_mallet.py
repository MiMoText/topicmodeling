"""
Doing Topic Modeling on Eighteenth-Century French Novels with mallet and gensim in the context of MiMoText:

postprocessing.

This module performs postprocessing of the raw mallet model output.  
It creates a list of words with top probability for each topic. 
It creates a list of word probabilities in each topic. 
And it creates a matrix of topic probabilities by document in the corpus. 
Also, it creates a so-called mastermatrix
that combines the metadata with the topic scores per document chunk.
The average topic scores per document are written into a separate list.

See: https://pandas.pydata.org/

"""

# == Imports == 

from os.path import join
import pandas as pd
import re
import helpers


# == Functions: extract basic information == 

def get_topics(model, numtopics, resultsfolder): 
    """
    Extracts the probabilities for the top 50 words in each topic. 
    Saves this data to a CSV file.
    """
    print("get_topics")
    topics = []
    for i in range(0,numtopics): 
        topic = model.show_topic(i, topn=50)
        topic = list(zip(*topic))
        topic = pd.Series(topic[1], index=topic[0], name=str(i))
        topics.append(topic)
    topics = pd.concat(topics, axis=1, keys=[topic.name for topic in topics], sort=False)
    topics = topics.fillna(0)
    with open(join(resultsfolder, "wordprobs.csv"), "w", encoding="utf8") as outfile: 
        topics.to_csv(outfile, sep="\t")


def get_topicwords(model, numtopics, resultsfolder): 
    """
    Extracts the top 50 words in each topic, 
    in descending order of probability. 
    Saves this data to a CSV file.
    """
    print("get_topicwords")
    topicdata = model.show_topics(num_topics=numtopics, num_words=50,formatted=False)
    topicwords = [(tp[0], [wd[0] for wd in tp[1]]) for tp in topicdata]
    topicwordsdict = {}
    for topic,words in topicwords:
        topicwordsdict[str(topic)] = words
    topicwordsdf = pd.DataFrame.from_dict(topicwordsdict, orient="index").T
    with open(join(resultsfolder, "topicwords.csv"), "w", encoding="utf8") as outfile: 
        topicwordsdf.to_csv(outfile, sep="\t")
        

def get_doc_topic_matrix(identifier, resultsfolder, numtopics): 
    """
    Converts the document x topic matrix (mallet output) into a CSV file.
    The matrix shows the topic probability 
    for each topic in each document.
    """
    print("get_topic_matrix")
    filename = identifier + "doctopics.txt"
    doctopics_txt = join(resultsfolder, filename)
    doctopics_csv = join(resultsfolder, "doc-topic-matrix.csv")
    read_file = pd.read_csv(doctopics_txt, sep='\t')
    read_file.drop('0', axis=1, inplace=True)
    read_file.drop('0.1', axis=1, inplace=True)
    read_file.columns = [i for i in range(0,numtopics)]
    read_file.to_csv(doctopics_csv, sep='\t')
    
    
# == Functions: make mastermatrix ==

def load_metadata(metadatafile):
    """
    Loads the metadata file from disk.
    Provides it as a pandas DataFrame.
    """
    with open(metadatafile, "r", encoding="utf8") as infile:
        metadata = pd.read_csv(infile, sep="\t")
        return metadata


def load_doc_topic_matrix(dtmatrixfile):
    """
    Loads the document x topic matrix from the previous step.
    Provides it as a pandas DataFrame.
    """
    with open(dtmatrixfile, "r", encoding="utf8") as infile:
        dtmatrix = pd.read_csv(infile, sep="\t", index_col="Unnamed: 0")
        return dtmatrix


def merge_matrices(metadata, dtmatrix):
    """
    Merges the metadata matrix and the document x topic matrix on the index.
    Returns the result as a pands DataFrame.
    """
    mastermatrix = metadata.merge(dtmatrix, right_index=True, left_index=True)
    mastermatrix.drop('Unnamed: 0', axis=1, inplace=True)
    return mastermatrix


def save_mastermatrix(mastermatrix, mastermatrixfile):
    """
    Saves the mastermatrix to disk as a CSV file.
    """
    with open(mastermatrixfile, "w", encoding="utf8") as outfile:
        mastermatrix.to_csv(mastermatrixfile, sep="\t")
        

def make_mastermatrix(workdir, dataset, identifier):
    print("make_mastermatrix")
    metadatafile = join(workdir, "datasets", dataset, "metadata.csv")
    metadata = load_metadata(metadatafile)
    dtmatrixfile = join(workdir, "results", identifier, "doc-topic-matrix.csv")
    dtmatrix = load_doc_topic_matrix(dtmatrixfile)
    mastermatrix = merge_matrices(metadata, dtmatrix)
    mastermatrixfile = join(workdir, "results", identifier, "mastermatrix.csv")
    save_mastermatrix(mastermatrix, mastermatrixfile)
    return mastermatrix


# == Functions: make average matrix ==

def make_avgmatrix(mastermatrix, numtopics):
    """
    Takes the mastermatrix as DataFrame,
    calculates the average probability per novel and topic
    and writes it into a new DataFrame.
    Calculates the average probabilty per topic (respective to whole corpus).
    """
    
    id_list = []
    for ind in mastermatrix.index:
        id = mastermatrix['id'][ind]
        if id not in id_list:
            id_list.append(id)
    
    
    df_avg = pd.DataFrame(columns=[i for i in range(0,numtopics)])
    df_avg.insert(0, 'id', [id for id in id_list])
    
    
    for column in range(0,numtopics):
        column = str(column)
        id_prev = ""
        counter = 0
        score = 0
        for ind in mastermatrix.index:
            id = mastermatrix['id'][ind]
            score_add = mastermatrix[column][ind] 
            
            if ind == 0:   # Sonderfall: erste Zeile
                id_prev = id
                score = score_add
                counter +=1
                
            elif ind == mastermatrix.index[-1] or id != id_prev:  # Sonderfall: letzte Zeile oder neue ID
                avg = str(score / counter)   # Durchschnitt des Topicscore berechnen
                key = df_avg[df_avg['id'] == id_prev].index.item()
                df_avg.loc[key][int(column)] = float(avg)
                
                id_prev = id
                score = score_add
                counter = 1
                
            else:  #id == id_prev:
                score = score + score_add
                counter +=1
        
    # Spaltensummen:
    sum_row = {'id': "Total"}
    
    for column in range(0,numtopics):
        total = df_avg[int(column)].sum()
        sum_row.update({(column) : (total/len(id_list))})
        
    df_avg = df_avg.append(sum_row, ignore_index=True)

    return df_avg


def save_avgmatrix(df_avg, avgmatrixfile):
    """
    Saves DataFrame to CSV.

    """
    df_avg.to_csv(avgmatrixfile, sep='\t', encoding="utf-8")


def make_doc_topic_avg(mastermatrix, numtopics, workdir, identifier):
    print("make_doc_topic_avg")
    df_avg = make_avgmatrix(mastermatrix, numtopics)
    avgmatrixfile = join(workdir, "results", identifier, "avgtopics.csv")
    save_avgmatrix(df_avg, avgmatrixfile)


# == Main ==
    
def main(workdir, dataset, identifier, numtopics):
    print("\n== postprocessing ==")
    model = helpers.load_model(workdir, identifier)
    resultsfolder = join(workdir, "results", identifier)
    get_topics(model, numtopics, resultsfolder)
    get_topicwords(model, numtopics, resultsfolder)
    get_doc_topic_matrix(identifier, resultsfolder, numtopics)
    mastermatrix = make_mastermatrix(workdir, dataset, identifier)
    make_doc_topic_avg(mastermatrix, numtopics, workdir, identifier)
    print("==", helpers.get_time(), "done postprocessing", "==") 
