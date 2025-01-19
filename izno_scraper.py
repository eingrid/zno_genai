import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin
import time

class IznoScraper:
    def __init__(self):
        self.base_url = "https://izno.com.ua"
        self.visited_urls = set()
        self.output_dir = "izno_content"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def sanitize_filename(self, filename):
        # Remove invalid characters and limit length
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        return sanitized[:100]

    def get_page_content(self, url):
        try:
            print(f"Fetching {url}...")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            response.encoding = 'utf-8'  # Set encoding explicitly
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_content(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the title
        title = None
        h1_tag = soup.find('h1', class_='entry-title')
        if h1_tag:
            title = h1_tag.get_text(strip=True)
            print(f"Found title: {title}")
        
        # Find the main content div
        content = []
        entry_div = soup.find('div', class_='entry')
        
        if entry_div:
            print("Found main content div")
            # Extract all text content, including nested elements
            for element in entry_div.stripped_strings:
                content.append(element)
        else:
            print("Main content div not found")

        return title or "Untitled", '\n'.join(content)

    def extract_article_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        # Find all article links
        for article in soup.find_all('article'):
            link_tag = article.find('h3', class_='loop-title').find('a')
            if link_tag and 'href' in link_tag.attrs:
                url = link_tag['href']
                title = link_tag.get_text(strip=True)
                links.append((url, title))
        
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

    def crawl(self):
        # Start with the history category page
        category_url = "https://izno.com.ua/category/istoriya-ukrayini/"
        page = 1
        all_links = []
        
        while True:
            url = f"{category_url}page/{page}/" if page > 1 else category_url
            html = self.get_page_content(url)
            
            if not html:
                break
                
            links = self.extract_article_links(html)
            if not links:
                break
                
            all_links.extend(links)
            print(f"Found {len(links)} articles on page {page}")
            page += 1
            time.sleep(1)  # Be polite to the server
        
        print(f"\nTotal articles found: {len(all_links)}")
        
        # Process each article
        for url, title in all_links:
            if url in self.visited_urls:
                continue
                
            print(f"\nProcessing article: {title}")
            self.visited_urls.add(url)
            
            html = self.get_page_content(url)
            if not html:
                continue
            
            article_title, content = self.extract_content(html)
            if content:
                self.save_content(article_title, content)
            
            time.sleep(1)  # Be polite to the server

def main():
    scraper = IznoScraper()
    scraper.crawl()
    print("\nScraping completed!")
    print(f"Total articles processed: {len(scraper.visited_urls)}")

if __name__ == "__main__":
    main()