import requests 
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

#from collections import defaultdict, Counter
import re

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# list of websites to search from 
website_urls = [
    "https://www.tomshardware.com/search",
    "https://www.pcmag.com/search/results",
    "https://www.pcworld.com/search"
]

# search terms 
search_terms = [
    "Desktop", 
    "Gaming Desktop", 
    "Pro Desktop"
]

key_words_gaming = [
    "iBUYPOWER",
    "ASUS", 
    "MSI", 
    "ACER", 
    "HP", 
    "CYBERPOWER", 
    "ALIENWARE",
    "Gigabyte", 
    "Vision", 
    "Aegis", 
    "Infinite", 
    "Razer", 
    "Microsoft"
]

key_words_pro = [
    "MSI",
    "Gigabyte", 
    "BRIX", 
    "Minisforum", 
    "Beelink", 
    "Zotac Zbox", 
    "Apple Mac Mini", 
    "HP Elite Mini", 
    "Cubi", 
    "Pro", 
    "Microsoft Surface",
]

headers = {"User-Agent": "Chrome/114.0.0.0 Safari/537.36"}

pattern_gaming = r'\b(' + '|'.join(re.escape(k) for k in key_words_gaming) + r')\b'
patter_pro = r'\b(' + '|'.join(re.escape(k) for k in key_words_pro) + r')\b'

pattern = [pattern_gaming, patter_pro]

def match_keywords(article_text, term_index):
    if term_index == 1 or term_index == 2:
        matches = re.findall(pattern[term_index-1], article_text, flags=re.IGNORECASE)
        if matches: 
            return list(match.lower() for match in matches), article_text
    else:
        matches_1 = re.findall(pattern[0], article_text, flags=re.IGNORECASE)
        matches_2 = re.findall(pattern[1], article_text, flags=re.IGNORECASE)
        if matches_1 or matches_2:
            return (list(set(list(match.lower() for match in matches_1) + list(match.lower() for match in matches_1)))), article_text
    return [], ''

def search_toms_hardware(website_url, search_terms, article_limit=3, word_limit=5000): 
    for term in search_terms:
        params = {"searchTerm": term}

        response = requests.get(website_url, params=params, headers=headers)
        print("Search URL:", response.url)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # get all the articles in one container
            results_container = soup.find("div", class_="listingResults")
            if results_container is None: 
                print(f"No results for {term}")
                continue

            # separate the individual articles from the container and store in new container
            articles = results_container.find_all("div", class_="listingResult")

            '''for article in articles[:3]:  # limit to first 5 articles
                # get the link tag <a>
                synopsis = article.find("p", class_="synopsis").get_text(strip=True)
                print("-", title, "\n")
                print("   Author:", author, "\n")
                print("   Link:", link, "\n")
                print("   Synopsis:", synopsis, "\n")'''

            matched_articles = {}
            matched_articles_keywords = {}
            matched_article_titles = {}
            matched_article_authors = {}
            for article in articles:
                current_article_text = ""
                author = article.find("span", style ="white-space:nowrap").get_text(strip=True)
                a_tag = article.find("a", class_="article-link")
                link = a_tag.get("href")
                title = a_tag.get("aria-label")
                response = requests.get(link, headers=headers)
                if response.status_code == 200:
                    opened_article = BeautifulSoup(response.text, "html.parser")
                    article_body = opened_article.find("div", id="article-body")
                    article_paragraphs = article_body.find_all("p")
                    for article_paragraph in article_paragraphs:
                        current_article_text += (article_paragraph.get_text(strip=True) + ' ')
                    term_index = search_terms.index(term)
                    a, b = match_keywords(current_article_text, term_index)
                    if len(b) != 0:
                        matched_articles[link] = b
                        matched_articles_keywords[link] = a
                        matched_article_titles[link] = title
                        matched_article_authors[link] = author
                else:
                    print(f"link: {link} did not work. (status code: {response.status_code})")
            
            i = 0
            for link, article_text in matched_articles.items():
                if i < article_limit:
                    word_count = len(article_text.lower().split())
                    print(f"Title: {matched_article_titles[link]}\nAuthor: {matched_article_authors[link]}")
                    print(f"Matched keywords: {matched_articles_keywords[link]}")
                    print(f"Matched Link: {link}\n")
                    if len(article_text.lower().split()) < word_limit:
                        print(f"Article Length:{word_count}\nMatched Article:\n{article_text}\n")
                        i += 1
                    else: 
                        print(f"Article exceeds limit: {word_count} words. Read full article at {link}\n")
                else: 
                    print(f"Limit reached, {article_limit} articles displayed.\n")
                    break
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")
    

    # search through each article on the page and match keywords (DONE)
    # if an article matches keywords (desktop, pro desktop, gaming desktop, MSI, ASUS, Cyberpower, etc.), summarize using LLM api (LLM to be chosen) (DONE)
    # after summarizing, do sentiment analysis on the article and provide bullet points of positive, neutral, and negative 
    # figure out how to send these as notifications to emails, and how to save to database for future reference 
    # allow user lookup in the database 

