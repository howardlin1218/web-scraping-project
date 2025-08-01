from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import sys
import signal
import re

comma_splitter = re.compile(r'\s*,\s*')
now = datetime.now()
d_year = now.year 
d_month = now.month
d_day = now.day
# Import your existing modules
try:
    from automate_email import construct_message, json_dict, send_email, email_dict # Import your email automation
    from test import search_all_sites  # Import your scraping logic
    from database import insert_to_supabase, get_recent_10_articles, populate_fields, search_for_articles, get_all_saved
except ImportError:
    print("Warning: Could not import some modules. Make sure database.py and automate_email.py exist.")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication 

@app.route('/api/email-to-user', methods=['POST'])
def email_to_user():
    try:
        email_html_content = ""
        payload = json.loads(request.data.decode("utf-8"))
        article_ids = payload.get("data")
        email_address = payload.get("email_address")
        for article_id in article_ids:
            email_html_content += email_dict[article_id]
        send_email(email_content_html=email_html_content, email_address="howlin1218@gmail.com", recipient_emails=email_address)
        return jsonify({"status": "success", 
                        "message": "email successfully sent"
                        }), 200
    except Exception as e:
        print(str(e))
        return jsonify({
            'status': 'saving error',
            'message': str(e)
        }), 500
    
@app.route('/api/save-to-database', methods=['POST'])
def save_to_database():
    try:
        payload = request.get_json()
        article_ids = payload.get("data")
        list_of_json_data = [json_dict[article_id] for article_id in article_ids]
        insert_to_supabase(list_of_json_data)
        return jsonify({"status": "success", 
                        "message": "saved successfully to database"
                        }), 200
    except Exception as e:
        print(str(e))
        return jsonify({
            'status': 'saving error',
            'message': str(e)
        }), 500
    
@app.route('/api/search-site', methods=['POST'])
def search_site():
    """Handle site search requests from frontend"""
    try:
        data = request.get_json()
        
        # Extract search parameters
        websites = [int(x) for x in data.get('websites', ["0"])]
        search_terms = comma_splitter.split(data.get('searchTerms', ''))
        limit = data.get('limit')
        day = data.get('day')
        month = data.get('month')
        year = data.get('year')
        keywords = data.get('keywords', [])
        
        if keywords != "":
            keywords = keywords.strip().replace(" ", "").split(",")
        else: 
            keywords = []
        
        # Log the search request
        print(f"Site search request: {search_terms} on {len(websites)} websites: {websites}, limit:{limit}")
        results_list = search_all_sites(search_terms=search_terms, article_limit=limit, filter_year=year, filter_month=month, filter_day=day, sites_to_search=websites, keywords=keywords)
                
        return_str = construct_message(results_list=results_list)
        #save_to_file(return_str)
        return jsonify({"status": "success", 
                        "message": "returning json",
                        "html": return_str
                        }), 200
        
    except Exception as e:
        print(str(e))
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/recent-saves', methods=['GET'])
def get_recent_articles():
    try:
        response = get_recent_10_articles()
        for dict in response: 
            input_tag = f"<input value='{dict['url']}' style='width: auto; transform: scale(1.5);' type='checkbox' name='articleCheckBox' />\n"
            for_email_html = dict['content'].replace(input_tag, "")

            email_dict[dict['url']] = for_email_html

        return jsonify({"status": "success", 
                        "message": "got 10 most recent articles saved",
                        "html": "".join(article.get("content", "") for article in response)
                        }), 200
    except Exception as e:
        print(str(e))
        return jsonify({
            'status': 'error fetching from database',
            'message': str(e)
        }), 500

@app.route('/api/all-saved', methods=['GET'])
def get_all_saved_articles():
    try:
        response = get_all_saved()
        for dict in response: 
            input_tag = f"<input value='{dict['url']}' style='width: auto; transform: scale(1.5);' type='checkbox' name='articleCheckBox' />\n"
            for_email_html = dict['content'].replace(input_tag, "")

            email_dict[dict['url']] = for_email_html

        return jsonify({"status": "success", 
                        "message": "got all saved articles",
                        "html": "".join(article.get("content", "") for article in response)
                        }), 200
    except Exception as e:
        print(str(e))
        return jsonify({
            'status': 'error fetching from database',
            'message': str(e)
        }), 500
    
@app.route('/api/search-database', methods=['POST'])
def search_database():
    """Handle database search requests from frontend"""
    try:
        data = request.get_json()
        
        # Extract search parameters
        websites = data.get('websites') # required
        search_terms = comma_splitter.split(data.get('searchTerms', ''))
        limit = data.get('limit') # optional
        keywords = data.get('keywords') # optional
        urls = data.get('urls') # optional
        day = data.get('day') # optional
        month = data.get('month') # optional
        year = data.get('year') # optional

        if keywords != "":
            keywords = keywords.strip().replace(" ", "").split(",")
        else: 
            keywords = []

        if urls != "":
            urls = urls.strip().replace(" ", "").split(",")
        else: 
            urls = []
        
        # print("websites: ", websites)
        # print("search terms: ", search_terms)
        # print("limit: ", limit)
        # print("day: ", day)
        # print("month: ", month)
        # print("year: ", year)
        # print("keywords: ", keywords)
        # print("urls: ", urls)

        # Log the search request
        print(f"Database search request: matching titles with {search_terms} with limit of {limit}")
        response = search_for_articles(websites, search_terms, limit, keywords, urls, day, month, year)
        # Here you can integrate with your existing database functions
        return jsonify({"status": "success", 
                        "message": "returning json",
                        "html": "".join(article.get("content", "") for article in response)
                        }), 200
        
    except Exception as e:
        print(str(e))
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

def graceful_shutdown(sig, frame):
    insert_to_supabase(list(json_dict.values()))
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)  # Ctrl+C
signal.signal(signal.SIGTERM, graceful_shutdown)

if __name__ == '__main__':
    populate_fields()
    app.run(debug=True, host='127.0.0.1', port=5000)