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
combined_coll = db['tag_combinations']  # New collection to store all combinations

# Remove all collections except 'api-img' and 'tags_summary'
protected_collections = ['api-img', 'tags_summary']
all_collections = db.list_collection_names()

for collection_name in all_collections:
    if collection_name not in protected_collections:
        db[collection_name].drop()  # Drop the collection
        print(f"Dropped collection: {collection_name}")

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
            
            # If common serial numbers exist, store in the consolidated collection
            if common_serial_numbers:
                tag_combination_name = "_".join(combination)  # Name of tag combination
                
                # Insert the data into the consolidated collection
                combined_coll.insert_one({
                    "tag_name_combination": tag_combination_name,
                                        "total_count": len(common_serial_numbers),  # Add total_count field

                    "common_serial_number_list": common_serial_numbers
                })
        
        print(f"Processed combinations of size {r} out of {len(tags)} tags")

print("Done processing and saved all tag combinations into 'tag_combinations' collection.")
