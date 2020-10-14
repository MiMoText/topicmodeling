'''
Script for assigning labels to topics of a topic model using word embeddings.
The topics with their corresponding words are passed as CSV file, which was generated as output during topic modeling.
A pre-trained Word2Vec model is used, which was trained on French Wikipedia texts.
For each topic, represented by a topic vector, the semantically most similar words in the Word Embedding Model are calculated as possible labels.

Using python library gensim: https://radimrehurek.com/gensim/models/word2vec.html
'''

#==============
# Imports 
#==============

from gensim.models import KeyedVectors
import numpy as np
import pandas as pd
import re

#=======================
# File paths
#=======================


modelfile = "frWiki_no_phrase_no_postag_500_cbow_cut10.bin"
topicfile = r'C:\Users\Anne\Documents\Arbeit\MiMoText\Topic Modeling\results\rom18_20t_2000i_200opt\topicwords.csv'
resultfile = "labels_20t_frwiki2015.csv"

#=======================
# Parameters
#=======================

numtopics = 20
numwords = 20


#==============
# Functions 
#==============


def load_model(modelfile):
    '''
    Loads Word2Vec model.
    '''
    model = KeyedVectors.load_word2vec_format(modelfile, binary=True, unicode_errors="ignore")
    return model


def get_topics(topicfile, numtopics, numwords):
    '''
    Opens CSV file with topic word distribution.
    Creates a dictionary with topics and corresponding word lists.
    The length of the word list is defined by numwords (e.g. the 10 most relevant words of a topic).
    '''
    with open(topicfile, "r", encoding="utf8") as infile:
        topics = pd.read_csv(infile, sep="\t", index_col="Unnamed: 0")
    
    topic_dict = {}
    topicnumbers = [i for i in range(0,numtopics)]

    #for number in topicnumbers:
    for col in topics:
        col_list = []
        for i, row_value in topics[col].iteritems():
            if i in range(0,numwords):
                col_list.append(topics[col][i])
                #print(topics[col][i])
        topic_dict[col] = col_list
        
    return topic_dict


def get_topic_labels(topic_dict, model):
    '''
    For each topic a topic vector (the topic centroid) is calculated by taking the average of all word vectors of a topic.
    Words of a topic for which the model does not contain a vector are ignored in the calculation. These words are displayed in the shell.
    For each of these topic centroids the top-10 nearest words in the model are calculated and saved into a dictionary.
    '''
    no_vector_dict = {}
    topic_label_dict = {}
    
    for topic in topic_dict:
        array_tuple = ()
        for word in topic_dict[topic]:
            # turn œ to oe:
            word = re.sub(r'œ', r'oe', word)
            word = re.sub(r'aurois', r'avoir', word)
            word = re.sub(r'berger\|bergère', r'berger', word)
            try:
                word_v = model[word]
                array_tuple = (*array_tuple, word_v) # add vector to tuple
            except:
                no_vector_dict[topic] = word
        
        word_arrays = np.vstack(array_tuple)  # convert Tuple to Array
        topic_centroid = np.mean(word_arrays, axis = 0) # topic centroid = average vector of a topic

        most_similar_words = model.most_similar(positive = [topic_centroid], topn=10)
        #print(most_similar_words)
        topic_label_dict[topic] = most_similar_words
    print(topic_label_dict)
        
    print("words with no vector in model:  ")
    print(no_vector_dict)
    
    return topic_label_dict   # contains topic number and topic vector


def make_csv(numtopics, topic_dict, topic_label_dict, resultfile):
    '''
    Saves the results into a CSV file.
    '''
    df_labels = pd.DataFrame()
    # Topicnumbers
    df_labels['Topic'] = [i for i in range(0, numtopics)]
    # Top-Topicwords
    topic_words = []
    for topic in topic_dict:
        topic_words.append(topic_dict[topic])
    df_labels['Top-Words'] = topic_words
    
    # calculated nearest words as possible labels
    label_list = []

    for topic in topic_label_dict:
        label_list.append(topic_label_dict[topic])
   
    df_labels['Word2Vec labels'] = label_list

    with open(resultfile, "w", encoding="utf8") as outfile: 
        df_labels.to_csv(outfile, sep="\t")


#==============
# Main 
#==============

def main(modelfile, numtopics, numwords, resultfile):

    model = load_model(modelfile)
    topic_dict = get_topics(topicfile, numtopics, numwords)
    topic_label_dict = get_topic_labels(topic_dict, model)
    make_csv(numtopics, topic_dict, topic_label_dict, resultfile)


main(modelfile, numtopics, numwords, resultfile)