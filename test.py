import requests 
from bs4 import BeautifulSoup

#from collections import defaultdict, Counter
import re

# list of websites to search from 
website_urls = [
    "https://www.tomshardware.com/search",
    "https://www.pcmag.com/search/results",
    "https://thepcenthusiast.com/",
    "https://hothardware.com/search",
    "https://pcper.com/",
    "https://gamerant.com/search",
    "https://www.windowscentral.com/search",
    "https://www.techradar.com/search"
]

# search terms 
search_terms = [
    "gaming desktop",
    "pro desktop"
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
    "Razer"
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
    "Apple", 
    "Macbook"
]

headers = {"User-Agent": "Chrome/114.0.0.0 Safari/537.36"}

pattern_gaming = r'\b(' + '|'.join(re.escape(k) for k in key_words_gaming) + r')(?:[\w\'\-]*)'
pattern_pro = r'\b(' + '|'.join(re.escape(k) for k in key_words_pro) + r')(?:[\w\'\-]*)'

pattern = [pattern_gaming, pattern_pro]

def match_keywords(article_text, term_index):
    if term_index == 1 or term_index == 2:
        matches = re.findall(pattern[term_index-1], article_text, flags=re.IGNORECASE)
        if matches: 
            return list(set(match.lower() for match in matches))
    else:
        matches_1 = re.findall(pattern[0], article_text, flags=re.IGNORECASE)
        matches_2 = re.findall(pattern[1], article_text, flags=re.IGNORECASE)
        if matches_1 or matches_2:
            return (list(set(list(match.lower() for match in matches_1) + list(match.lower() for match in matches_2))))
    return []

def search_toms_hardware(website_url=website_urls[0], search_terms=search_terms, article_limit=1, word_limit=500): 
    #print("\nSearching on website: https://www.tomshardware.com")
    matched_articles = {}
    matched_articles_keywords = {}
    matched_articles_titles = {}
    matched_articles_authors = {}
    matched_articles_publish_date = {}
    for term in range(len(search_terms)):
        i = 0
        params = {"searchTerm": search_terms[term]}

        response = requests.get(website_url, params=params, headers=headers)
        #print("Search URL:", response.url)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # get all the articles in one container
            results_container = soup.find("div", class_="listingResults")
            if results_container is None: 
                #print(f"No results for {search_terms[term]}\n")
                continue

            # separate the individual articles from the container and store in new container
            articles = results_container.find_all("div", class_="listingResult")
            if not articles: 
                print(f"No results for {search_terms[term]}\n")
                continue
            '''for article in articles[:3]:  # limit to first 5 articles
                # get the link tag <a>
                synopsis = article.find("p", class_="synopsis").get_text(strip=True)
                print("-", title, "\n")
                print("   Author:", author, "\n")
                print("   Link:", link, "\n")
                print("   Synopsis:", synopsis, "\n")'''

            at_least_one_article = False
            for article in articles:
                if i < article_limit:
                    current_article_text = ""
                    author = article.find("span", style ="white-space:nowrap").get_text(strip=True)
                    a_tag = article.find("a", class_="article-link")
                    link = a_tag.get("href")
                    title = a_tag.get("aria-label")
                    publish_date = article.find("time", class_="date-with-prefix").get_text(strip=True)
                    response = requests.get(link, headers=headers)
                    if response.status_code == 200:
                        opened_article = BeautifulSoup(response.text, "html.parser")
                        article_body = opened_article.find("div", id="article-body")
                        article_paragraphs = article_body.find_all("p")
                        for article_paragraph in article_paragraphs:
                            current_article_text += (article_paragraph.get_text(strip=True) + ' ')
                        if len(current_article_text.lower().split()) > word_limit:
                            continue
                        term_index = term
                        matched = match_keywords(current_article_text, term_index)
                        if len(matched) != 0:
                            matched_articles[link] = current_article_text
                            matched_articles_keywords[link] = matched
                            matched_articles_titles[link] = title
                            matched_articles_authors[link] = author
                            matched_articles_publish_date[link] = publish_date
                            i += 1
                            at_least_one_article = True
                    else:
                        #print(f"link: {link} did not work. (status code: {response.status_code})")
                        pass
                else:
                    #print(f"Limit reached, {article_limit} articles displayed.\n")
                    break
            if not at_least_one_article:
                #print(f"No articles found within {word_limit} word limit.\n")
                pass
            '''
            i = 0
            at_least_one_article = False
            for link, article_text in matched_articles.items():
                if i < article_limit:
                    if len(article_text.lower().split()) < word_limit:
                        word_count = len(article_text.lower().split())
                        print(f"Title: {matched_articles_titles[link]}\nAuthor: {matched_articles_authors[link]}")
                        print(f"Publish Date: {matched_articles_publish_date[link]}")
                        print(f"Matched keywords: {matched_articles_keywords[link]}")
                        print(f"Matched Link: {link}\n")
                        print(f"Article Length:{word_count}\nMatched Article:\n{article_text}\n")
                        i += 1
                        at_least_one_article = True
                    else: 
                        #print(f"Article exceeds limit: {word_count} words. Read full article at {link}\n")
                        pass
                else: 
                    print(f"Limit reached, {article_limit} articles displayed.\n")
                    break
            if not at_least_one_article:
                print(f"No articles found within {word_limit} word limit.\n")'''
        else:
            #print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")
            pass
    return matched_articles, matched_articles_keywords, matched_articles_titles, matched_articles_authors, matched_articles_publish_date
    
    # search through each article on the page and match keywords (DONE)
    # if an article matches keywords (desktop, pro desktop, gaming desktop, MSI, ASUS, Cyberpower, etc.), summarize using LLM api (LLM to be chosen) (DONE)
    # after summarizing, do sentiment analysis on the article and provide bullet points of positive, neutral, and negative 
    # figure out how to send these as notifications to emails, and how to save to database for future reference 
    # allow user lookup in the database 

