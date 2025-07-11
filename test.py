import requests 
from bs4 import BeautifulSoup

from collections import defaultdict
import re

from datetime import datetime

now = datetime.now()
year = now.year 
month = now.month
day = now.day

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
    "Desktop", 
    "Gaming Desktop",
    "Pro Desktop"
]

key_words_gaming = [
    "MSI",
    "iBUYPOWER",
    "ASUS", 
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

months = {
    "january" : 1, 
    "jan": 1,
    "february": 2, 
    "feb": 2,
    "march": 3,
    "mar": 3, 
    "april": 4,
    "apr": 4, 
    "may": 5, 
    "june": 6,
    "jun": 6, 
    "july": 7,
    "jul": 7, 
    "august": 8,
    "aug": 8, 
    "september": 9,
    "sep": 9, 
    "october": 10,
    "oct": 10, 
    "november": 11,
    "nov": 11, 
    "december": 12,
    "dec": 12
}

headers = {"User-Agent": "Chrome/114.0.0.0 Safari/537.36"}

pattern = ""
def keywords_pattern(keywords):
    if len(keywords) == 0:
        return ""
    pattern = r'\b(' + '|'.join(re.escape(k) for k in keywords) + r')\b'
    return pattern

#pattern = [pattern_gaming, pattern_pro]

# parse dates
splitter = re.compile(r"[ /,]+")

def match_keywords(article_text, term_index):
    if pattern == "":
        return ["no keywords"]
    matches = re.findall(pattern, article_text, flags=re.IGNORECASE)
    if matches: 
        return list(set(match.lower() for match in matches))
    return []

def search_toms_hardware(website_url=website_urls[0], search_terms=search_terms, article_limit=1, word_limit=500, filter_year=year, filter_month=month, filter_day=day): 
    matched_article_metadata = defaultdict(list)
    for term in range(len(search_terms)):
        i = 0
        params = {"searchTerm": search_terms[term],
                  "articleType": "all",
                  "sortBy": "publishedDate"
                  }

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

            at_least_one_article = False
            for article in articles:
                if i < article_limit:
                    current_article_text = ""
                    author = article.find("span", style ="white-space:nowrap").get_text(strip=True)
                    a_tag = article.find("a", class_="article-link")
                    link = a_tag.get("href")
                    title = a_tag.get("aria-label")
                    publish_date = article.find("time", class_="date-with-prefix").get_text(strip=True)
                    parsed_date = splitter.split(publish_date)
                    if int("20"+parsed_date[-1]) < filter_year or months[parsed_date[1].lower()] < filter_month or int(parsed_date[0]) < filter_day:
                        continue

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
                            matched_article_metadata[link] = [current_article_text, 
                                                              matched, 
                                                              title, 
                                                              author, 
                                                              publish_date]
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
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")
            pass
    return matched_article_metadata
    
    # search through each article on the page and match keywords (DONE)
    # if an article matches keywords (desktop, pro desktop, gaming desktop, MSI, ASUS, Cyberpower, etc.), summarize using LLM api (LLM to be chosen) (DONE)
    # after summarizing, do sentiment analysis on the article and provide bullet points of positive, neutral, and negative 
    # figure out how to send these as notifications to emails, and how to save to database for future reference 
    # allow user lookup in the database 

def search_pc_mag(website_url=website_urls[1], search_terms=search_terms, article_limit=1, word_limit=500, filter_year=year, filter_month=month, filter_day=day):
    matched_article_metadata = {}
    for term in range(len(search_terms)):
        i = 0
        params = {"query": search_terms[term]}

        response = requests.get(website_url, params=params, headers=headers)
        #print("Search URL:", response.url)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # get all the articles in one container
            results_container = soup.find("div", class_="flex flex-col gap-4")
            if results_container is None: 
                print(f"PC Mag No results for {search_terms[term]}\n")
                continue

            # separate the individual articles from the container and store in new container
            articles = results_container.find_all("div", class_="dark:border-gray-600")
            if not articles: 
                print(f"PC Mag No results for {search_terms[term]}\n")
                continue

           #print("Searching articles and matching keywords...\n")
            at_least_one_article = False
            for article in articles:  
                if i < article_limit:
                    # get the link tag <a>
                    a_tag = article.find("a", attrs={"x-track-ga-click": True})
                    link = "https://www.pcmag.com/"+a_tag.get("href")
                    title = a_tag.get_text(strip=True)
                    publish_date = article.find("span", attrs={"data-content-published-date": True}).get_text(strip=True)
                    parsed_date = splitter.split(publish_date)
                    if parsed_date[-1] != 'ago': 
                        if int(parsed_date[-1]) < filter_year or int(parsed_date[0]) < filter_month or int(parsed_date[1]) < filter_day:
                            continue
                    # synopsis = article.find("p", class_="line-clamp-2").get_text(strip=True)
                    author = article.find_all("a",  attrs={"data-element": "author-name"})
                    author_names = []
                    for a in author: 
                        author_names.append(a.get_text(strip=True))
                    
                    if len(author_names) > 1:
                        author = ", ".join(author_names)
                    elif len(author_names) == 1:
                        author = "".join(author_names)

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
                        if len(current_article_text.lower().split()) > word_limit:
                            continue
                        term_index = term
                        matched = match_keywords(current_article_text, term_index)
                        if len(matched) != 0:
                            matched_article_metadata[link] = [current_article_text, 
                                                              matched, 
                                                              title,
                                                              author,
                                                              publish_date]
                            i += 1
                            at_least_one_article = True
                    else:
                        print(f"link: {link} did not work. (status code: {response.status_code})")
                else:
                    break
            if not at_least_one_article:
                #print(f"No articles found within {word_limit} word limit.\n")
                pass
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")
            pass
    return matched_article_metadata

def search_the_pc_enthusiast(website_url=website_urls[2], search_terms=search_terms, article_limit=1, word_limit=500, filter_year=year, filter_month=month, filter_day=day):
    matched_article_metadata = {}
    for term in range(len(search_terms)):
        i = 0
        params = {"s": search_terms[term]}

        response = requests.get(website_url, params=params, headers=headers)
        #print("Search URL:", response.url)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # get all the articles in one container
            results_container = soup.find("main", class_="site-main")
            no_content = results_container.find("div", class_="no-results")
            if no_content is not None: 
                print(f"PC E No results for {search_terms[term]}\n")
                continue

            # separate the individual articles from the container and store in new container
            articles = results_container.find_all("div", class_="inside-article")
            if not articles: 
                print(f"PC E No results for {search_terms[term]}\n")
                continue
            
            at_least_one_article = False
            for article in articles:
                if i < article_limit:  
                    # get the link tag <a>
                    author = article.find("span", class_="author-name").get_text(strip=True)
                    a_tag = article.find("a", rel="bookmark")
                    link = a_tag.get("href")
                    title = a_tag.get_text(strip=True)
                    publish_date = article.find("time", class_="published").get_text(strip=True)
                    parsed_date = splitter.split(publish_date)
                    if int(parsed_date[-1]) < filter_year or months[parsed_date[0].lower()] < filter_month or int(parsed_date[1]) < filter_day:
                        continue
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
                        if len(current_article_text.lower().split()) > word_limit:
                            continue
                        term_index = term
                        matched = match_keywords(current_article_text, term_index)
                        if len(matched) != 0:
                            matched_article_metadata[link] = [current_article_text,
                                                        matched,
                                                        title,
                                                        author,
                                                        publish_date]
                            i += 1
                            at_least_one_article = True
                    else:
                        print(f"link: {link} did not work. (status code: {response.status_code})")
                else:
                    break
            if not at_least_one_article:
                #print(f"No articles found within {word_limit} word limit.\n")
                pass
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")
    return matched_article_metadata

def search_hothardware(website_url=website_urls[3], search_terms=search_terms, article_limit=1, word_limit=500, filter_year=year, filter_month=month, filter_day=day):
    matched_article_metadata = {}
    for term in range(len(search_terms)):
        i = 0
        params = {"a": "all",
                  "s": search_terms[term]}

        response = requests.get(website_url, params=params, headers=headers)
        #print("Search URL:", response.url)
    
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
            #print("Searching articles and matching keywords...\n")
            at_least_one_article = False
            for article in articles:  
                if i < article_limit:
                    author = article.find("b", class_=False, id=False).get_text(strip=True)
                    title_link_tag = article.find("a", class_="black p-name u-url")
                    link = "https://hothardware.com" + title_link_tag.get("href")
                    title = title_link_tag.get_text(strip=True)
                
                    publish_date = article.find("div", class_="cli-byline").get_text(strip=True).split('-')[-1].strip()
                    parsed_date = splitter.split(publish_date)
                    if int(parsed_date[-1]) < filter_year or months[parsed_date[1].lower()] < filter_month or int(parsed_date[2]) < filter_day:
                        continue
                    current_article_text = ""
                    response = requests.get(link, headers=headers)
                    if response.status_code == 200:
                        opened_article = BeautifulSoup(response.text, "html.parser")
                        current_article_text = opened_article.find("div", class_="cn-body e-content").get_text(strip=True)
                        if current_article_text is None: 
                            print(f"Article is empty at Link: {link}")
                            break
                        if len(current_article_text.lower().split()) > word_limit:
                            continue
                        term_index = term
                        matched = match_keywords(current_article_text, term_index)
                        if len(matched) != 0:
                            matched_article_metadata[link] = [current_article_text, 
                                                        matched, 
                                                        title, 
                                                        author, 
                                                        publish_date]
                            i += 1
                            at_least_one_article = True
                    else:
                        print(f"link: {link} did not work. (status code: {response.status_code})")
                else:
                    break
            if not at_least_one_article:
                #print(f"No articles found within {word_limit} word limit.\n")
                pass
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")
    return matched_article_metadata

def search_pc_perspective(website_url=website_urls[4], search_terms=search_terms, article_limit=1, word_limit = 500, filter_year=year, filter_month=month, filter_day=day):
    matched_article_metadata = {}
    for term in range(len(search_terms)):
        i = 0
        params = {"s": search_terms[term]}

        response = requests.get(website_url, params=params, headers=headers)
        #print("Search URL:", response.url)
    
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
            #print("Searching articles and matching keywords...\n")
            at_least_one_article = False
            for article in articles:  
                if i < article_limit:
                    # get the link tag <a>
                    author = article.find("a", rel="author").get_text(strip=True)
                    a_tag = article.find("a", class_="et-accent-color")
                    link = a_tag.get("href")
                    title = a_tag.get_text(strip=True)
                    publish_date = article.find("span", class_="updated").get_text(strip=True)
                    parsed_date = splitter.split(publish_date)
                    if int(parsed_date[-1]) < filter_year or months[parsed_date[0].lower()] < filter_month or int(parsed_date[1]) < filter_day:
                        continue
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
                        if len(current_article_text.lower().split()) > word_limit:
                            continue
                        term_index = term
                        matched = match_keywords(current_article_text, term_index)
                        if len(matched) != 0:
                            matched_article_metadata[link] = [current_article_text, 
                                                        matched, 
                                                        title, 
                                                        author, 
                                                        publish_date]
                            i += 1
                            at_least_one_article = True
                    else:
                        print(f"link: {link} did not work. (status code: {response.status_code})")
                else:
                    break
            if not at_least_one_article:
                #print(f"No articles found within {word_limit} word limit.\n")
                pass
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")
    return matched_article_metadata

def search_gamerant(website_url=website_urls[5], search_terms=search_terms, article_limit=1, word_limit=500, filter_year=year, filter_month=month, filter_day=day):
    matched_article_metadata = {}
    for term in range(len(search_terms)):
        i = 0
        params = {"q": search_terms[term]}

        response = requests.get(website_url, params=params, headers=headers)
        #print("Search URL:", response.url)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # get all the articles in one container
            results_container = soup.find("section", class_="listing-content")
            if results_container is None: 
                print(f"GR Results No results for {search_terms[term]}")
                continue

            # separate the individual articles from the container and store in new container
            articles = results_container.find_all("div", class_="article")
            if not articles: 
                print(f"GR Articles No results for {search_terms[term]}\n")
                continue
            
            at_least_one_article = False
            for article in articles:  
                if i < article_limit:
                    # get the link tag <a>
                    author = article.find("a", rel="author").get_text(strip=True)
                    a_tag = article.find("a", class_=False, id=False)
                    link = "https://gamerant.com" + a_tag.get("href")
                    title = a_tag.get_text(strip=True)
                    publish_date = article.find("time", class_="display-card-date").get_text(strip=True)
                    parsed_date = splitter.split(publish_date)
                    if int(parsed_date[-1]) < filter_year or months[parsed_date[0].lower()] < filter_month or int(parsed_date[1]) < filter_day:
                        continue
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
                        if len(current_article_text.lower().split()) > word_limit:
                            continue
                        term_index = term
                        matched = match_keywords(current_article_text, term_index)
                        if len(matched) != 0:
                            matched_article_metadata[link] = [current_article_text, 
                                                        matched, 
                                                        title, 
                                                        author, 
                                                        publish_date]
                            i += 1
                            at_least_one_article = True
                    else:
                        print(f"link: {link} did not work. (status code: {response.status_code})")
                else:
                    break
            if not at_least_one_article:
                #print(f"No articles found within {word_limit} word limit.\n")
                pass
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")
    return matched_article_metadata

def search_windows_central(website_url=website_urls[6], search_terms=search_terms, article_limit=1, word_limit=500, filter_year=year, filter_month=month, filter_day=day):
    matched_article_metadata = {}
    for term in range(len(search_terms)):
        i = 0
        params = {"searchTerm": search_terms[term],
                  "dateRange": "DATE_RANGE_12_MONTHS"}

        response = requests.get(website_url, params=params, headers=headers)
        #print("Search URL:", response.url)
    
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
            
            at_least_one_article = False
            for article in articles:  
                if i < article_limit:
                # get the link tag <a>
                    author = article.find("span", style="white-space:nowrap").get_text(strip=True)
                    link = article.find("a", class_="article-link").get("href")
                    title = article.find("h3", class_="article-name").get_text(strip=True)
                    publish_date = article.find("time", class_="no-wrap relative-date date-with-prefix").get_text(strip=True)
                    parsed_date = splitter.split(publish_date)
                    if int("20"+parsed_date[-1]) < filter_year or months[parsed_date[1].lower()] < filter_month or int(parsed_date[0]) < filter_day:
                        continue
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
                        if len(current_article_text.lower().split()) > word_limit:
                            continue
                        term_index = term
                        matched = match_keywords(current_article_text, term_index)
                        if len(matched) != 0:
                            matched_article_metadata[link] = [current_article_text, 
                                                        matched, 
                                                        title, 
                                                        author, 
                                                        publish_date]
                            i += 1
                            at_least_one_article = True
                    else:
                        print(f"link: {link} did not work. (status code: {response.status_code})")
                else:
                    break
            if not at_least_one_article:
                #print(f"No articles found within {word_limit} word limit.\n")
                pass
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")
    return matched_article_metadata

def search_tech_radar(website_url=website_urls[7], search_terms=search_terms, article_limit=1, word_limit=500, filter_year=year, filter_month=month, filter_day=day):
    matched_article_metadata = {}
    for term in range(len(search_terms)):
        i = 0
        params = {"searchTerm": search_terms[term],
                  "articleType": "all",
                  "sortBy": "publishedDate"}

        response = requests.get(website_url, params=params, headers=headers)
        #print("Search URL:", response.url)
    
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

            at_least_one_article = False
            for article in articles:  
                if i < article_limit:
                    # get the link tag <a>
                    author = article.find("span", style="white-space:nowrap").get_text(strip=True)
                    link = article.find("a", class_="article-link").get("href")
                    title = article.find("h3", class_="article-name").get_text(strip=True)
                    publish_date = article.find("time", class_="no-wrap relative-date date-with-prefix").get_text(strip=True)
                    parsed_date = splitter.split(publish_date)
                    if int("20"+parsed_date[-1]) < filter_year or months[parsed_date[1].lower()] < filter_month or int(parsed_date[0]) < filter_day:
                        continue
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
                        if len(current_article_text.lower().split()) > word_limit:
                            continue
                        term_index = term
                        matched = match_keywords(current_article_text, term_index)
                        if len(matched) != 0:
                            matched_article_metadata[link] = [current_article_text, 
                                                        matched, 
                                                        title, 
                                                        author, 
                                                        publish_date]
                            i += 1
                            at_least_one_article = True
                    else:
                        print(f"link: {link} did not work. (status code: {response.status_code})")
                else:
                    break
            if not at_least_one_article:
                #print(f"No articles found within {word_limit} word limit.\n")
                pass
        else:
            print(f"Failed to fetch results for {search_terms[term]} (status code: {response.status_code})")
    return matched_article_metadata

search_functions = [search_toms_hardware, 
                    search_pc_mag, 
                    search_the_pc_enthusiast, 
                    search_hothardware, 
                    search_pc_perspective, 
                    search_gamerant, 
                    search_windows_central,
                    search_tech_radar]

def search_all_sites(website_urls=website_urls, search_terms=search_terms, article_limit=1, word_limit=2500, filter_year=year, filter_month=month, filter_day=day, sites_to_search=[0], keywords=[]):
    global pattern 
    pattern = keywords_pattern(keywords)
    i = 0
    return_list = {}
    for website_url in website_urls:
        if i in sites_to_search:
            return_list[website_url] = search_functions[i](website_url, search_terms, article_limit, word_limit, filter_year, filter_month, filter_day)
        i += 1
        # site_data = search_functions[i](website_url, search_terms, article_limit, word_limit) # returns a dict, see below for structure
        # site_data = {"article link": ["article text", ["article keywords"], "article title", "article author(s)", "article publish date"], 
        #              "article link": ["article text", ["article keywords"], "article title", "article author(s)", "article publish date"], 
        #               ...more links...}
        # result_list = {"website link":{"article link": ["article text", ["article keywords"], "article title", "article author(s)", "article publish date"],
        #                           "article link": ["article text", ["article keywords"], "article title", "article author(s)", "article publish date"],
        #                            ...more links...}, 
        #                "website link": {....}, 
        #                ...}
        # site_data = dict[article link] = [list]
        # result_list = dict[website link] = (dict[article link] = [list])
    return return_list