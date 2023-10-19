# Generation of Topic Statements from a Topic Model

## Associated Topic Model

The data for the associated Topic Model Topic Model mmt_2020-11-19_11-38 can be found here:
https://github.com/MiMoText/mmt_2020-11-19_11-38

### Explanation
The resulting Topic Model consists of a predefined number of Topics consisting of a probability distribution of the input words and a probability distribution of these Topics for each text document of the corpus.  Based on the most likely words, a label is assigned to each topic. Together with this information, topic statements are finally derived from the distribution of top topics per injected work. We consider the five most likely Topics for each novel, with prior sorting out of all Topics contained in less than 10% and in more than 80% of the corpus works.  In this way, very rare, partly work-specific, and very frequent, usually generic, topics are excluded, since they are of no use for a cross-work topic comparison. This leaves 25 topics that are included in the generation of topic statements.

It should be noted that basically every topic is present in every work. However, it only appears significantly above a certain probability, above which we speak in simplified terms of it being present in a work. The threshold value depends on the corpus size and number of topics. For the topic model described here, we have used a probability of 0.03 as the threshold value. With the help of this, we can calculate the percentage of texts in which each topic occurs.