def search_pc_mag(website_url, search_terms, article_limit=3, word_limit=5000):
    for term in range(len(search_terms)):
        params = {"query": search_terms[term]}

        response = requests.get(website_url, params=params, headers=headers)
        print("Search URL:", response.url)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # get all the articles in one container
            results_container = soup.find("div", class_="flex-col")
            if results_container is None: 
                print(f"No results for {term}")
                continue

            # separate the individual articles from the container and store in new container
            articles = results_container.find_all("div", class_="dark:border-gray-600")

            matched_articles = {}
            matched_articles_keywords = {}
            matched_article_titles = {}
            matched_article_authors = {}

            print("Searching articles and matching keywords...\n")
            for article in articles:  
                # get the link tag <a>
                a_tag = article.find("a", attrs={"x-track-ga-click": True})
                link = "https://www.pcmag.com/"+a_tag.get("href")
                title = a_tag.get_text(strip=True)
                # synopsis = article.find("p", class_="line-clamp-2").get_text(strip=True)
                author = article.find_all("a",  attrs={"data-element": "author-name"})
                author_names = []
                for a in author: 
                    author_names.append(a.get_text(strip=True))
                '''
                print("-", title, "\n")
                print("   Author:", ", ".join(author_names), "\n")
                print("   Link:", "https://www.pcmag.com/"+link, "\n")
                print("   Synopsis:", synopsis, "\n")
                '''

                current_article_text = ""
                response = requests.get(link, headers=headers)
                if response.status_code == 200:
                    opened_article = BeautifulSoup(response.text, "html.parser")
                    article_body = opened_article.find("article")
                    if article_body is None: 
                        print(f"Article is empty at Link: {link}")
                        break
                    article_paragraphs = article_body.find_all("p")
                    for article_paragraph in article_paragraphs:
                        current_article_text += (article_paragraph.get_text(strip=True) + ' ')
                    term_index = term
                    a, b = match_keywords(current_article_text, term_index)
                    if len(b) != 0:
                        matched_articles[link] = b
                        matched_articles_keywords[link] = a
                        matched_article_titles[link] = title
                        matched_article_authors[link] = author_names
                else:
                    print(f"link: {link} did not work. (status code: {response.status_code})")
            
            i = 0
            for link, article_text in matched_articles.items():
                if i < article_limit:
                    word_count = len(article_text.lower().split())
                    print(f"Title: {matched_article_titles[link]}\nAuthor: {", ".join(matched_article_authors[link])}")
                    print(f"Matched keywords: {matched_articles_keywords[link]}")
                    print(f"Matched Link: {link}\n")
                    if len(article_text.lower().split()) < word_limit:
                        print(f"Article Length:{word_count}\nMatched Article:\n{article_text}\n")
                        i += 1
                    else: 
                        print(f"Article exceeds limit: {word_count} words. Read full article at {link}\n")
                else: 
                    print(f"Limit reached, {article_limit} articles displayed.\n")
                    break
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")

def search_pc_world(website_url, search_terms, article_limit=3, word_limit=5000):
    for term in range(len(search_terms)):
        params = {"query": search_terms[term],
                  "gsc.page": 1,
                  "gsc.tab": 0
                  }

        response = requests.Request("GET", website_url, params=params).prepare().url()
        print("Search URL:", response.url)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # get all the articles in one container
            results_container = soup.find("div", class_="gsc-results-wrapper-nooverlay gsc-results-wrapper-visible")
            if results_container is None: 
                print(f"No results for {search_terms[term]}")
                continue

            # separate the individual articles from the container and store in new container
            articles = results_container.find_all("div", class_="gsc-webResult gsc-result")

            matched_articles = {}
            matched_articles_keywords = {}
            matched_article_titles = {}
            matched_article_authors = {}

            print("Searching articles and matching keywords...\n")
            for article in articles:  
                # get the link tag <a>
                author = ""
                a_tag = article.find("a", class_="gs-title")
                link = a_tag.get("href")
                title = a_tag.get_text(strip=True)
                # synopsis = article.find("p", class_="line-clamp-2").get_text(strip=True)
                '''
                print("-", title, "\n")
                print("   Author:", ", ".join(author_names), "\n")
                print("   Link:", "https://www.pcmag.com/"+link, "\n")
                print("   Synopsis:", synopsis, "\n")
                '''

                current_article_text = ""
                response = requests.get(link, headers=headers)
                if response.status_code == 200:
                    opened_article = BeautifulSoup(response.text, "html.parser")
                    author = opened_article.find("span", class_="author vcard")
                    article_body = opened_article.find("div", id="link_wrapped_content")
                    if article_body is None: 
                        print(f"Article is empty at Link: {link}")
                        break
                    article_paragraphs = article_body.find_all("p")
                    for article_paragraph in article_paragraphs:
                        current_article_text += (article_paragraph.get_text(strip=True) + ' ')
                    term_index = term
                    a, b = match_keywords(current_article_text, term_index)
                    if len(b) != 0:
                        matched_articles[link] = b
                        matched_articles_keywords[link] = a
                        matched_article_titles[link] = title
                        matched_article_authors[link] = author
                else:
                    print(f"link: {link} did not work. (status code: {response.status_code})")
            
            i = 0
            for link, article_text in matched_articles.items():
                if i < article_limit:
                    word_count = len(article_text.lower().split())
                    print(f"Title: {matched_article_titles[link]}\nAuthor: {", ".join(matched_article_authors[link])}")
                    print(f"Matched keywords: {matched_articles_keywords[link]}")
                    print(f"Matched Link: {link}\n")
                    if len(article_text.lower().split()) < word_limit:
                        print(f"Article Length:{word_count}\nMatched Article:\n{article_text}\n")
                        i += 1
                    else: 
                        print(f"Article exceeds limit: {word_count} words. Read full article at {link}\n")
                else: 
                    print(f"Limit reached, {article_limit} articles displayed.\n")
                    break
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")

search_functions = [search_toms_hardware, search_pc_mag, search_pc_world]

i = 0
'''for website_url in website_urls:
    search_functions[i](website_url, search_terms, article_limit=1, word_limit=1000)
    i += 1'''

search_pc_world("https://www.pcworld.com/search", search_terms)