def search_pc_mag(website_url=website_urls[1], search_terms=search_terms, article_limit=1, word_limit=500):
    print("Searching on website: https://www.pcmag.com")
    for term in range(len(search_terms)):
        params = {"query": search_terms[term]}

        response = requests.get(website_url, params=params, headers=headers)
        print("Search URL:", response.url)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # get all the articles in one container
            results_container = soup.find("div", class_="flex flex-col gap-4")
            if results_container is None: 
                print(f"No results for {search_terms[term]}\n")
                continue

            # separate the individual articles from the container and store in new container
            articles = results_container.find_all("div", class_="dark:border-gray-600")
            if not articles: 
                print(f"No results for {search_terms[term]}\n")
                continue
            matched_articles = {}
            matched_articles_keywords = {}
            matched_article_titles = {}
            matched_article_authors = {}
            matched_article_publish_date = {}

            print("Searching articles and matching keywords...\n")
            for article in articles:  
                # get the link tag <a>
                a_tag = article.find("a", attrs={"x-track-ga-click": True})
                link = "https://www.pcmag.com/"+a_tag.get("href")
                title = a_tag.get_text(strip=True)
                publish_date = article.find("span", attrs={"data-content-published-date": True}).get_text(strip=True)
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
                    matched = match_keywords(current_article_text, term_index)
                    if len(matched) != 0:
                        matched_articles[link] = current_article_text
                        matched_articles_keywords[link] = matched
                        matched_article_titles[link] = title
                        matched_article_authors[link] = author_names
                        matched_article_publish_date[link] = publish_date
                else:
                    print(f"link: {link} did not work. (status code: {response.status_code})")
            
            i = 0
            at_least_one_article = False
            for link, article_text in matched_articles.items():
                if i < article_limit:
                    if len(article_text.lower().split()) < word_limit:
                        word_count = len(article_text.lower().split())
                        print(f"Title: {matched_article_titles[link]}\nAuthor: {", ".join(matched_article_authors[link])}")
                        print(f"Publish Date: {matched_article_publish_date[link]}")
                        print(f"Matched keywords: {matched_articles_keywords[link]}")
                        print(f"Matched Link: {link}\n")
                        print(f"Article Length:{word_count}\nMatched Article:\n{article_text}\n")
                        i += 1
                        at_least_one_article = True
                    else: 
                        #print(f"Article exceeds limit: {word_count} words. Read full article at {link}\n")
                        pass
                else: 
                    print(f"Limit reached, {article_limit} articles displayed.\n")
                    break
            if not at_least_one_article:
                print(f"No articles found within {word_limit} word limit.\n")
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")

