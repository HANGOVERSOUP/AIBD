# %%
from db_connection import supaDB

db = supaDB()

p_name = '2302019_A_(2023-11-03)'
check_query = f'''SELECT project_id FROM project Where project_name = '{p_name}' '''
p_id = db.query2df(check_query).values[0][0]
print(p_id)
p_id = 'c25369f5-48fc-4f48-b6f7-c7f2b2124cee'
query = f"""select get_max_version_data 
('{p_id}');"""
df = db.query2df(query)
print(df.columns)
df = df.set_index("id")

dict_Val = df.to_json(orient= 'index', force_ascii= False)
# %%
import psycopg2
import pandas as pd




conn  = psycopg2.connect(host='db.mhljewhquduzewpumlwp.supabase.co', 
                            dbname='postgres',
                            user='postgres',
                            password='Aibd8520*%@)',
                            port=5432)

query = f"""select  get_max_version_data
('{p_id}');"""


df = pd.read_sql_query(query, conn)
# %%
conn.close()
# %%
p_id = 'c25369f5-48fc-4f48-b6f7-c7f2b2124cee'
query = f"""SELECT
  *
FROM
  get_max_version_data ('c25369f5-48fc-4f48-b6f7-c7f2b2124cee');
;"""

# query = '''SELECT * FROM raw_data'''

cur = conn.cursor()
cur.execute(query)
columns = [desc[0] for desc in cur.description]
data = cur.fetchall()
df = pd.read_sql_query(query, conn)
# df = pd.DataFrame(data, columns=columns)# %%

# %%
query = f"""SELECT
  *
FROM
  result_data ;
;"""

df2 = pd.read_sql_query(query, conn)
# %%
        # project_list, _  = supabase.table('project').select("*").execute()

        # project_list = project_list[1]
        # project_id = project_list[0]['project_id']
        # # response = supabase.table('columns').select('name, teams(name)').execute()

        # response , _ = supabase.table('columns').select("*").eq("project_id",project_id).execute()
        # q_df = pd.DataFrame(response[1])
        # q_df_input = q_df[['q_id','question_code','question_text']]
        # q_df_input.columns = ['QUESTION_KEY','SURVEY_QUESTION_CD', 'SURVEY_QUESTION_TXT']
from fastapi import APIRouter,  File, UploadFile , Form
import pandas as pd
import json
import io
from typing import Annotated
import os
from fastapi.responses import FileResponse
import requests
from itertools import tee
from supabase import create_client, Client
from db_connection import supaDB
from matplotlib import colors as mcolors
from typing import Optional
    
db = supaDB()
p_name = 'koreanaaaaaaa'
model = 'kri-2-3-brand-model'
data_query = f'''SELECT pm.pq_id, question_code, question_text, value, idkey FROM project_meta as pm
                left join raw_data as rd
                ON pm.pq_id = rd.pq_id
                WHERE project_name = '{p_name}'
'''
df = db.query2df(data_query)
print(df)
q_df_input = df[['pq_id','question_code','question_text']]
q_dict = df.set_index('pq_id')['question_code'].to_dict()
q_df_input.columns = ['QUESTION_KEY','SURVEY_QUESTION_CD', 'SURVEY_QUESTION_TXT']
q_df_input = q_df_input.drop_duplicates()
a_df = df.pivot(columns = "question_code", index = "idkey", values = "value")
a_df = a_df.rename(columns = q_dict).reset_index()
a_df = a_df.rename(columns = {"idkey":"IDKEY"})

# q_dict = q_df.set_index('q_id')['question_code'].to_dict()
# response , _ = supabase.table('raw_data').select('*').execute()
# temp = response[1]
# temp = pd.DataFrame(temp)

# a_df =  temp.pivot(columns = "q_id", index = "idkey", values = "value")
# a_df = a_df.rename(columns = q_dict).reset_index()
# a_df = a_df.rename(columns = {"idkey":"IDKEY"})

q_df_input.to_csv('question.csv',index = False)
a_df.to_csv('answer.csv',index = False)

endpoint = "http://kri.twindoc.ai/kri-api-test-server-1/api"

question_path = 'question.csv'
response_path = 'answer.csv'

cls_model_name = 'kri-2-3-brand-model'
cls_model_version = '1'
snt_model_name = 'kri-1-1-emotion-model'
snt_model_version = '1'
emb_model_name = 'ko-sbert-sts'
emb_model_version = '1'


files = {
    'question': open(question_path, 'rb'),
    'response': open(response_path, 'rb'),
    'cls_model_name': (None, cls_model_name),
    'cls_model_version': (None, cls_model_version),
    'snt_model_name': (None, snt_model_name),
    'snt_model_version': (None, snt_model_version),
    'emb_model_name': (None, emb_model_name),
    'emb_model_version': (None, emb_model_version),
}

response = requests.post(f'{endpoint}/predict', files=files)
response_json = response.json()
# filename = response_json["result"]['response_filename']
# filename = filename.split(".")[0]
# format = "csv"
# url = "http://43.202.119.16:8000/download-csv"
# params = {"file_name": "answer", "format": format}
# response = requests.get(url, params=params)
# # directory = nas_path + '/result_data/'
# if response.status_code == 200:
#     # Get the file name from the response headers
#     content_disposition = response.headers.get("Content-Disposition")
#     if content_disposition:
#         filename_from_header = content_disposition.split("filename=")[1]
#     else:
#         filename_from_header = filename + ".csv"



