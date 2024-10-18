import cloudinary
import cloudinary.api
import os
import time

# Load environment variables for API data
api_data = os.getenv("API_DATA")
lst = api_data.split("_")

# Cloudinary setup (replace with your credentials)
cloudinary.config(
    cloud_name=lst[1],  # Your cloud_name from Cloudinary
    api_key=lst[2],     # Your api_key from Cloudinary
    api_secret=lst[3]   # Your api_secret from Cloudinary
)


count = 20
# Function to delete all resources (images)
def delete_all_images():
    try:
        # Delete all uploaded images in Cloudinary
        result = cloudinary.api.delete_all_resources(type='upload', resource_type='image')
        
        print(f"{count} : Deleted all images:")
        
    except cloudinary.exceptions.Error as e:
        print(f"Error deleting images:")

# Start the process
while count >0:
    delete_all_images()
    count -+1
    time.sleep(5)
    
