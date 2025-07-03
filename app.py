from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import sys
import os

# Import your existing modules
try:
    import automate_email # Import your email automation
    import test  # Import your scraping logic
except ImportError:
    print("Warning: Could not import some modules. Make sure database.py and automate_email.py exist.")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route('/api/search-site', methods=['POST'])
def search_site():
    """Handle site search requests from frontend"""
    try:
        data = request.get_json()
        
        # Extract search parameters
        websites = [int(x) for x in data.get('websites', ["0"])]
        search_terms = data.get('searchTerms', '')
        limit = data.get('limit', 5)
        day = data.get('day', 15)
        month = data.get('month', "June")
        year = data.get('year', 2025)
        keywords = data.get('keywords', '').replace(" ", "").split(",")
        # Log the search request
        print(f"Site search request: {search_terms} on {len(websites)} websites: {websites}")
    
        results_list = test.search_all_sites(search_terms=search_terms, article_limit=limit, filter_year=year, filter_month=month, filter_day=day, sites_to_search=websites, keywords=keywords)
        return jsonify({"html": automate_email.construct_message(results_list=results_list)})
        
    except Exception as e:
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