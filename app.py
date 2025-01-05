from flask import Flask, request, render_template, send_file
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Folder to store temporary files for download
UPLOAD_FOLDER = 'scraped_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    scraped_content = None
    file_path = None
    if request.method == 'POST':
        url = request.form.get('url')
        content_type = request.form.get('content_type')
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            if content_type == 'title':
                scraped_content = soup.title.string if soup.title else 'No title found'
            elif content_type == 'headers':
                headers = [header.get_text() for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
                scraped_content = '\n'.join(headers) if headers else 'No headers found'
            elif content_type == 'links':
                links = [a['href'] for a in soup.find_all('a', href=True)]
                scraped_content = '\n'.join(links) if links else 'No links found'
            elif content_type == 'images':
                images = [img['src'] for img in soup.find_all('img', src=True)]
                scraped_content = '\n'.join(images) if images else 'No images found'
            elif content_type == 'meta_description':
                meta_description = soup.find('meta', attrs={'name': 'description'})
                scraped_content = meta_description['content'] if meta_description else 'No meta description found'
            elif content_type == 'paragraphs':
                paragraphs = [p.get_text() for p in soup.find_all('p')]
                scraped_content = '\n'.join(paragraphs) if paragraphs else 'No paragraphs found'
            elif content_type == 'links_with_text':
                links = [f"{a.get_text()} -> {a['href']}" for a in soup.find_all('a', href=True)]
                scraped_content = '\n'.join(links) if links else 'No links with text found'
            elif content_type == 'images_with_alt':
                images = [f"{img['alt']} -> {img['src']}" for img in soup.find_all('img', src=True, alt=True)]
                scraped_content = '\n'.join(images) if images else 'No images with alt text found'
            elif content_type == 'lists':
                lists = []
                for ul in soup.find_all('ul'):
                    lists.append(f"Unordered List: {', '.join([li.get_text() for li in ul.find_all('li')])}")
                for ol in soup.find_all('ol'):
                    lists.append(f"Ordered List: {', '.join([li.get_text() for li in ol.find_all('li')])}")
                scraped_content = '\n'.join(lists) if lists else 'No lists found'
            else:
                scraped_content = "Invalid content type selected."

            # Create a text file with the scraped content
            if scraped_content:
                file_path = os.path.join(UPLOAD_FOLDER, 'scraped_content.txt')
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(scraped_content)

        except Exception as e:
            scraped_content = f"An error occurred: {e}"

    return render_template('index.html', scraped_content=scraped_content, file_path=file_path)

@app.route('/download')
def download_file():
    file_path = request.args.get('file')
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
