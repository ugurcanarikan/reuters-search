import re
import string
import collections

stopwords = []
punctuations = []
inverted_index = dict()
bigrams = dict()

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

# Get stopwords from the file and put them in a list
with open("../stopwords.txt", "r") as stopwords_file:
	for line in stopwords_file:
		stopwords.append(line[:-1])
#print(stopwords)

# Get punctuations from the file and put them in a list
with open("../punctuations.txt", "r") as punctuations_file:
	for line in punctuations_file:
		punctuations.append(line[:-1])
#print(punctuations)

# Replace html characters from the corpus
def replace_html_characters(text):
	text = text.replace("\\n", " ")
	text = text.replace("&lt;", " ")
	text = text.replace("&#5;", " ")
	text = text.replace("&#22;", " ")
	text = text.replace("&#127;", " ")
	text = text.replace("&#1;", " ")
	text = text.replace("&amp;", " ")
	text = text.replace("&#30;", " ")
	text = text.replace("&#2;", " ")
	text = text.replace("&#27;", " ")
	text = text.replace("&#3;", " ")
	text = text.replace("&#31;", " ")
	return text

# Remove stopwords from the text
def remove_stopwords(text):
	"""
	for stopword in stopwords:
		text = text.replace(" " + stopword + " ", " ")
		text = text.replace(" " + stopword + "\n", " ")
	"""
	text = " ".join(filter(lambda word: word not in stopwords, text.split()))
	return text

# Remove punctuations from the text
def remove_punctuations(text):
	for punctuation in punctuations:
		text = text.replace(punctuation, " ")
	return text

corpus = ""		# Corpus
corpus_before_stopword_removal = ""		# Corpus before stopwords are removed
corpus_after_stopword_removal = ""		# Corpus after stopwords are removed
counter = 0		# DocID
for i in range(0,22):		# Read all the files
	if i < 10:
		filename = "../reuters21578/reut2-00" + str(i) + ".sgm"
	else:
		filename = "../reuters21578/reut2-0" + str(i) + ".sgm"
	with open(filename, "r", encoding="latin-1") as f:
		text = ""
		print("reading file: " + filename)
		in_text = False
		for line in f:
			if line[0:5] == "<TEXT":	# Start reading
				in_text = True				
			elif line[-8:] == "</TEXT>\n":	# End reading, start processing read text
				counter = counter + 1		# DocID
				in_text = False
				text = text + " " + line.strip() 
				text = text.replace("<TEXT>", " ")
				text = text.replace("</TEXT>", " ")
				text = text.replace("<TEXT TYPE=\"UNPROC\">", " ")
				text = text.replace("<TEXT TYPE=\"BRIEF\">", " ")
				text = re.sub('<DATELINE>.*?</DATELINE>',' ',text, flags=re.DOTALL)
				text = re.sub('<AUTHOR>.*?</AUTHOR>',' ',text, flags=re.DOTALL)
				text = text.replace("<TITLE>", " ")
				text = text.replace("</TITLE>", " ")
				text = text.replace("<BODY>", " ")
				text = text.replace("</BODY>", " ")
				corpus = corpus + " " + text
				text = remove_punctuations(text)
				text = text.lower()
				corpus_before_stopword_removal = corpus_before_stopword_removal + " " + text
				text = remove_stopwords(text)
				corpus_after_stopword_removal = corpus_after_stopword_removal + " " + text
				tokens_array = text.split()
				for token in tokens_array:
					inverted_index.setdefault(token, [])
					if counter not in inverted_index[token]:		# Add DocID in the iverted index list if it is not already present
						inverted_index[token].append(counter)
				text = ""
			if in_text:
				#if line[0:5] != "<TEXT":
				text = text + " " + line.strip()

inverted_index = collections.OrderedDict(sorted(inverted_index.items()))	# Order lexicographly

# Construct bigrams 
for key in inverted_index:
	bigram = "$" + key[0]
	bigrams.setdefault(bigram, [])
	if key not in bigrams[bigram]:
		bigrams[bigram].append(key)
	for i in range(0, len(key)):
		if i == len(key) - 1:
			bigram = key[i] + "$"
		else:
			bigram = key[i:i + 2]
		if bigram:
			bigrams.setdefault(bigram, [])
			if key not in bigrams[bigram]:
				bigrams[bigram].append(key)

bigrams = collections.OrderedDict(sorted(bigrams.items()))

# Write index file
index_file = open("../Output/index.json","w+")
index_file.write("{")
for key in list(inverted_index.keys())[:-1]:
	index_file.write("\"" + key + "\":[" + ", ".join(str(e) for e in inverted_index[key]) + "],\n")
index_file.write("\"" + list(inverted_index.keys())[-1] + "\":[" + ", ".join(str(e) for e in inverted_index[list(inverted_index.keys())[-1]]) + "]\n")
index_file.write("}")

# Write bigrams file
bigrams_file = open("../Output/bigrams.json","w+")
bigrams_file.write("{")
for key in list(bigrams.keys())[:-1]:
	bigrams_file.write("\"" + key + "\":[\"" + "\", \"".join(str(e) for e in bigrams[key]) + "\"],\n")
bigrams_file.write("\"" + list(bigrams.keys())[-1] + "\":[\"" + "\", \"".join(str(e) for e in bigrams[list(bigrams.keys())[-1]]) + "\"]\n")
bigrams_file.write("}")

print("number of words before stopword removal: " + str(len(corpus_before_stopword_removal.strip().split())))
print("number of words after stopword removal: " + str(len(corpus_after_stopword_removal.strip().split())))
print("number of terms before stopword removal and case-folding: " + str(len(set(corpus.strip().split()))))
#print("number of terms after stopword removal and case-folding: " + str(len(set(corpus_after_stopword_removal.split()))))
print("number of terms after stopword removal and case-folding: " + str(len(inverted_index.keys())))
print("top 20 most frequent terms before stopword removal and case-folding: ")
print(collections.Counter(corpus.strip().split()).most_common(20))
print("top 20 most frequent terms after stopword removal and case-folding: ")
print(collections.Counter(corpus_after_stopword_removal.strip().split()).most_common(20))

"""
corpus_file = open("corpus.txt", "w+")
corpus_file.write(corpus)

corpus_before_stopword_removal_file = open("corpus_before_stopword_removal.txt", "w+")
corpus_before_stopword_removal_file.write(corpus_before_stopword_removal)

corpus_after_stopword_removal_file = open("corpus_after_stopword_removal.txt", "w+")
corpus_after_stopword_removal_file.write(corpus_after_stopword_removal)
"""

