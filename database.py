from supabase import create_client, Client
import os 
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for backend

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_to_supabase(articles): 
    # Insert all articles into Supabase
    try:
        supabase.table("articles").upsert(articles, on_conflict="url").execute()
    except Exception as e:
        print("Unexpected error inserting into Supabase:", e)

def save_single_article(article):
    try:
        supabase.table("articles").upsert([article], on_conflict="url").execute()
    except Exception as e:
        print("Unexpected error inserting into Supabase:", e)