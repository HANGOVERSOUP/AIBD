# %%
import psycopg2
import pandas as pd

class supaDB():
    
    def __init__(self):
        
        self.conn  = psycopg2.connect(host='db.zyqtytdhyppqhrherzni.supabase.co', 
                            dbname='postgres',
                            user='postgres',
                            password='Aibd8520*%@)',
                            port=5432)


        self.cursor= self.conn.cursor()




        
    def query2df (self, query):
        df = pd.read_sql_query(query, self.conn)
        return df
    
    def query_call (self, query):
        self.cursor.execute(query)
        self.conn.commit()
        
    
    def __del__(self):
        self.conn.close()