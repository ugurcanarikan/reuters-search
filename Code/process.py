import sys
import json

# open created index file
with open("../Output/index.json", "r") as index_file:
	inverted_index = json.load(index_file)

# open created bigrams file
with open("../Output/bigrams.json", "r") as bigrams_file:
	bigrams = json.load(bigrams_file)

result = []
words = []

# process the query
if sys.argv[1] == "3":		# wildcard
	query = sys.argv[2]
	query = query.split("*")
	if not query[0] and not query[1]:
		for key in bigrams.keys():
			words = words + bigrams[key]
	elif query[0]:
		words = bigrams["$" + query[0][0]]
		for i in range(0, len(query[0]) - 1):
			words = list(set(words) & set(bigrams[query[0][i:i + 2]]))
		for i in range(0, len(query[1]) - 1):
			words = list(set(words) & set(bigrams[query[1][i:i + 2]]))
		if query[1]:
			words = list(set(words) & set(bigrams[query[1][-1] + "$"]))
	else:
		words = bigrams[query[1][-1] + "$"]
		for i in range(0, len(query[1]) - 1):
			words = list(set(words) & set(bigrams[query[1][i:i + 2]]))
	if query[0] or query[1]:
		words = [item for item in words if query[0] == item[0:len(query[0])] and (not query[1] or query[1] == item[-1*len(query[1]):]) and len(item) >= len(query[0]) + len(query[1])]
	#print(words)
	for word in words:
		result.extend(inverted_index[word])
	result = list(set(result))
	

elif (sys.argv[1] == "1" or sys.argv[1] == "2") and len(sys.argv[2].split()) == 1:		# single word
	try:
		result = inverted_index[sys.argv[2]]
	except Exception as e:
		result = []

elif sys.argv[1] == "1":		# and
	try:
		query = sys.argv[2].replace("AND", "")
		query = query.split()
		result = inverted_index[query[0]]
		for token in query[1:]:
			result = list(set(result) & set(inverted_index[token]))
	except Exception as e:
		result = []

elif sys.argv[1] == "2":  		# or
	query = sys.argv[2].replace("OR", "")
	query = query.split()
	try:
		result = inverted_index[query[0]]
	except Exception as e:
		result = []
	for token in query[1:]:
		try:
			result = result + inverted_index[token]
		except Exception as e:
			continue

result.sort()
print(result)


