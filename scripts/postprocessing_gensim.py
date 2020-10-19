"""
Doing Topic Modeling on Eighteenth-Century French Novels with gensim in the context of MiMoText:

postprocessing.

This module performs postprocessing of the raw gensim model output.  
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
    

def get_doc_topic_matrix(vectorcorpus, model, resultsfolder): 
    """
    Creates a document y topic matrix that shows the topic probability 
    for each topic in each document.
    Saves this data to a CSV file.
    """
    print("get_topic_matrix")
    document_topics = model.get_document_topics(vectorcorpus, per_word_topics=True)
    doc_number = 0
    all_doc_topics = []
    for doc_topics, word_topics, phi_values in document_topics:
        doc_topics = dict(doc_topics)
        doc_topics = pd.Series(doc_topics, name=str(doc_number))
        all_doc_topics.append(doc_topics)
        doc_number +=1
    all_doc_topics = pd.concat(all_doc_topics, axis=1, keys=[s.name for s in all_doc_topics])
    all_doc_topics = all_doc_topics.fillna(0).T
    #print(all_doc_topics.head())
    with open(join(resultsfolder, "doc-topic-matrix.csv"), "w", encoding="utf8") as outfile: 
        all_doc_topics.to_csv(outfile, sep="\t")


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
        #print(dtmatrix)
        return dtmatrix


def merge_matrices(metadata, dtmatrix):
    """
    Merges the metadata matrix and the document x topic matrix on the index.
    Returns the result as a pands DataFrame.
    """
    mastermatrix = metadata.merge(dtmatrix, right_index=True, left_index=True)
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
    
# == Functions: rank topics ==

def get_ranking(df_avg, numtopics):
    '''
    Takes work-topic distribution.
    For each work takes the top-10 most relevant topics.
    Provides it a pandas Dictionary.
    '''
    work_ranked_topics = {}
    topics = [i for i in range(0,numtopics)]
    for index, row in df_avg.iterrows():
        id = row['id']
        probs = []
        for topic in topics:
            probs.append(row[str(topic)])
        work_ranked_topics[id] = sorted(zip(probs, topics), reverse=True)[:10] # top-10 topics are ranked
    
    return work_ranked_topics # dictionary with works and ranked topics


def save_ranking(work_ranked_topics):
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


def rank_topics(df_avg, numtopics):
    print("rank topics")
    work_ranked_topics = get_ranking(df_avg, numtopics)
    save_ranking(work_ranked_topics)


# == Coordinating function ==

def main(paths, params):
    print("\n== postprocessing ==")
    workdir = paths["workdir"]
    identifier = paths["identifier"]
    dataset = paths["dataset"]
    numtopics = params["numtopics"]
    model = helpers.load_model(paths)
    vectorcorpus = helpers.load_pickle(paths, "vectorcorpus.pickle")
    resultsfolder = join(workdir, "results", identifier)
    get_topics(model, numtopics, resultsfolder)
    get_topicwords(model, numtopics, resultsfolder)
    get_doc_topic_matrix(vectorcorpus, model, resultsfolder)
    mastermatrix = make_mastermatrix(workdir, dataset, identifier)
    df_avg = make_doc_topic_avg(mastermatrix, numtopics, workdir, identifier)
    rank_topics(df_avg, numtopics)
    print("==", helpers.get_time(), "done postprocessing", "==")   