def search_the_pc_enthusiast(website_url=website_urls[2], search_terms=search_terms, article_limit=1, word_limit=500):
    print("Searching on website: https://thepcenthusiast.com")
    for term in range(len(search_terms)):
        params = {"s": search_terms[term]}

        response = requests.get(website_url, params=params, headers=headers)
        print("Search URL:", response.url)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # get all the articles in one container
            results_container = soup.find("main", class_="site-main")
            no_content = results_container.find("div", class_="no-results")
            if no_content is not None: 
                print(f"No results for {search_terms[term]}\n")
                continue
            # separate the individual articles from the container and store in new container
            articles = results_container.find_all("div", class_="inside-article")
            if not articles: 
                print(f"No results for {search_terms[term]}\n")
                continue
            matched_articles = {}
            matched_articles_keywords = {}
            matched_article_titles = {}
            matched_article_authors = {}
            matched_article_publish_date = {}
            print("Searching articles and matching keywords...\n")
            for article in articles:  
                # get the link tag <a>
                author = article.find("span", class_="author-name").get_text(strip=True)
                a_tag = article.find("a", rel="bookmark")
                link = a_tag.get("href")
                title = a_tag.get_text(strip=True)
                publish_date = article.find("time", class_="published").get_text(strip=True)
                
                '''print("-", title, "\n")
                print("   Author:", ", ".join(author_names), "\n")
                print("   Link:", "https://www.pcmag.com/"+link, "\n")
                print("   Synopsis:", synopsis, "\n")'''
                

                current_article_text = ""
                response = requests.get(link, headers=headers)
                if response.status_code == 200:
                    opened_article = BeautifulSoup(response.text, "html.parser")
                    article_body = opened_article.find("div", class_="entry-content")
                    if article_body is None: 
                        print(f"Article is empty at Link: {link}")
                        break
                    article_paragraphs = article_body.find_all("p", class_=False, id=False)
                    for article_paragraph in article_paragraphs:
                        current_article_text += (article_paragraph.get_text(strip=True) + ' ')
                    term_index = term
                    matched = match_keywords(current_article_text, term_index)
                    if len(matched) != 0:
                        matched_articles[link] = current_article_text
                        matched_articles_keywords[link] = matched
                        matched_article_titles[link] = title
                        matched_article_authors[link] = author
                        matched_article_publish_date[link] = publish_date
                else:
                    print(f"link: {link} did not work. (status code: {response.status_code})")
            
            i = 0
            at_least_one_article = False
            for link, article_text in matched_articles.items():
                if i < article_limit:
                    if len(article_text.lower().split()) < word_limit:
                        word_count = len(article_text.lower().split())
                        print(f"Title: {matched_article_titles[link]}\nAuthor: {matched_article_authors[link]}")
                        print(f"Publish Date: {matched_article_publish_date[link]}")
                        print(f"Matched keywords: {matched_articles_keywords[link]}")
                        print(f"Matched Link: {link}\n")
                        print(f"Article Length:{word_count}\nMatched Article:\n{article_text}\n")
                        i += 1
                        at_least_one_article = True
                    else: 
                        #print(f"Article exceeds limit: {word_count} words. Read full article at {link}\n")
                        pass
                else: 
                    print(f"Limit reached, {article_limit} articles displayed.\n")
                    break
            if not at_least_one_article:
                print(f"No articles found within {word_limit} word limit.\n")
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")

