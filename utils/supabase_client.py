import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()  # para mabasa yung .env file

url: str = os.getenv("SUPABASE_PROJECT_URL")
anon_key: str = os.getenv("SUPABASE_ANON_KEY")
service_key: str = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(url, service_key)  # use service_key for backend ops
