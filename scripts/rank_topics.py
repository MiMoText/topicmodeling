"""
Script to determine the 10 most relevant topics per work.
Input: work-topic distribution of a topic modeling.
Output: CSV with 10 most relevant topics and their probabilities for each work.

"""

#==============
# Imports 
#==============

from os.path import join
import pandas as pd


#=======================
# File paths
#=======================

workdir = ".."
identifier = "rom18_20t_2000i_200opt"
avgmatrixfile = join(workdir, "results", identifier, "avgtopics.csv")
resultfile = join(workdir, "results", identifier, "topicranking.csv")


#=======================
# Parameters
#=======================

numtopics = 20  # topic number of the topic model


#==============
# Functions 
#==============

def get_avg_topics(avgmatrixfile):
    '''
    Loads the work-topic distribution file from disk.
    Provides it as a pandas DataFrame.
    '''
    with open(avgmatrixfile, "r", encoding="utf8") as infile:
        avgmatrix = pd.read_csv(infile, sep="\t", index_col="Unnamed: 0")
        return avgmatrix
    
    
def get_ranking(avgmatrix, numtopics):
    '''
    Takes work-topic distribution.
    For each work takes the top-10 most relevant topics.
    Provides it a pandas Dictionary.
    '''
    work_ranked_topics = {}
    topics = [i for i in range(0,numtopics)]
    for index, row in avgmatrix.iterrows():
        id = row['id']
        probs = []
        for topic in topics:
            probs.append(row[str(topic)])
        work_ranked_topics[id] = sorted(zip(probs, topics), reverse=True)[:10] # top-10 topics are ranked
    #print(work_ranked_topics)
    return work_ranked_topics # dictionary with works and ranked topics


def save2csv(work_ranked_topics, resultfile):
    '''
    Saves the topic ranking to disk as a CSV file..
    '''
    df_ranking = pd.DataFrame()
    df_ranking['id'] = work_ranked_topics.keys()
    
    ranked_topics = []
    for work in work_ranked_topics:
        ranked_topics.append(work_ranked_topics[work])
    df_ranking['Ranked topics'] = ranked_topics

    with open(resultfile, "w", encoding="utf8") as outfile: 
        df_ranking.to_csv(outfile, sep="\t")


#==============
# Main 
#==============

def main(avgmatrixfile, resultfile, numtopics):
    avgmatrix = get_avg_topics(avgmatrixfile)
    work_ranked_topics = get_ranking(avgmatrix, numtopics)
    save2csv(work_ranked_topics, resultfile)
    print("Topic ranking done!")
    
main(avgmatrixfile, resultfile, numtopics)
