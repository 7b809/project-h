import itertools
import json
from pymongo import MongoClient
import os

# Load environment variables for API data
api_data = os.getenv("API_DATA")
lst = api_data.split("_")
mongo_url = lst[0]

# MongoDB setup
client = MongoClient(mongo_url)
db = client['project-h']
coll = db['tags_summary']

# Function to find common elements in multiple lists
def intersect_lists(lists):
    return list(set.intersection(*map(set, lists)))

# Process the single document in the collection
doc = coll.find_one()  # Since you have only one document
if doc:
    tags = doc['tags']
    tag_data = doc['tag_data']
    
    # Create a dictionary to map tag_name to its serial_number_list
    tag_serial_map = {item['tag_name']: item['serial_number_list'] for item in tag_data}
    
    # Generate all combinations of tags (from 2 to len(tags))
    for r in range(2, len(tags) + 1):
        for combination in itertools.combinations(tags, r):
            # Get the corresponding serial_number_lists for this combination
            serial_lists = [tag_serial_map[tag] for tag in combination]
            
            # Find the common serial numbers
            common_serial_numbers = intersect_lists(serial_lists)
            
            # If common serial numbers exist, store in new collection
            if common_serial_numbers:
                tag_combination_name = "_".join(combination)  # Collection name based on tag combination
                collection_name = tag_combination_name.replace(" ", "_")  # Replace spaces with underscores

                # Insert the data into the new collection
                new_coll = db[collection_name]  # Create or access the new collection
                new_coll.insert_one({
                    "tag_name_combination": tag_combination_name,
                    "common_serial_number_list": common_serial_numbers
                })
        print(f"Processed combinations of size {r} out of {len(tags)} tags")

print("Done processing and saved each tag combination into its respective MongoDB collection.")
