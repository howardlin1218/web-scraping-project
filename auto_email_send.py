from automate_email import send_email, construct_message, email_dict
from test import search_all_sites

from datetime import datetime

now = datetime.now()
year = now.year 
month = now.month
day = now.day

email_list = ['howlin1218@gmail.com']
email_address = "howlin1218@gmail.com"
searches = ['gaming desktop', 'pro desktop']
a_limit = 1
w_limit = 2500
f_year = year
f_month = 5 
f_day = 1
sites = [0]
keywords = ["MSI",
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
    "Razer","BRIX", 
    "Minisforum", 
    "Beelink", 
    "Zotac Zbox", 
    "Apple Mac Mini", 
    "HP Elite Mini", 
    "Cubi", 
    "Pro", 
    "Microsoft Surface",
    "Apple", 
    "Macbook"]

def send_emails():
    response_html = search_all_sites(search_terms=searches, article_limit=a_limit, word_limit=w_limit, filter_year=f_year, filter_month=f_month, filter_day=f_day, sites_to_search=sites, keywords=keywords)
    
    construct_message(results_list=response_html)
    email_html = ""

    for article in email_dict: 
        email_html += email_dict[article]
    send_email(email_content_html=email_html, email_address=email_address, recipient_emails=email_list)

send_emails()