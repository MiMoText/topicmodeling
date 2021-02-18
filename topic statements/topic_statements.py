'''
Script for creating the thematic statements based on topic modeling.
Input:
- mastermatrix file (results topic modeling)
- topic ranking file (results topic modeling)
- file with topic labels (manually generated)

Output:
- mastermatrix with additional percentage distribution of topics based on a
threshold value to be defined in the Parameters
- CSV file with prepared statements as a starting point for feeding into wikibase

Notes:
-The labelfile must be newly created for each new topic model. For this purpose,
the topics generated in the topic model are interpreted and labels
from the topic vocabulary are assigned to them.

- In order to calculate in what percentage of the works a topic occurs,
a threshold value must be defined. This threshold must be determined anew for a new topic model,
especially for a new number of topics. It should be selected in such a way
that particularly frequent and very rare topics are sorted out.
(We have defined that Topics that occur in more than 80%
and less than 10% of the works are disregarded for the statements -> see get_percentage()).

'''
# == Imports ==

import pandas as pd
import re

# == Files and Folders ==

zenodo_url = "https://doi.org/10.5281/zenodo.4493224" # Zenodo-URL der Veröffentlichung des TM
mastermatrixfile = "mastermatrix_tm_19112020.csv" # Mastermatrix-Datei (siehe results TM)
rankingfile = "topicranking.csv" # Topic-Ranking-Datei (siehe results TM)
labelfile = "topic_label.csv" # CSV-Datei mit der Zuordnung von Topicnummer und Label

# == Parameters ==

identifier = "mmt_2020-11-19_11-38"  # identifier des zugrundeliegenden Topic Models
numtopics = 30 # number of Topics
treshold = 0.03   # the treshold determines when a topic is consisidered to occur in a work
number_top_topics = 5 # how many Top-Topics to feed into Wikidata


# == Functions ==

"""
Calculating the percentages of the topics in the corpus
and getting topics with very high and very low occurences.
"""

def load_mastermatrix(mastermatrixfile):
    """
    Loads the mastermatrix file from disk.
    Provides it as a pandas DataFrame.
    """
    with open(mastermatrixfile, "r", encoding="utf8") as infile:
        df_avg = pd.read_csv(infile, sep="\t")
        return df_avg
    
    
def get_percentage(df_avg, numtopics, treshold):
    '''
    Calculates in what percentage of the works each topic occurs
    and writes the percentage into the mastermatrix file.
    
    Additionally, depending on the threshold value,
    determines the topics that occur in more than 80%
    and less than 10% of the works. Returns list with those topic numbers.
    '''
    textnumber = df_avg.index.size
    perc_row = {'id': "Percentage"}
    frequent = []  # save all topics with percentage > 80%
    seldom = []  # # save all topics with percentage < 10%
    for column in range(0,numtopics):
        column = str(column)
        counter = 0
        for ind in df_avg.index:
            if df_avg[column][ind] > treshold:
                counter += 1
        percentage = counter/textnumber
        if percentage > 0.8:
            frequent.append(column)
        if percentage < 0.1:
            seldom.append(column)
        perc_row.update({(column) : (percentage)})
    
    print("Topics with percentage > 80%:")
    print(frequent)
    print("Topics with percentage < 10%:")
    print(seldom)
    
    delete = frequent + seldom # all topics to ignore
    
    df_perc = df_avg.append(perc_row, ignore_index=True)

    return df_perc, delete
        
        
def save_df(df, identifier):
    """
    Saves DataFrame to CSV.

    """
    filename = identifier + "_avg_" + str(treshold) + ".csv"
    df.to_csv(filename, sep='\t', encoding="utf-8")


"""
Preparation of thematic statements:
for each work the very rare and frequent topics will be deleted,
for each of the top topics (number_top_topics defined in parameters)
a label is assigned and a statement is generated.
"""

def load_topicranking(rankingfile):
    """
    Loads the ranking file from disk.
    Provides it as a pandas DataFrame.
    """
    with open(rankingfile, "r", encoding="utf8") as infile:
        df_ranking = pd.read_csv(infile, sep="\t")
        df_ranking.drop('Unnamed: 0', axis=1, inplace=True)
        return df_ranking
    

def get_topTopics(df_ranking, delete, number_top_topics):
    """
    Takes Ranking file and for each novel deletes seldom and frequent topics.
    Returns the remaining top topics as Dataframe.
    """
    all_rows = []
    for ind in df_ranking.index:
        keep = []
        top_ten = df_ranking['Ranked topics'][ind]
        id = df_ranking['id'][ind]
        pattern = r'(\()([^\,]+)(\,)(\s\d*)(\))'
        for match in re.finditer(pattern, top_ten):
            topic = match[4].strip()
            if topic not in delete:
                if len(keep) in range(0,number_top_topics):
                    keep.append(topic)
        
        for item in keep:
            all_rows.append([id, "isAbout", item])
    
    
    df_top = pd.DataFrame(all_rows, columns=['MiMoText-ID', 'Property', 'TopicNumber'])
    #print(df_top)
    return df_top


def load_topicLabel(labelfile):
    """
    Loads the label file from disk.
    Provides it as a pandas DataFrame.
    """
    with open(labelfile, "r", encoding="utf8") as infile:
        df_labels = pd.read_csv(infile, sep="\t")
        label_dict = {}
        for ind in df_labels.index:
            label_dict[df_labels['TopicNumber'][ind]] = df_labels['Label'][ind]
            
        return label_dict
    

def add_label_ref(df_top, label_dict, zenodo_url):
    '''
    Adds topic label and reference-url.
    Returns Dataframe with prepared statements.
    '''
    column_label = []
    reference = []
    for ind in df_top.index:
        number = int(df_top['TopicNumber'][ind])
        column_label.append(label_dict.get(number))
        reference.append(zenodo_url)
    
    df_top['Item (Themen-Konzept)'] = column_label
    df_top['ReferencedBy'] = reference
    
    return df_top

# == Coordinating function ==

def main(mastermatrixfile, numtopics, treshold, identifier, rankingfile, number_top_topics, labelfile,zenodo_url):
    df_avg = load_mastermatrix(mastermatrixfile)
    df_perc, delete = get_percentage(df_avg, numtopics, treshold)
    save_df(df_perc, identifier)
    df_ranking = load_topicranking(rankingfile)
    df_top = get_topTopics(df_ranking, delete, number_top_topics)
    label_dict = load_topicLabel(labelfile)
    df_top = add_label_ref(df_top, label_dict, zenodo_url)
    filename = identifier + "_statements.csv"
    df_top.to_csv(filename, sep='\t', encoding="utf-8")

main(mastermatrixfile, numtopics, treshold, identifier, rankingfile, number_top_topics, labelfile, zenodo_url)