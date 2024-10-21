from pymongo import MongoClient
import os
# Load environment variables for API data
api_data = os.getenv("API_DATA")
lst = api_data.split("_")
mongo_url = lst[0]
# Connect to MongoDB
client = MongoClient(mongo_url)
db = client['project-h']
original_collection = db['api-img']
new_collection = db['tags_summary']  # New collection for storing tags and tag data

# Dictionary to store tags and the corresponding serial numbers
tags_dict = {}

# Step 1: Extract unique tags and build tag-data mapping
documents = original_collection.find()
for document in documents:
    serial_no = document['serial_no']
    tags = document.get('data', {}).get('tags', [])

    for tag in tags:
        if tag not in tags_dict:
            tags_dict[tag] = []  # Initialize list for this tag
        tags_dict[tag].append(serial_no)  # Add the serial number to this tag's list

# Step 2: Create the list of unique tags and the tag data
unique_tags = list(tags_dict.keys())
tag_data_list = [{"tag_name": tag, "serial_number_list": serials} for tag, serials in tags_dict.items()]

# Step 3: Insert the result into the new collection
new_document = {
    "tags": unique_tags,
    "tag_data": tag_data_list
}

# Insert the new document into the new collection
new_collection.insert_one(new_document)

print("Tags and tag data have been inserted into the new collection.")
