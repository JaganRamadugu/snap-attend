import streamlit as st
import os
from supabase import create_client, Client

def get_secret(key):
    # Try Streamlit secrets first
    try:
        return st.secrets[key]
    except Exception:
        pass
    
    # Try environment variables
    val = os.environ.get(key)
    if val:
        return val
        
    # Try reading from .env file manually
    env_path = "c:/Users/rjaga/OneDrive/Documents/PROJECTS/ATTENDX AI/.env"
    if os.path.exists(env_path):
        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() == key:
                            return v.strip()
        except Exception:
            pass
    return None

supabase_url = get_secret("SUPABASE_URL")
supabase_key = get_secret("SUPABASE_PUBLISHABLE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL or SUPABASE_PUBLISHABLE_KEY not found in Streamlit secrets, environment, or .env file.")

supabase: Client = create_client(supabase_url, supabase_key)