def search_hothardware(website_url=website_urls[3], search_terms=search_terms, article_limit=1, word_limit=500):
    print("Searching on website: https://hothardware.com/search")
    for term in range(len(search_terms)):
        params = {"a": "all",
                  "s": search_terms[term]}

        response = requests.get(website_url, params=params, headers=headers)
        print("Search URL:", response.url)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # get all the articles in one container
            results_container = soup.find("div", class_="content-list")
            if results_container is None: 
                print(f"No results for {search_terms[term]}")
                continue

            # separate the individual articles from the container and store in new container
            articles = results_container.find_all("div", class_="cl-item")
            if not articles: 
                print(f"No results for {search_terms[term]}\n")
                continue
            matched_articles = {}
            matched_articles_keywords = {}
            matched_article_titles = {}
            matched_article_authors = {}
            matched_article_publish_date = {}
            print("Searching articles and matching keywords...\n")
            for article in articles:  
                # get the link tag <a>
                a_tag = article.find("a", class_=False, id=False)
                author = a_tag.get_text(strip=True)
                title_link_tag = article.find("a", class_="black p-name u-url")
                link = "https://hothardware.com" + title_link_tag.get("href")
                title = title_link_tag.get_text(strip=True)
                
                publish_date = article.find("div", class_="cli-byline").get_text(strip=True).split('-')[-1].strip()
                
                '''print("-", title, "\n")
                print("   Author:", ", ".join(author_names), "\n")
                print("   Link:", "https://www.pcmag.com/"+link, "\n")
                print("   Synopsis:", synopsis, "\n")'''
                

                current_article_text = ""
                response = requests.get(link, headers=headers)
                if response.status_code == 200:
                    opened_article = BeautifulSoup(response.text, "html.parser")
                    current_article_text = opened_article.find("div", class_="cn-body e-content").get_text(strip=True)
                    if current_article_text is None: 
                        print(f"Article is empty at Link: {link}")
                        break
                    '''article_paragraphs = article_body.find_all("p", class_=False, id=False)
                    for article_paragraph in article_paragraphs:
                        current_article_text += (article_paragraph.get_text(strip=True) + ' ')'''
                    term_index = term
                    matched = match_keywords(current_article_text, term_index)
                    if len(matched) != 0:
                        matched_articles[link] = current_article_text
                        matched_articles_keywords[link] = matched
                        matched_article_titles[link] = title
                        matched_article_authors[link] = author
                        matched_article_publish_date[link] = publish_date
                else:
                    print(f"link: {link} did not work. (status code: {response.status_code})")
            
            i = 0
            at_least_one_article = False
            for link, article_text in matched_articles.items():
                if i < article_limit:
                    if len(article_text.lower().split()) < word_limit:
                        word_count = len(article_text.lower().split())
                        print(f"Title: {matched_article_titles[link]}\nAuthor: {matched_article_authors[link]}")
                        print(f"Publish Date: {matched_article_publish_date[link]}")
                        print(f"Matched keywords: {matched_articles_keywords[link]}")
                        print(f"Matched Link: {link}\n")
                        print(f"Article Length:{word_count}\nMatched Article:\n{article_text}\n")
                        i += 1
                        at_least_one_article = True
                    else: 
                        #print(f"Article exceeds limit: {word_count} words. Read full article at {link}\n")
                        pass
                else: 
                    print(f"Limit reached, {article_limit} articles displayed.\n")
                    break
            if not at_least_one_article:
                print(f"No articles found within {word_limit} word limit.\n")
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")

def search_pc_perspective(website_url=website_urls[4], search_terms=search_terms, article_limit=1, word_limit=500):
    print("Searching on website: https://pcper.com")
    for term in range(len(search_terms)):
        params = {"s": search_terms[term]}

        response = requests.get(website_url, params=params, headers=headers)
        print("Search URL:", response.url)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # get all the articles in one container
            results_container = soup.find("div", class_="paginated_content")
            if results_container is None: 
                print(f"No results for {search_terms[term]}")
                continue

            # separate the individual articles from the container and store in new container
            articles = results_container.find_all("article", class_="hentry")
            if not articles: 
                print(f"No results for {search_terms[term]}\n")
                continue
            matched_articles = {}
            matched_articles_keywords = {}
            matched_article_titles = {}
            matched_article_authors = {}
            matched_article_publish_date = {}
            print("Searching articles and matching keywords...\n")
            for article in articles:  
                # get the link tag <a>
                author = article.find("a", rel="author").get_text(strip=True)
                a_tag = article.find("a", class_="et-accent-color")
                link = a_tag.get("href")
                title = a_tag.get_text(strip=True)
                publish_date = article.find("span", class_="updated").get_text(strip=True)
                
                '''print("-", title, "\n")
                print("   Author:", ", ".join(author_names), "\n")
                print("   Link:", "https://www.pcmag.com/"+link, "\n")
                print("   Synopsis:", synopsis, "\n")'''
                

                current_article_text = ""
                response = requests.get(link, headers=headers)
                if response.status_code == 200:
                    opened_article = BeautifulSoup(response.text, "html.parser")
                    article_body = opened_article.find("div", class_="et-l et-l--post")
                    if article_body is None: 
                        print(f"Article is empty at Link: {link}")
                        break
                    article_paragraphs = article_body.find_all("p", class_=False, id=False)
                    for article_paragraph in article_paragraphs:
                        current_article_text += (article_paragraph.get_text(strip=True) + ' ')
                    term_index = term
                    matched = match_keywords(current_article_text, term_index)
                    if len(matched) != 0:
                        matched_articles[link] = current_article_text
                        matched_articles_keywords[link] = matched
                        matched_article_titles[link] = title
                        matched_article_authors[link] = author
                        matched_article_publish_date[link] = publish_date
                else:
                    print(f"link: {link} did not work. (status code: {response.status_code})")
            
            i = 0
            at_least_one_article = False
            for link, article_text in matched_articles.items():
                if i < article_limit:
                    if len(article_text.lower().split()) < word_limit:
                        word_count = len(article_text.lower().split())
                        print(f"Title: {matched_article_titles[link]}\nAuthor: {matched_article_authors[link]}")
                        print(f"Publish Date: {matched_article_publish_date[link]}")
                        print(f"Matched keywords: {matched_articles_keywords[link]}")
                        print(f"Matched Link: {link}\n")
                        print(f"Article Length:{word_count}\nMatched Article:\n{article_text}\n")
                        i += 1
                        at_least_one_article = True
                    else: 
                        #print(f"Article exceeds limit: {word_count} words. Read full article at {link}\n")
                        pass
                else: 
                    print(f"Limit reached, {article_limit} articles displayed.\n")
                    break
            if not at_least_one_article:
                print(f"No articles found within {word_limit} word limit.\n")
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")

