import os
from flask import Flask, render_template, request, send_file
from bs4 import BeautifulSoup
import requests
import pandas as pd

app = Flask(__name__)

# Function to scrape data from URL
def scrape_data(url):
    try:
        response = requests.get(url, timeout=60)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Example: Extracting all links from the webpage
        links = soup.find_all('a')
        extracted_links = [link.get('href') for link in links]
        return extracted_links
    except Exception as e:
        print(f"Error scraping: {str(e)}")
        return None

# Function to create 'downloads' directory if it doesn't exist
def create_downloads_dir():
    downloads_dir = os.path.join(app.root_path, 'downloads')
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)

# Route to serve the HTML file
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission and perform scraping
@app.route('/scrape', methods=['POST'])
def scrape():
    if request.method == 'POST':
        url = request.form['url']
        extracted_links = scrape_data(url)
        if extracted_links:
            return render_template('index.html', url=url, extracted_links=extracted_links)
        else:
            error_message = f"Error scraping data from URL: {url}"
            return render_template('index.html', error=error_message)

# Route to export data as Excel file
@app.route('/export_excel', methods=['POST'])
def export_excel():
    if request.method == 'POST':
        url = request.form['url']
        extracted_links = scrape_data(url)
        if extracted_links:
            create_downloads_dir()  # Create 'downloads' directory if it doesn't exist
            
            # Create a pandas DataFrame
            df = pd.DataFrame({'Links': extracted_links})
            
            # Generate a filename for the Excel file
            filename = 'scraped_data.xlsx'
            filepath = os.path.join(app.root_path, 'downloads', filename)
            
            # Export DataFrame to Excel
            df.to_excel(filepath, index=False)
            
            # Send the Excel file as a response
            return send_file(filepath, as_attachment=True)
        else:
            error_message = f"Error exporting data as Excel for URL: {url}"
            return render_template('index.html', error=error_message)

if __name__ == '__main__':
    app.run(debug=True)
