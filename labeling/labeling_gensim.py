'''
Script for assigning labels to topics of a topic model using word embeddings.
The label candidates are passed as a list in a TXT file.
The topics with their corresponding words are passed as CSV file, which was generated as output during topic modeling.
A pre-trained Word2Vec model is used, which was trained on French Wikipedia texts.

Using python library gensim: https://radimrehurek.com/gensim/models/word2vec.html
'''

#==============
# Imports 
#==============

from gensim.models import KeyedVectors
import pandas as pd
import numpy as np
from scipy.spatial import distance
import re


#=======================
# File paths
#=======================

txtfile = 'Schnittmenge_DEL_Grundwortschatz.txt'   # list with potential labels
modelfile = 'frWiki_no_phrase_no_postag_500_cbow_cut10.bin'  #word2vec model
topicfile = r'C:\Users\Anne\Documents\Arbeit\MiMoText\Topic Modeling\results\rom18_20t_2000i_200opt\topicwords.csv'  
#resultfile = "DEL_kompl_20t_20w_frWiki_500_cbow.csv"
resultfile = "testtest.csv"

#=======================
# Parameters
#=======================

numtopics = 20     # Anzahl der Topics
numwords = 20      # Anzahl der Top-N-Words, die für das Labeling berücksichtigt werden


#==============
# Functions 
#==============

def load_model(modelfile):
    '''
    Load Word2Vec-Model.
    '''
    model = KeyedVectors.load_word2vec_format(modelfile, binary=True, unicode_errors="ignore")
    return model


def term2list(txtfile, model):
    '''
    Opens a list of label candidates as a txt file and saves all terms for which there is a vector in the model into a list.
    Terms for which the model does not provide a vector are displayed in the shell.
    '''
    term_list = []
    no_vector_list = []
    with open(txtfile, "r", encoding="utf8") as infile: 
        txt = infile.read()
    lines = txt.split("\n")
    
    for line in lines:
        try:
            model[line]
            term_list.append(line)
        except KeyError:    
            no_vector_list.append(line)
            
    print("For the following terms no vector is provided in the model:")
    print(no_vector_list)
    return term_list

            
            
def make_term_dict(model, term_list):
    '''
    Creates a dictionary with the terms (label candidates) and associated vectors.
    '''
    term_dict = {}
    for term in term_list:
        term_dict[term] = model[term]

    return term_dict

        
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


def get_topic_vectors(topic_dict, model):
    '''
    For each topic a topic vector (topic centroid) is calculated by taking the average of all word vectors of a topic.
    Words of a topic for which the model does not contain a vector are ignored.
    These words are displayed in the shell.
    '''
    no_vector_dict = {}
    topic_vector_dict = {}
    
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
        topic_vector_dict[topic] = topic_centroid
    
    print("words with no vector in model:  ")
    print(no_vector_dict)
    
    return topic_vector_dict   # contains topic number and topic vector



def get_topic_label_distances(topic_vector_dict, term_dict, model):
    '''
    Takes the topic vectors and vectors of the label candidates and calculates the cosine distances for each topic.
    '''
    topic_distance_dict = {}
    # Kosinusdistanzen berechnen:
    for topic in topic_vector_dict:
        distance_dict = {}
        for term in term_dict:
            # Cosine distance is defined as 1.0 minus the cosine similarity
            distance_dict[term] = abs(1 - distance.cosine(topic_vector_dict[topic], term_dict[term])).round(4)  # Subtraction of 1 and taking amount
        topic_distance_dict[topic] = distance_dict
    
    return topic_distance_dict

    
    
def get_top_labels(topic_distance_dict):
    '''
    Returns a dictionary with the top 5 most similar labels per topic.
    '''
    dict_top_labels = {}
    for topic in topic_distance_dict:
        # sorting
        ranking = sorted(topic_distance_dict[topic].items(), key=lambda x: x[1], reverse=True)
        print("------------------------------")
        print(topic)
        counter = 0
        dict_ranked = {}
        for i in ranking:
            if counter in range(0,5):  # get the 5 highest values
                print(i[0], i[1])
                dict_ranked[i[0]] = i[1]
            counter += 1
        dict_top_labels[topic] = dict_ranked

    return dict_top_labels


def make_csv(numtopics, topic_dict, dict_top_labels, resultfile):
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
    # Top 5-Labels
    label_1 = []
    label_2 = []
    label_3 = []
    label_4 = []
    label_5 = []
    for topic in dict_top_labels:
        label_1.append(list(dict_top_labels[topic].items())[0])
        label_2.append(list(dict_top_labels[topic].items())[1])
        label_3.append(list(dict_top_labels[topic].items())[2])
        label_4.append(list(dict_top_labels[topic].items())[3])
        label_5.append(list(dict_top_labels[topic].items())[4])
    df_labels['Label 1'] = label_1
    df_labels['Label 2'] = label_2
    df_labels['Label 3'] = label_3
    df_labels['Label 4'] = label_4
    df_labels['Label 5'] = label_5
    
    with open(resultfile, "w", encoding="utf8") as outfile: 
        df_labels.to_csv(outfile, sep="\t")
   

#==============
# Main 
#==============

def main(txtfile, modelfile, numtopics, numwords, resultfile):
    model = load_model(modelfile)
    terms = term2list(txtfile, model)
    term_dict = make_term_dict(model, terms)
    topic_dict = get_topics(topicfile, numtopics, numwords)
    topic_vector_dict = get_topic_vectors(topic_dict, model)
    topic_distance_dict = get_topic_label_distances(topic_vector_dict, term_dict, model)
    dict_top_labels = get_top_labels(topic_distance_dict)
    make_csv(numtopics, topic_dict, dict_top_labels, resultfile)

main(txtfile, modelfile, numtopics, numwords, resultfile)