def search_gamerant(website_url=website_urls[5], search_terms=search_terms, article_limit=1, word_limit=500):
    print("Searching on website: https://gamerant.com")
    for term in range(len(search_terms)):
        params = {"q": search_terms[term]}

        response = requests.get(website_url, params=params, headers=headers)
        print("Search URL:", response.url)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # get all the articles in one container
            results_container = soup.find("section", class_="listing-content")
            if results_container is None: 
                print(f"No results for {search_terms[term]}")
                continue

            # separate the individual articles from the container and store in new container
            articles = results_container.find_all("div", class_="article")
            if not articles: 
                print(f"No results for {search_terms[term]}\n")
                continue
            matched_articles = {}
            matched_articles_keywords = {}
            matched_article_titles = {}
            matched_article_authors = {}
            matched_article_publish_date = {}
            print("Searching articles and matching keywords...\n")
            for article in articles:  
                # get the link tag <a>
                author = article.find("a", rel="author").get_text(strip=True)
                a_tag = article.find("a", class_=False, id=False)
                link = "https://gamerant.com" + a_tag.get("href")
                title = a_tag.get_text(strip=True)
                publish_date = article.find("time", class_="display-card-date").get_text(strip=True)
                '''print("-", title, "\n")
                print("   Author:", ", ".join(author_names), "\n")
                print("   Link:", "https://www.pcmag.com/"+link, "\n")
                print("   Synopsis:", synopsis, "\n")'''
                

                current_article_text = ""
                response = requests.get(link, headers=headers)
                if response.status_code == 200:
                    opened_article = BeautifulSoup(response.text, "html.parser")
                    article_body = opened_article.find("div", class_="content-block-regular")
                    if article_body is None: 
                        print(f"Article is empty at Link: {link}")
                        break
                    article_paragraphs = article_body.find_all("p", class_=False, id=False)
                    for article_paragraph in article_paragraphs:
                        current_article_text += (article_paragraph.get_text(strip=True) + ' ')
                    term_index = term
                    matched = match_keywords(current_article_text, term_index)
                    if len(matched) != 0:
                        matched_articles[link] = current_article_text
                        matched_articles_keywords[link] = matched
                        matched_article_titles[link] = title
                        matched_article_authors[link] = author
                        matched_article_publish_date[link] = publish_date
                else:
                    print(f"link: {link} did not work. (status code: {response.status_code})")
            
            i = 0
            at_least_one_article = False
            for link, article_text in matched_articles.items():
                if i < article_limit:
                    if len(article_text.lower().split()) < word_limit:
                        word_count = len(article_text.lower().split())
                        print(f"Title: {matched_article_titles[link]}\nAuthor: {matched_article_authors[link]}")
                        print(f"Publish Date: {matched_article_publish_date[link]}")
                        print(f"Matched keywords: {matched_articles_keywords[link]}")
                        print(f"Matched Link: {link}\n")
                        print(f"Article Length:{word_count}\nMatched Article:\n{article_text}\n")
                        i += 1
                        at_least_one_article = True
                    else: 
                        #print(f"Article exceeds limit: {word_count} words. Read full article at {link}\n")
                        pass
                else: 
                    print(f"Limit reached, {article_limit} articles displayed.\n")
                    break
            if not at_least_one_article:
                print(f"No articles found within {word_limit} word limit.\n")
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")

