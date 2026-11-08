import os

from dotenv import load_dotenv
from supabase import create_client


def get_supabase_client():
    """Create a Supabase client using environment settings."""
    load_dotenv()

    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]

    return create_client(url, key)

