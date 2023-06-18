import json

with open('images.json', 'r') as f:
    data = json.load(f)

arr = []

for item in data:
	if type(item) == list:
		arr.append(item)
  
with open('images-grouped.json', 'w') as f:
    json.dump(arr, f)