def search_windows_central(website_url=website_urls[6], search_terms=search_terms, article_limit=1, word_limit=500):
    print("Searching on website: https://www.windowscentral.com")
    for term in range(len(search_terms)):
        params = {"searchTerm": search_terms[term],
                  "dateRange": "DATE_RANGE_12_MONTHS"}

        response = requests.get(website_url, params=params, headers=headers)
        print("Search URL:", response.url)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # get all the articles in one container
            results_container = soup.find("div", class_="listingResults")
            if results_container is None: 
                print(f"No results for {search_terms[term]}")
                continue

            # separate the individual articles from the container and store in new container
            articles = results_container.find_all("div", class_="listingResult")
            if not articles: 
                print(f"No results for {search_terms[term]}\n")
                continue
            matched_articles = {}
            matched_articles_keywords = {}
            matched_article_titles = {}
            matched_article_authors = {}
            matched_article_publish_date = {}
            print("Searching articles and matching keywords...\n")
            for article in articles:  

                # get the link tag <a>
                author = article.find("span", style="white-space:nowrap").get_text(strip=True)
                link = article.find("a", class_="article-link").get("href")
                title = article.find("h3", class_="article-name").get_text(strip=True)
                publish_date = article.find("time", class_="no-wrap relative-date date-with-prefix").get_text(strip=True)
                
                '''print("-", title, "\n")
                print("   Author:", ", ".join(author_names), "\n")
                print("   Link:", "https://www.pcmag.com/"+link, "\n")
                print("   Synopsis:", synopsis, "\n")'''
                

                current_article_text = ""
                response = requests.get(link, headers=headers)
                if response.status_code == 200:
                    opened_article = BeautifulSoup(response.text, "html.parser")
                    article_body = opened_article.find("div", id="article-body")
                    if article_body is None: 
                        print(f"Article is empty at Link: {link}")
                        break
                    article_paragraphs = article_body.find_all("p", class_=False, id=False)
                    for article_paragraph in article_paragraphs:
                        current_article_text += (article_paragraph.get_text(strip=True) + ' ')
                    term_index = term
                    matched = match_keywords(current_article_text, term_index)
                    if len(matched) != 0:
                        matched_articles[link] = current_article_text
                        matched_articles_keywords[link] = matched
                        matched_article_titles[link] = title
                        matched_article_authors[link] = author
                        matched_article_publish_date[link] = publish_date
                else:
                    print(f"link: {link} did not work. (status code: {response.status_code})")
            
            i = 0
            at_least_one_article = False
            for link, article_text in matched_articles.items():
                if i < article_limit:
                    if len(article_text.lower().split()) < word_limit:
                        word_count = len(article_text.lower().split())
                        print(f"Title: {matched_article_titles[link]}\nAuthor: {matched_article_authors[link]}")
                        print(f"Publish Date: {matched_article_publish_date[link]}")
                        print(f"Matched keywords: {matched_articles_keywords[link]}")
                        print(f"Matched Link: {link}\n")
                        print(f"Article Length:{word_count}\nMatched Article:\n{article_text}\n")
                        i += 1
                        at_least_one_article = True
                    else: 
                        #print(f"Article exceeds limit: {word_count} words. Read full article at {link}\n")
                        pass
                else: 
                    print(f"Limit reached, {article_limit} articles displayed.\n")
                    break
            if not at_least_one_article:
                print(f"No articles found within {word_limit} word limit.\n")
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")

