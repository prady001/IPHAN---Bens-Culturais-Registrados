import requests
from bs4 import BeautifulSoup
import io
from PIL import Image
import os

# Define the URL
url = "https://bcr.iphan.gov.br/wp-json/tainacan/v2/items/?perpage=96&order=ASC&orderby=date&exposer=html&paged=1"

# Function to download image from URL
def download_image(download_path, url, file_name):
    try:
        image_content = requests.get(url).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)
        file_path = os.path.join(download_path, file_name)

        with open(file_path, "wb") as f:
            image.save(f, "JPEG")

        print(f"Successfully downloaded {file_name}")
    except Exception as e:
        print(f'FAILED - {e}')

# Function to save description to a text file
def save_description(download_path, file_name, description):
    try:
        file_path = os.path.join(download_path, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(description)
        print(f"Successfully saved description to {file_name}")
    except Exception as e:
        print(f'FAILED - {e}')

# Fetch the HTML data
response = requests.get(url)

# Print the response status and content for debugging
print(f"Response Status Code: {response.status_code}")
print("Response Content:")
print(response.text[:500])  # Print the first 500 characters of the response for inspection

# Parse HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Create directories to save images and descriptions if they don't exist
download_path = "imgs/"
os.makedirs(download_path, exist_ok=True)

# Extract image URLs, titles, and descriptions from the table
table = soup.find('table', {'border': '1'})  # Find the table by its border attribute
if table:
    headers = [th.text.strip() for th in table.find('thead').find_all('th')]
    rows = table.find('tbody').find_all('tr')
    
    image_counter = 0
    max_images = 20  # Limit to 20 images
    
    for row in rows:
        if image_counter >= max_images:
            break

        cells = row.find_all('td')
        data = {headers[i]: cells[i].text.strip() for i in range(len(cells))}
        
        # Extract title and description (assuming title and description are in specific columns)
        description = data.get('Descrição', 'No Description')
        title = data.get('Denominação', 'No Title')
        
        print(f"Title: {title}")
        print(f"Description: {description}")
        
        # Save description to a text file
        description_filename = f"{title}.txt".replace('/', '_').replace(' ', '_')
        save_description(download_path, description_filename, description)
        
        # Extract and download images (assuming images URLs are in 'Mídias' column)
        media_column = cells[headers.index('Mídias')].find_all('img') if 'Mídias' in headers else []
        
        if media_column:
            img_tag = media_column[0]  # Only get the first image
            img_url = img_tag.get('src')
            if img_url and img_url.startswith('http'):
                # Generate a filename based on the title
                img_filename = f"{title}.jpg".replace('/', '_').replace(' ', '_')  # sanitize filename
                download_image(download_path, img_url, img_filename)
                image_counter += 1

else:
    print("Table not found in the HTML content.")
