# Work in progess: Topic Modeling pipeline for 18th century French novels

This repository contains scripts and test data used for the development of a topic modeling pipeline in the context of the MiMoText project.

The pipeline is based on the following set of scripts by Christof Schöch: https://github.com/dh-trier/topicmodeling/. It is constantly being revised and developed.

## Current implementations
* Extracting metadata
* Splitting texts 
* Preprocessing: lemmatizing, POS-tagging, filtering by POS, stopword list and minimum word length
* Modeling with mallet (using the python wrapper of the gensim library)
* Postprocessing: statistics (different lists and matrices)
* Visualizing via pyLDAvis
* Generating heatmaps
* Generating wordclouds

## How to

### Requirements

Please install the following: 

* Python 3
* Some additional libraries (with their respective dependencies): 
    * "numpy", see: https://www.numpy.org/
    * "pandas", see: https://pandas.pydata.org/
    * "treetaggerwrapper", see: https://pypi.org/project/treetaggerwrapper/
    * "gensim", see: https://radimrehurek.com/gensim/install.html
    * "pyLDAvis", see: https://github.com/bmabey/pyLDAvis
    * "sklearn", see: https://pypi.org/project/scikit-learn/
    * "seaborn", see: https://seaborn.pydata.org/
    * "wordcloud", see: https://pypi.org/project/wordcloud/  (Note: Trying to install wordcloud on Windows often leads to difficulties. It might help to install and run the library with Python version 3.7)
     
    * TreeTagger, see https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/
    * Please note: Follow the installation instructions given here; consider the differences between the different operating systems. It isn't necessary to download any language parameter files. They are already included in this folder.
    
* For the modeling you have to install the mallet implementation first:
	* mallet: http://mallet.cs.umass.edu/; download here: http://mallet.cs.umass.edu/topics.php
	(here you can find a helpful installation guide: https://programminghistorian.org/en/lessons/topic-modeling-and-mallet#installing-mallet)
	* important: In order to run the scripts it is necessary to specify the path where you stored the mallet binary on your computer (see "mallet_path" in roman18_run_pipeline.py)

### Application and usage notes

* Please make sure you have installed Python 3, TreeTagger, mallet and the desired libraries.
* Download and save this repository. 
* Save your text files (TXT) in datasets/[name-of-your-dataset]/full.
* Now you can run the scripts. 
* Set your parameters in roman18_run_pipeline.py.
* Run roman18_run_pipeline.py. 
    * It calls all required scripts in the correct order.
    * You can change the following parameters:
       - **chunksize**: size of text parts (number of tokens) into which the novels are split
       - **lang**: language parameter to choose the model for POS-tagging; choose "fr" for modern French and "presto" for French of 16th/17th century.
       - **numtopics**: number of topics created by the modeling
       - **passes**: number of iterations 
       - **modeling**: Specify whether you want to perform the modelling with gensim or mallet.
       - (only if chosen mallet:) **optimize_interval**: optimization of the topic model every "[chosen value]" iterations
	- **cats**: category for which the most distinctive topics are visualized in heatmap

* the splitted texts are saved in datasets/[name of dataset]/txt
* the preprocessed texts are saved as lists of lemmas in results/[name of dataset]/pickles
* the gensim model is saved in results/[name of dataset]/model
* in results/[name of dataset]/ you also find statistical files, a file "visualization.html" and the heatmap visualizations

### Topic statements
FIles and script for preparing topic statements to feed into Wikibase.