def search_tech_radar(website_url=website_urls[7], search_terms=search_terms, article_limit=1, word_limit=500):
    print("Searching on website: https://www.techradar.com")
    for term in range(len(search_terms)):
        params = {"searchTerm": search_terms[term],
                  "articleType": "all",
                  "sortBy": "publishedDate"}

        response = requests.get(website_url, params=params, headers=headers)
        print("Search URL:", response.url)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # get all the articles in one container
            results_container = soup.find("div", class_="listingResults")
            if results_container is None: 
                print(f"No results for {search_terms[term]}")
                continue

            # separate the individual articles from the container and store in new container
            articles = results_container.find_all("div", class_="listingResult")
            if not articles: 
                print(f"No results for {search_terms[term]}\n")
                continue
            matched_articles = {}
            matched_articles_keywords = {}
            matched_article_titles = {}
            matched_article_authors = {}
            matched_article_publish_date = {}
            print("Searching articles and matching keywords...\n")
            for article in articles:  
                # get the link tag <a>
                author = article.find("span", style="white-space:nowrap").get_text(strip=True)
                link = article.find("a", class_="article-link").get("href")
                title = article.find("h3", class_="article-name").get_text(strip=True)
                publish_date = article.find("time", class_="no-wrap relative-date date-with-prefix").get_text(strip=True)
                
                '''print("-", title, "\n")
                print("   Author:", ", ".join(author_names), "\n")
                print("   Link:", "https://www.pcmag.com/"+link, "\n")
                print("   Synopsis:", synopsis, "\n")'''
                

                current_article_text = ""
                response = requests.get(link, headers=headers)
                if response.status_code == 200:
                    opened_article = BeautifulSoup(response.text, "html.parser")
                    article_body = opened_article.find("div", id="article-body")
                    if article_body is None: 
                        print(f"Article is empty at Link: {link}")
                        break
                    article_paragraphs = article_body.find_all("p", class_=False, id=False)
                    for article_paragraph in article_paragraphs:
                        current_article_text += (article_paragraph.get_text(strip=True) + ' ')
                    term_index = term
                    matched = match_keywords(current_article_text, term_index)
                    if len(matched) != 0:
                        matched_articles[link] = current_article_text
                        matched_articles_keywords[link] = matched
                        matched_article_titles[link] = title
                        matched_article_authors[link] = author
                        matched_article_publish_date[link] = publish_date
                else:
                    print(f"link: {link} did not work. (status code: {response.status_code})")
            
            i = 0
            at_least_one_article = False
            for link, article_text in matched_articles.items():
                if i < article_limit:
                    if len(article_text.lower().split()) < word_limit:
                        word_count = len(article_text.lower().split())
                        print(f"Title: {matched_article_titles[link]}\nAuthor: {matched_article_authors[link]}")
                        print(f"Publish Date: {matched_article_publish_date[link]}")
                        print(f"Matched keywords: {matched_articles_keywords[link]}")
                        print(f"Matched Link: {link}\n")
                        print(f"Article Length:{word_count}\nMatched Article:\n{article_text}\n")
                        i += 1
                        at_least_one_article = True
                    else: 
                        #print(f"Article exceeds limit: {word_count} words. Read full article at {link}\n")
                        pass
                else: 
                    print(f"Limit reached, {article_limit} articles displayed.\n")
                    break
            if not at_least_one_article:
                print(f"No articles found within {word_limit} word limit.\n")
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")

search_functions = [search_toms_hardware, 
                    search_pc_mag, 
                    search_the_pc_enthusiast, 
                    search_hothardware, 
                    search_pc_perspective, 
                    search_gamerant, 
                    search_windows_central,
                    search_tech_radar]

'''i = 0
for website_url in website_urls:
    search_functions[i](website_url, search_terms, article_limit=1, word_limit=300)
    i += 1'''
'''search_toms_hardware(website_urls[0], search_terms, article_limit=1, word_limit=2000)
search_pc_mag(website_urls[1], search_terms, article_limit=1, word_limit=2000)
search_the_pc_enthusiast(website_urls[2], search_terms, article_limit=1, word_limit=2000)
search_hothardware(website_urls[3], search_terms, article_limit=1, word_limit=2500)
search_pc_perspective(website_urls[4], search_terms, article_limit=1, word_limit=2000)
search_gamerant(website_urls[5], search_terms, article_limit=1, word_limit=2000)
search_windows_central(website_urls[6], search_terms, article_limit=1, word_limit=2000)
search_tech_radar(website_urls[7], search_terms, article_limit=1, word_limit=2000)'''