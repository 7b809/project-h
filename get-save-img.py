from pymongo import MongoClient
import cloudinary
import cloudinary.api
import json
import os
# Load environment variables for API data
api_data = os.getenv("API_DATA")
lst = api_data.split("_")


# Cloudinary setup (replace with your credentials)
cloudinary.config(
    cloud_name=lst[1],  # Your cloud_name from Cloudinary
    api_key=lst[2],     # Your api_key from Cloudinary
    api_secret=lst[3]   # Your api_secret from Cloudinary
)


# Function to fetch and sort images by upload time (ascending order)
def get_images_sorted_by_time(max_batches=10):
    image_list = []
    next_cursor = None  # Used for pagination if there are more results
    batch_count = 0     # Counter for the number of batches processed

    print("Connecting to Cloudinary...")

    # Fetch images from Cloudinary
    while batch_count < max_batches:
        try:
            # Fetch resources with 'type=upload' and sort by 'created_at' (ascending)
            print(f"Fetching batch {batch_count + 1} of images from Cloudinary...")
            response = cloudinary.api.resources(
                type='upload',
                resource_type='image',
                max_results=500,  # Fetch up to 500 resources per call (adjust if needed)
                direction=1,  # Ensure ascending order (oldest first)
                sort_by={'created_at': 'asc'},  # Sort by upload time in ascending order
                next_cursor=next_cursor  # Used for fetching the next page of results
            )

            # Append fetched resources to the image list
            image_list.extend(response['resources'])

            print(f"Fetched {len(response['resources'])} images. Total so far: {len(image_list)}")

            batch_count += 1  # Increment the batch counter

            # Check if there are more pages to fetch
            if 'next_cursor' in response and batch_count < max_batches:
                next_cursor = response['next_cursor']
                print("Fetching the next batch...")
            else:
                print("Maximum batch limit reached or no more images to fetch.")
                break  # No more pages to fetch or batch limit reached

        except cloudinary.exceptions.Error as e:
            print(f"Error fetching resources: {e}")
            break

    # Return the sorted list of images
    return image_list

# Function to save images to MongoDB with serial numbers
def save_images_to_mongodb(image_list, mongodb_url, db_name, collection_name):
    # Connect to MongoDB
    client = MongoClient(mongodb_url)
    db = client[db_name]
    collection = db[collection_name]

    data = []
    total_images = len(image_list)
    
    print(f"Saving {total_images} images to MongoDB collection '{collection_name}'...")

    # Loop through the image list and format the data
    for i, img in enumerate(image_list, start=1):  # Start serial numbers from 1
        # Extract the image name from the secure URL
        img_name = img['public_id'].split('/')[-1]

        # Create a dictionary with only the required fields
        image_data = {
            "serial_no": i,
            "img_name": img_name,  # Include the image name
            "img_link": img['secure_url']  # Include the secure URL
        }
        data.append(image_data)

        if i % 100 == 0 or i == total_images:
            print(f"Processed {i}/{total_images} images.")

    # Insert the data into the MongoDB collection
    if data:
        collection.insert_many(data)
        print(f"Successfully saved {total_images} images to MongoDB collection '{collection_name}'.")

    # Close the MongoDB connection
    client.close()

# Start the process
print("Process started.")
sorted_images = get_images_sorted_by_time(max_batches=10)  # Limit to 10 batches

if sorted_images:
   # Cloudinary setup (replace with your credentials)


    # MongoDB Atlas setup (replace with your MongoDB Atlas URL and database details)
    mongo_url = lst[0]
    client = MongoClient(mongo_url)
    db = client['project-h']
    collection = db['api-img']
        # Save images to MongoDB
    save_images_to_mongodb(sorted_images, mongo_url, db, collection)

print("Process completed.")
