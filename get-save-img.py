import os
import json
import requests
from PIL import Image
from io import BytesIO
import zipfile
import cloudinary
import cloudinary.uploader
from pymongo import MongoClient

# Load environment variables for API data
api_data = os.getenv("API_DATA")
lst = api_data.split("_")

# Cloudinary setup (replace with your credentials)
cloudinary.config(
    cloud_name=lst[1],  # Your cloud_name from Cloudinary
    api_key=lst[2],     # Your api_key from Cloudinary
    api_secret=lst[3]   # Your api_secret from Cloudinary
)

# MongoDB Atlas setup (replace with your MongoDB Atlas URL and database details)
mongo_url = lst[0]
client = MongoClient(mongo_url)
db = client['project-h']
collection = db['api-img']

# Define paths for ZIP, extracted JSON, and local image storage
zip_file_path = 'updated_data.zip'
extract_folder = 'extracted_data'
image_folder = 'pictures'
json_file_path = os.path.join(extract_folder, 'updated_data.json')

# Create the 'pictures' directory if it doesn't exist
os.makedirs(image_folder, exist_ok=True)

# Unzip the JSON file
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_folder)

# Load data from the extracted JSON file and start from image 28163 onwards
with open(json_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
    

# Function to download, compress, and save images with custom naming based on URL
def save_compressed_image(image_data, file_path, target_size_kb=60):
    img = Image.open(BytesIO(image_data))
    quality = 50
    while True:
        img.save(file_path, 'JPEG', quality=quality)
        if os.path.getsize(file_path) <= target_size_kb * 1024:  # Convert KB to bytes
            break
        quality -= 5
        if quality < 10:
            print(f"Unable to compress {file_path} to {target_size_kb} KB")
            break

# Function to extract image name from the URL (e.g., 'hr_229605' from the example URL)
def extract_image_name_from_url(url):
    # Extract the filename from the URL (e.g., 'hr_229605.jpg')
    image_name = url.split('/')[-1]  # Get the last part of the URL
    return image_name.split('.')[0]  # Remove the file extension (e.g., '.jpg')

# Function to upload images to Cloudinary and get URLs and sizes
def upload_images(folder_path):
    img_urls = []
    for img_file in os.listdir(folder_path):
        img_path = os.path.join(folder_path, img_file)
        try:
            response = cloudinary.uploader.upload(img_path, public_id=img_file.split('.')[0])  # Use the extracted name as public_id
            img_url = response['secure_url']
            img_serial_no = img_file.split('.')[0]  # Extract serial number from file name
            img_size_kb = response['bytes'] / 1024  # Get image size in KB
            img_urls.append({'img_serial_no': img_serial_no, 'copied_url': img_url, 'img_size_kb': img_size_kb})
            print(f"Uploaded: {img_file} - URL: {img_url}, Size: {img_size_kb:.2f} KB")
        except cloudinary.exceptions.Error as e:
            print(f"Error uploading {img_file}: {e}")
    return img_urls

# Function to save data to MongoDB
def save_to_mongodb(image_data):
    try:
        # First, delete the previous 1000 images (if any)
        if image_data:
            previous_serials = [img['img_serial_no'] for img in image_data]
            collection.delete_many({'img_serial_no': {'$in': previous_serials}})

        # Insert new images
        collection.insert_many(image_data)
        print(f"Successfully saved {len(image_data)} image links to MongoDB.")
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")

# Process images in batches of 1000
batch_size = 1000
total_images = len(data)
start_index = 0

while start_index < total_images:
    end_index = min(start_index + batch_size, total_images)
    img_list = data[start_index:end_index]

    # Step 1: Download and compress images
    uploaded_urls = []  # Store URLs for the current batch
    for index, entry in enumerate(img_list, start=start_image_serial + start_index):
        img_src = entry['data']['image']['src']
        try:
            res = requests.get(img_src)
            res.raise_for_status()
            # Extract image name from the URL (e.g., 'hr_229605')
            img_name = extract_image_name_from_url(img_src)
            img_filename = os.path.join(image_folder, f'{img_name}.jpg')
            save_compressed_image(res.content, img_filename)
            print(f"Downloaded and compressed image {img_name} as {img_filename}")
        except Exception as e:
            print(f"Failed to download image {index + 1}: {e}")

    # Step 2: Upload images to Cloudinary and get URLs and sizes
    uploaded_urls = upload_images(image_folder)

    # Step 3: Save uploaded URLs to MongoDB
    save_to_mongodb(uploaded_urls)

    # Step 4: Clear 'pictures' folder for the next batch
    for img_file in os.listdir(image_folder):
        os.remove(os.path.join(image_folder, img_file))

    # Step 5: Increment the start index for the next batch
    start_index = end_index

print("All images processed and uploaded.")
