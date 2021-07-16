import pandas as pd 
import re



def read_data(): 
	with open("mastermatrix.csv", "r", encoding="utf8") as infile: 
		mmx = pd.read_csv(infile, sep="\t", index_col="id")
		mmx.drop(["Unnamed: 0", "author", "decade", "gender", "narration"], axis=1, inplace=True)
		#print(mmx.head())
		return mmx


def read_labels(): 
	with open("topic_label.csv", "r", encoding="utf8") as infile: 
		rawlabels = pd.read_csv(infile, sep="\t", index_col="TopicNumber").to_dict()["Label"]
		keys_values = rawlabels.items()
		labels = {str(key): str(value) for key, value in keys_values}
		return labels


def prepare_data(mmx, labels, threshold): 
	mmx.rename(labels, axis=1, inplace=True)
	data = []
	for d in range(0,92): # documents
		for t in range(0,30): # topics
			if mmx.iloc[d,t] > threshold: 
				data.append([mmx.index[d], mmx.columns[t], mmx.iloc[d,t]])
	print("number of edges:", len(data))
	return data



def save_data(data, threshold): 
	resultsfile = "topicmodel-Nov20_"+re.sub("\.", "", str(threshold))+".csv"
	data = pd.DataFrame(data, columns = ["source", "target", "weight"])
	with open(resultsfile, "w", encoding="utf8") as outfile: 
		data.to_csv(outfile)




def main(): 
	threshold = 0.03 # PARAMETER #
	mmx = read_data()
	labels = read_labels()
	data = prepare_data(mmx, labels, threshold)
	save_data(data, threshold)

main()			
