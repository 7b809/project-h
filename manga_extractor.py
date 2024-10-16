from bs4 import BeautifulSoup
import json

def extract_manga_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract title and alternate title
    title = soup.select_one('.manga-item__link').text.strip() if soup.select_one('.manga-item__link') else "N/A"
    alt_title = soup.select_one('.manga-item__detail .line-clamp-2').text.strip() if soup.select_one('.manga-item__detail .line-clamp-2') else "N/A"

    # Extract categories
    category_link = soup.select_one('.manga-item__cat-link')
    categories = []
    if category_link:
        categories.append({
            "name": category_link.text.strip(),
            "url": category_link['href']
        })

    

    # Extract image links
    image_tag = soup.select_one('.manga-item__img img')
    image = {
        "src": image_tag['src'] if image_tag and 'src' in image_tag.attrs else "N/A",
        "srcset": image_tag['srcset'].split(", ") if image_tag and 'srcset' in image_tag.attrs else []
    }

    # Extract tags
    tag_elements = soup.select('.manga-item__tags span')
    tags = [tag.text.strip() for tag in tag_elements]

    # Extract read link
    read_link = soup.select_one('.btn-read')['href'] if soup.select_one('.btn-read') else "N/A"

     #Extract rating, views, and image count
    views = soup.select_one('.fa-eye + .text-sm').text.strip() if soup.select_one('.fa-eye + .text-sm') else "N/A"
    rating = soup.select_one('.fa-star + .text-sm').text.strip() if soup.select_one('.fa-star + .text-sm') else "N/A"
    image_count = soup.select_one('.fa-images + .text-sm').text.strip() if soup.select_one('.fa-images + .text-sm') else "N/A"


    # Build the JSON data
    manga_data = {
        "title": title,
        "alt_title": alt_title,
        "categories": categories,
        "image": image,
        "tags": tags,
        "metadata": {
            "views": views,
            "rating": rating,
            "image_count": image_count
        },
        "read_link": read_link
    }

    return json.dumps(manga_data, ensure_ascii=False, indent=4)
