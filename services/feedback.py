"""
Feedback Service using Supabase
"""
import pandas as pd
from services.db import supabase

def init_feedback_db():
    """Initialize the feedback database table."""
    # In Supabase, tables are created via SQL Editor or Migrations.
    # This function is kept for compatibility but does nothing.
    pass

def add_feedback(name, email, category, content):
    """Add a new feedback entry."""
    if not supabase:
        print("Supabase client not initialized.")
        return

    try:
        data = {
            "name": name,
            "email": email,
            "category": category,
            "content": content,
            "status": "New"
        }
        supabase.table("feedback").insert(data).execute()
    except Exception as e:
        print(f"Error adding feedback: {e}")

def get_all_feedback():
    """Retrieve all feedback entries."""
    if not supabase:
        return pd.DataFrame()

    try:
        response = supabase.table("feedback").select("*").order("id", desc=True).execute()
        data = response.data
        if data:
            df = pd.DataFrame(data)
            # Map created_at to timestamp for compatibility
            if 'created_at' in df.columns:
                df['timestamp'] = df['created_at']
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error retrieving feedback: {e}")
        return pd.DataFrame()