#     file_like_object = io.BytesIO(response.content)
#     actual_data = pd.read_csv(file_like_object)
    
    
# url = "http://43.202.119.16:8000/download-frame"
# params = {"file_name": "answer", "format": format}
# response = requests.get(url, params=params)

# if response.status_code == 200:
#     # Get the file name from the response headers
#     content_disposition = response.headers.get("Content-Disposition")

#     if content_disposition:
#         filename_from_header = content_disposition.split("filename=")[1]
#     else:
#         filename_from_header = filename + ".csv"

#     # storage = directory2 + filename +"."+ format
#     # Save the content to the local file
#     # with open(storage, "wb") as file:
#     #     file.write(response.content)

#     file_like_object = io.BytesIO(response.content)
#     code_frame_data = pd.read_csv(file_like_object)
        
#     init_insert_result(actual_data,code_frame_data)


# %%
import requests
import io
####### 모델 API

endpoint = "http://kri.twindoc.ai/kri-api-test-server-1/api"


question_path = 'question.csv'
response_path = 'answer.csv'

cls_model_name = 'kri-2-3-brand-model'
cls_model_version = '1'
snt_model_name = 'kri-1-1-emotion-model'
snt_model_version = '1'
emb_model_name = 'ko-sbert-sts'
emb_model_version = '1'


files = {
    'question': open(question_path, 'rb'),
    'response': open(response_path, 'rb'),
    'cls_model_name': (None, cls_model_name),
    'cls_model_version': (None, cls_model_version),
    'snt_model_name': (None, snt_model_name),
    'snt_model_version': (None, snt_model_version),
    'emb_model_name': (None, emb_model_name),
    'emb_model_version': (None, emb_model_version),
}

response = requests.post(f'{endpoint}/predict', files=files)
response_json = response.json()
# %%
url = "http://43.202.119.16:8000/download-frame"
params = {"file_name": "answer", "format": format}
response = requests.get(url, params=params)

# %%
url = "http://43.202.119.16:8000/download-csv"
params = {"file_name": "answer", "format": "csv"}
response = requests.get(url, params=params)
# directory = nas_path + '/result_data/'
if response.status_code == 200:
    # Get the file name from the response headers
    content_disposition = response.headers.get("Content-Disposition")
    if content_disposition:
        filename_from_header = content_disposition.split("filename=")[1]
    else:
      pass



    file_like_object = io.BytesIO(response.content)
    actual_data = pd.read_csv(file_like_object)
    
    
url = "http://43.202.119.16:8000/download-frame"
params = {"file_name": "answer", "format": format}
response = requests.get(url, params=params)

if response.status_code == 200:
    # Get the file name from the response headers
    content_disposition = response.headers.get("Content-Disposition")

    if content_disposition:
        filename_from_header = content_disposition.split("filename=")[1]
    else:
        pass

    # storage = directory2 + filename +"."+ format
    # Save the content to the local file
    # with open(storage, "wb") as file:
    #     file.write(response.content)

    file_like_object = io.BytesIO(response.content)
    code_frame_data = pd.read_csv(file_like_object)
# %%

net_list = code_frame_data[['TYPE_CLS']].drop_duplicates().reset_index().rename(columns={'index': 'net_code','TYPE_CLS':'net_text'})
# drop any nans from the original
result_data = actual_data.dropna(subset = "TYPE_CLS")

result_data_merge3 = pd.merge(result_data,net_list, 
                    how = "left",
                    left_on = "TYPE_CLS",
                    right_on = "net_text")
result_data_merge3['FILE_NM'] = result_data_merge3['FILE_NM'].apply(lambda x: x.replace(".csv",""))
result_data_merge3['pq_id'] = result_data_merge3['FILE_NM'] + result_data_merge3['SURVEY_QUESTION_CD']
result_data_merge3['net_code'] = result_data_merge3['net_code'].fillna(9999).apply(int)


net_list = result_data_merge3[['pq_id','net_code','TYPE_CLS']]
net_list = net_list.rename(columns = {'TYPE_CLS':'net_text'})
net_list = net_list.drop_duplicates()


result_temp = result_data_merge3[['pq_id', 'IDKEY',
        'TYPE_SIM_GROUP_TXT', 
      'SENTIMENT_CLS','net_code']]

result_temp.columns = ['pq_id','idkey','subnet','emotion','net_code']
# result_temp = result_temp.drop(["net_text","TYPE_CLS"], axis = 1)
result_temp = result_temp.replace({pd.NA: None})

result_temp['net_code'] = result_temp['net_code'].fillna(9999).apply(int)

result_json = result_temp.to_dict(orient= "index")
result_json = [value for _, value in result_json.items()]
# delete uselsess columns & reshape to adequate json format
net_json = net_list.to_dict(orient= "index")
net_json = [value for _, value in net_json.items()]
# %%
update_table("result_data", result_json)
update_table("net_table", net_json)
    
# %%
