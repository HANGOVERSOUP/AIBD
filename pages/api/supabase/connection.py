from supabase import create_client, Client
import pandas as pd


class supa():
    
    def __init__(self):
        url = "https://mhljewhquduzewpumlwp.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1obGpld2hxdWR1emV3cHVtbHdwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5OTIzMjU0MywiZXhwIjoyMDE0ODA4NTQzfQ.RelWd6-iVKpvjOhIq5XwWDGZeBu_8z3ewnbONaWPbdI"

        self.supabase: Client = create_client(url, key)
# %%

    def update_table(self, TABLE_NAME,data_to_add):
        data, _ = self.supabase.table(TABLE_NAME).insert(data_to_add).execute()
        return data

    def read_all_table(self, TABLE_NAME):
        data, _ = self.supabase.table(TABLE_NAME).select("*").execute()
        return data
    
    