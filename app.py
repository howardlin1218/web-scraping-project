from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import sys
import os
now = datetime.now()
d_year = now.year 
d_month = now.month
d_day = now.day
# Import your existing modules
try:
    from automate_email import construct_message, json_dict, send_email, email_dict, save_to_file # Import your email automation
    from test import search_all_sites  # Import your scraping logic
    from database import insert_to_supabase
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
        print(payload, article_ids, email_address)
        for article_id in article_ids:
            email_html_content += email_dict[article_id]
        send_email(email_html_content, email_address)
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
        list_of_json_data = []
        payload = request.get_json()
        article_ids = payload.get("data")
        for article_id in article_ids:
            list_of_json_data.append(json_dict[article_id])
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
        search_terms = [data.get('searchTerms', '')]
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

@app.route('/api/search-database', methods=['POST'])
def search_database():
    """Handle database search requests from frontend"""
    try:
        data = request.get_json()
        
        # Extract search parameters
        websites = data.get('websites', [])
        search_terms = data.get('searchTerms', '')
        limit = data.get('limit', 5)
        day = data.get('day', 0)
        month = data.get('month', '')
        year = data.get('year', 0)
        keywords = data.get('keywords', '')
        
        # Log the search request
        print(f"Database search request: {search_terms} on {len(websites)} websites")
        
        # Here you can integrate with your existing database functions
        results = {
            'status': 'success',
            'message': f'Searching database for "{search_terms}" on {len(websites)} websites with limit {limit}',
            'data': {
                'websites': websites,
                'search_terms': search_terms,
                'limit': limit,
                'date': {'day': day, 'month': month, 'year': year},
                'keywords': keywords.split(',') if keywords else [],
                'timestamp': datetime.now().isoformat()
            },
            'articles': []  # This would contain your database results
        }
        
        # TODO: Add your actual database search logic here
        # results['articles'] = search_articles_in_database(search_terms, limit, ...)
        
        return jsonify(results)
        
    except Exception as e:
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

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)