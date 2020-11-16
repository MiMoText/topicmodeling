"""
Doing Topic Modeling on Eighteenth-Century French Novels with mallet in the context of MiMoText:

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
    filename = identifier + "_doctopics.txt"
    doctopics_txt = join(resultsfolder, filename)
    doctopics_csv = join(resultsfolder, "doc-topic-matrix.csv")
    read_file = pd.read_csv(doctopics_txt, sep='\t')
    read_file.drop('0', axis=1, inplace=True)
    read_file.drop('0.1', axis=1, inplace=True)
    read_file.columns = [i for i in range(0,numtopics)]
    read_file.to_csv(doctopics_csv, sep='\t')
    
    
# == Functions: make chunkmatrix ==

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
    chunkmatrix = metadata.merge(dtmatrix, right_index=True, left_index=True)
    chunkmatrix.drop('Unnamed: 0', axis=1, inplace=True)
    return chunkmatrix
        

def make_chunkmatrix(workdir, dataset, identifier):
    print("make_chunkmatrix")
    metadatafile = join(workdir, "datasets", dataset, "metadata.csv")
    metadata = helpers.load_metadata(metadatafile)
    dtmatrixfile = join(workdir, "results", identifier, "doc-topic-matrix.csv")
    dtmatrix = load_doc_topic_matrix(dtmatrixfile)
    chunkmatrix = merge_matrices(metadata, dtmatrix)
    chunkmatrixfile = join(workdir, "results", identifier, "chunkmatrix.csv")
    helpers.save_matrix(chunkmatrix, chunkmatrixfile)
    return chunkmatrix


# == Functions: make mastermatrix ==

def make_avgmatrix(chunkmatrix, numtopics):
    """
    Takes the chunkmatrix as DataFrame,
    calculates the average probability per novel and topic
    and writes it into a new DataFrame.
    Calculates the average probabilty per topic (respective to whole corpus).
    """
    
    id_list = []
    for ind in chunkmatrix.index:
        id = chunkmatrix['id'][ind]
        if id not in id_list:
            id_list.append(id)
    
    
    df_avg = pd.DataFrame(columns=[i for i in range(0,numtopics)])
    df_avg.insert(0, 'id', [id for id in id_list])
    
    
    for column in range(0,numtopics):
        column = str(column)
        id_prev = ""
        counter = 0
        score = 0
        for ind in chunkmatrix.index:
            id = chunkmatrix['id'][ind]
            score_add = chunkmatrix[column][ind] 
            
            if ind == 0:   # Sonderfall: erste Zeile
                id_prev = id
                score = score_add
                counter +=1
                
            elif ind == chunkmatrix.index[-1] or id != id_prev:  # Sonderfall: letzte Zeile oder neue ID
                avg = str(score / counter)   # Durchschnitt des Topicscore berechnen
                key = df_avg[df_avg['id'] == id_prev].index.item()
                df_avg.loc[key][int(column)] = float(avg)
                
                id_prev = id
                score = score_add
                counter = 1
                
            else:  #id == id_prev:
                score = score + score_add
                counter +=1
    return df_avg



def make_mastermatrix(chunkmatrix, numtopics, workdir, dataset, identifier):
    print("make_mastermatrix")
    df_avg = make_avgmatrix(chunkmatrix, numtopics)
    metadatafile = join(workdir, "datasets", dataset, "metadata-full.csv")
    metadata = helpers.load_metadata(metadatafile)
    master_df = metadata.merge(df_avg, on ="id")
    mastermatrixfile = join(workdir, "results", identifier, "mastermatrix.csv")
    helpers.save_matrix(master_df, mastermatrixfile)
    return master_df


# == Functions: rank topics ==

def get_ranking(mastermatrixfile, numtopics):
    '''
    Takes work-topic distribution.
    For each work takes the top-10 most relevant topics.
    Provides it a pandas Dictionary.
    '''
    
    with open(mastermatrixfile, "r", encoding="utf8") as infile:
        df_avg = pd.read_csv(infile, sep="\t", index_col="Unnamed: 0")
    
        work_ranked_topics = {}
        topics = [i for i in range(0,numtopics)]
        for index, row in df_avg.iterrows():
            id = row['id']
            probs = []
            for topic in topics:
                probs.append(row[str(topic)])
            work_ranked_topics[id] = sorted(zip(probs, topics), reverse=True)[:10] # top-10 topics are ranked
    
    return work_ranked_topics # dictionary with works and ranked topics


def save_ranking(work_ranked_topics, workdir, identifier):
    '''
    Saves the topic ranking to disk as a CSV file.
    '''
    df_ranking = pd.DataFrame()
    df_ranking['id'] = work_ranked_topics.keys()
    
    ranked_topics = []
    for work in work_ranked_topics:
        ranked_topics.append(work_ranked_topics[work])
    df_ranking['Ranked topics'] = ranked_topics

    resultfile = join(workdir, "results", identifier, "topicranking.csv")

    with open(resultfile, "w", encoding="utf8") as outfile: 
        df_ranking.to_csv(outfile, sep="\t")


def rank_topics(workdir, identifier, numtopics):
    print("rank topics")
    mastermatrixfile = join(workdir, "results", identifier, "mastermatrix.csv")
    work_ranked_topics = get_ranking(mastermatrixfile, numtopics)
    save_ranking(work_ranked_topics, workdir, identifier)


# == Coordinating function ==
    
def main(paths, params):
    print("\n== postprocessing ==")
    workdir = paths["workdir"]
    identifier = paths["identifier"]
    dataset = paths["dataset"]
    numtopics = params["numtopics"]
    model = helpers.load_model(paths)
    resultsfolder = join(workdir, "results", identifier)
    get_topics(model, numtopics, resultsfolder)
    get_topicwords(model, numtopics, resultsfolder)
    get_doc_topic_matrix(identifier, resultsfolder, numtopics)
    chunkmatrix = make_chunkmatrix(workdir, dataset, identifier)
    master_df = make_mastermatrix(chunkmatrix, numtopics, workdir, dataset, identifier)
    rank_topics(workdir, identifier, numtopics)
    print("==", helpers.get_time(), "done postprocessing", "==") 
