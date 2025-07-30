from automate_email import send_email, construct_message
from test import search_all_sites

from datetime import datetime

now = datetime.now()
year = now.year 
month = now.month
day = now.day

email_list = []
searches = []
a_limit = 1
w_limit = 2500
f_year = year
f_month = month 
f_day = day
sites = []
keywords = []

def send_emails():
    response_html = search_all_sites(search_terms=searches, article_limit=a_limit, word_limit=w_limit, filter_year=f_year, filter_month=f_month, filter_day=f_day, sites_to_search=sites, keywords=keywords)
    
    return_string = construct_message(results_list=response_html)

    send_email(email_content_html=return_string, recipient_emails=email_list)