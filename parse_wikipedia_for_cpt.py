import wikipediaapi
import pandas as pd
from tqdm import tqdm
import re

def setup_wiki_api():
    """Setup Wikipedia API for Ukrainian language"""
    user_agent = "Ukrainian Wikipedia Parser/1.0"
    wiki = wikipediaapi.Wikipedia(
        language='uk',  # Ukrainian language
        extract_format=wikipediaapi.ExtractFormat.WIKI,
        user_agent=user_agent
    )
    return wiki

def clean_text(text):
    """Clean Wikipedia text content"""
    # Remove multiple newlines
    text = re.sub(r'\n+', '\n', text)
    # Remove references [1], [2], etc.
    text = re.sub(r'\[\d+\]', '', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_category_members(wiki, category_name, max_articles=100):
    """Get articles from a category and its subcategories"""
    category = wiki.page(f"Категорія:{category_name}")  # Note the Ukrainian "Категорія"
    if not category.exists():
        print(f"Category 'Категорія:{category_name}' not found")
        return []
    
    articles = []
    for member in category.categorymembers.values():
        if len(articles) >= max_articles:
            break
            
        if member.namespace == 0:  # Regular article
            content = member.text
            if content:
                articles.append({
                    'title': member.title,
                    'text': clean_text(content),
                    'category': category_name
                })
    
    return articles

def parse_wiki_articles(categories_dict, max_articles_per_category=100):
    """Parse Wikipedia articles from given categories"""
    wiki = setup_wiki_api()
    articles_data = []
    
    for subject, categories in categories_dict.items():
        print(f"\nProcessing {subject} categories:")
        for category in categories:
            print(f"Fetching from {category}")
            articles = get_category_members(wiki, category, max_articles_per_category)
            articles_data.extend(articles)
            print(f"Found {len(articles)} articles")
    
    return pd.DataFrame(articles_data)

if __name__ == "__main__":
    # Categories organized by subject
    categories = {
        'history': [
            "Історія_України",
            "Київська_Русь",
            "Козацька_доба",
            "Гетьмани_України",
            "УНР",
            "Українська_революція",
            "Історичні_події_в_Україні",
            "Визначні_історичні_постаті_України"
        ],
        'language': [
            "Українська_мова",
            "Фонетика_української_мови",
            "Морфологія_української_мови",
            "Синтаксис_української_мови",
            "Лексикологія_української_мови",
            "Стилістика_української_мови",
            "Правопис_української_мови",
            "Пунктуація_української_мови"
        ],
        'literature': [
            "Українська_література",
            "Українські_письменники",
            "Українські_поети",
            "Давня_українська_література",
            "Література_XIX_століття",
            "Література_XX_століття",
            "Шевченко_Тарас_Григорович",
            "Українські_літературні_твори",
            "Літературні_напрями"
        ]
    }
    
    # Parse articles
    df = parse_wiki_articles(categories, max_articles_per_category=25)  # Reduced for testing
    
    # Save to CSV
    df.to_csv('ukrainian_wiki_articles.csv', index=False, encoding='utf-8')
    
    print(f"\nTotal articles collected: {len(df)}")
    print("\nArticles per category:")
    print(df['category'].value_counts())
    print("\nSample of titles:")
    print(df['title'].head())