import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin
import time

class WebScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        self.output_dir = "parsed_content"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def sanitize_filename(self, filename):
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        return sanitized[:100]

    def get_page_content(self, url):
        try:
            print(f"Fetching {url}...")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_content(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        
        title = None
        h1_tag = soup.find('h1')
        if h1_tag:
            title = h1_tag.get_text(strip=True)
            print(f"Found title: {title}")
        
        content = []
        main_content = soup.find('div', class_='[&>*+*]:mt-5 grid whitespace-pre-wrap')
        
        if main_content:
            print("Found main content div")
            for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                text = element.get_text(strip=True)
                if text:
                    content.append(text)
        else:
            print("Main content div not found")

        return title or "Untitled", '\n\n'.join(content)

    def extract_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        
        # Find all links in the sidebar
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/'):
                full_url = urljoin(self.base_url, href)
                if full_url.startswith(self.base_url):
                    links.add(full_url)
        
        return links

    def save_content(self, title, content):
        if not content.strip():
            print(f"No content to save for {title}")
            return
            
        filename = self.sanitize_filename(title) + '.txt'
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Successfully saved: {filepath}")
            print(f"Content length: {len(content)} characters")
        except Exception as e:
            print(f"Error saving {filepath}: {e}")

    def crawl(self, start_url):
        queue = [start_url]
        
        while queue:
            current_url = queue.pop(0)
            
            if current_url in self.visited_urls:
                print(f"Already visited: {current_url}")
                continue
                
            print(f"\nProcessing: {current_url}")
            self.visited_urls.add(current_url)
            
            html = self.get_page_content(current_url)
            if not html:
                continue
            
            # Extract and save content
            title, content = self.extract_content(html)
            if content:
                self.save_content(title, content)
            else:
                print(f"No content extracted from {current_url}")
            
            # Get new links and add them to queue
            new_links = self.extract_links(html)
            for link in new_links:
                if link not in self.visited_urls and link not in queue:
                    queue.append(link)
            
            # Add a small delay between requests
            time.sleep(1)

def main():
    base_url = "https://ukr.ed-era.com"
    scraper = WebScraper(base_url)
    scraper.crawl(base_url)
    print("\nCrawling completed!")
    print(f"Total pages processed: {len(scraper.visited_urls)}")

if __name__ == "__main__":
    main()