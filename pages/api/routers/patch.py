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
from .db_connection import supaDB
from matplotlib import colors as mcolors
from typing import Optional

db = supaDB()
router = APIRouter(
    prefix="/net",
    tags=["net"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

url = "https://zyqtytdhyppqhrherzni.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp5cXR5dGRoeXBwcWhyaGVyem5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDA3OTE0MzUsImV4cCI6MjAxNjM2NzQzNX0.z2Gk2eJvKsvfkrtXgqY4s1s5xggFpmPkJFG8BMIBKz4"

supabase: Client = create_client(url, key)

def update_table(TABLE_NAME,data_to_add):
    data, _ = supabase.table(TABLE_NAME).insert(data_to_add).execute()
    return data

def get_df_from_pname(p_name, question):
    
    pq_val_query = f'''select pq_id from project_meta where question_text = '{question}' and project_name = '{p_name}'
    '''
    df = db.query2df(pq_val_query)
    print(df)
    pq_val = df.iloc[0,0]
    print ( pq_val)
    
    query = f"""SELECT CONCAT(rd.pq_id, '+', rd.idkey) as id , 
    nt.net_text, 
    rd.subnet, 
    rd.emotion 
    FROM result_data as rd
                LEFT JOIN net_table as nt
                on rd.net_code = nt.net_code
                where rd.pq_id = '{pq_val}'
                and nt.pq_id = '{pq_val}'
    """
    print(query)
    df = db.query2df(query)
    
    return df

def generate_fixed_alpha_rgba_strings(num_colors, fixed_alpha=0.6):
    # Get a list of distinct colors from the 'tab10' colormap
    color_list = list(mcolors.TABLEAU_COLORS.values())

    # If you need more colors than the predefined list, cycle through them
    colors = color_list * (num_colors // len(color_list)) + color_list[:num_colors % len(color_list)]

    # Convert color names to RGBA strings
    rgba_strings = [
        f'rgba({int(val[0] * 255)}, {int(val[1] * 255)}, {int(val[2] * 255)}, {fixed_alpha})'
        for val in [mcolors.to_rgba(color)[:3] for color in colors]
    ]

    return rgba_strings

def parse_xlsx_or_csv(file, filename):
    # file = file.seek(0)
    # df = pd.read_csv(file, encoding = 'utf-8',skiprows =1)

    try:
        if filename.endswith('.xlsx'):
            df = pd.read_excel(file, skiprows=1)
        else:
            df = pd.read_csv(file, encoding = 'cp949', skiprows=1)
            
    except UnicodeDecodeError:
        file.seek(0)
        try:
            df = pd.read_csv(file, encoding = 'utf-8',skiprows =1)
        except:
            file.seek(0)
            df = pd.read_csv(file, encoding = 'euc-kr',skiprows =1)
        # df = pd.read_csv(file, encoding = 'cp949', skiprows=1)
    except pd.errors.EmptyDataError:
        # Handle empty file
        df = pd.DataFrame()
    except pd.errors.ParserError:
        # Handle parsing error
        file.seek(0)
        df = pd.read_csv(file, encoding='cp949', errors='replace', skiprows=1)
    
    
    if ((df.columns[0] == "변수 가이드") or df.iloc[0, 0] == "IDKEY"):
        try:
            if filename.endswith('.xlsx'):
                file.seek(0)
                df = pd.read_excel(file)

            else:
                file.seek(0)
                df = pd.read_csv(file, encoding="cp949")

        except pd.errors.EmptyDataError:
            # Handle empty file
            df = pd.DataFrame()

        except pd.errors.ParserError:
            # Handle parsing error
            file.seek(0)
            df = pd.read_csv(file)


    return df
def load_guide_excel(file_path):
    return pd.read_excel(file_path, skiprows=1).fillna(method='ffill')

def is_numeric_string(x):
    try: 
        int(x)
        return False
    except:
        return True
    
def get_open_question_indices(df):
    df = df[df['문항 타입'] == "open"]
    df = df[df['내용'].apply(lambda x: is_numeric_string(x))]
    df = df.dropna(subset = '문항 / 보기번호')
    df = df[~(df['문항 / 보기번호'].str.contains("LAST"))]
    df = df[~(df['문항 / 보기번호'].str.contains("INTRO"))]
    df = df[~(df['문항 / 보기번호'].str.contains("CAPI"))]
    df = df[~(df['문항 / 보기번호'].str.contains("GPS"))]
    df = df[~(df['문항 / 보기번호'].str.contains("SQ"))].index.tolist()
        # df = df[df['내용'].apply(lambda x: is_numeric_string(x))]
    
    return df

def get_question_lengths(q_list, open_list, total_length):
    return {i: q_list[q_list.index(i) + 1] - i if q_list.index(i) + 1 < len(q_list) else total_length - i for i in open_list}

def generate_question_numbers(q_list, lengths):
    return [f"{q_list.loc[i]}_{tail_val}" for i in lengths.keys() for tail_val in range(1, lengths[i])]


def init_insert_result(p_name,result_data, code_frame_data):

    net_list_temp = code_frame_data[['TYPE_CLS']].drop_duplicates().reset_index().rename(columns={'index': 'net_code','TYPE_CLS':'net_text'})
    # drop any nans from the original
    result_data = result_data.dropna(subset = "TYPE_CLS")

    result_data_merge3 = pd.merge(result_data,net_list_temp, 
                        how = "left",
                        left_on = "TYPE_CLS",
                        right_on = "net_text")
    result_data_merge3['FILE_NM'] = result_data_merge3['FILE_NM'].apply(lambda x: x.replace(".csv",""))
    result_data_merge3['pq_id'] = p_name + "_" + result_data_merge3['SURVEY_QUESTION_CD']
    result_data_merge3['net_code'] = result_data_merge3['net_code'].fillna(9999).apply(int)
    print(result_data_merge3)

    net_list = result_data_merge3[['pq_id','net_code','TYPE_CLS']]
    net_list = net_list.rename(columns = {'TYPE_CLS':'net_text'})
    net_list = net_list.drop_duplicates()


    result_temp = result_data_merge3[['pq_id', 'IDKEY',
            'TYPE_SIM_GROUP_TXT', 
        'SENTIMENT_CLS','net_code']]

    result_temp.columns = ['pq_id','idkey','subnet','emotion','net_code']
    # result_temp = result_temp.drop(["net_text","TYPE_CLS"], axis = 1)
    result_temp = result_temp.replace({pd.NA: None})
    result_temp = result_temp.dropna(subset = "net_code")
    result_temp['net_code'] = result_temp['net_code'].fillna(9999).apply(int)

    result_json = result_temp.to_dict(orient= "index")
    result_json = [value for _, value in result_json.items()]
    # delete uselsess columns & reshape to adequate json format
    net_json = net_list.to_dict(orient= "index")
    net_json = [value for _, value in net_json.items()]

        
    update_table("result_data", result_json)
    update_table("net_table", net_json)
    
    return {"message": "update result compelete"}


# @router.get("/net_info")
# async def net_info(p_name):
#     # make sure from the query, get only the higest version of each net
#     # which is filtered by p_id
#     query = f"""select * from get_max_net_version ('{p_name}')
#                 """
#     data = db.query2df(query)
#     print(data)

#     # data = data[1] 
#     print(data)
#     data = data.to_dict(orient= "index")
#     net_json = [value for _, value in data.items()]
    
#     return net_json

@router.post("/net-change")
async def net_change(item : Annotated[str, Form()]):
    item_dict = json.loads(item)
    df = pd.DataFrame([item_dict])
    
    pq_id, net_code = df['id'][0].split("+")
    net_text = df['net_text'][0]
    
    db.query_call('''update net_table 
                  set 
                  net_text = :net_text
                  WHERE pq_id = :pq_id
                  and net_code = :net_code
                ''', {'net_text': net_text, 'pq_id': pq_id, 'net_code': net_code})
    
    return {"updated"}


@router.get("/data-check")
async def net_data(p_name, question):

    df = get_df_from_pname(p_name,question)
    dict_Val = df.to_json(orient= 'index', force_ascii= False)
    
    return dict_Val

@router.post("/data-change")
async def data_change(item : Annotated[str, Form()]):
    item_dict = json.loads(item)
    
    df = pd.DataFrame([item_dict])
    

    pq_idkey = df['id'][0]
    pq_id = pq_idkey.split("+")[0]
    idkey = pq_idkey.split("+")[1]
    subnet = df['subnet'][0]
    emotion = df['emotion'][0]
    net_text = df['net_text'][0]
    
    net_code = db.query2df(f'''select net_code from net_table
                           where net_text = '{net_text}'
                           and pq_id = '{pq_id}'
                           ''')
    
    net_code = net_code.iloc[0,0]

    net_query = f'''UPDATE result_data
                    SET 
                    subnet = '{subnet}',
                    emotion = '{emotion}',
                    net_code = '{net_code}'
                    WHERE pq_id = '{pq_id}'
                    and idkey = '{idkey}';
                    '''

    df = db.query_call(net_query)
    return {"updated"}

def get_df_from_pname_pame(p_name,q_code):
    if q_code == '':
        query = f"""select * from result_data as rd
                    left join net_table as nt
                    on rd.pq_id = nt.pq_id
                    left join project_meta as pm
                    on rd.pq_id = pm.pq_id 
                    where rd.pq_id like '%{p_name}%' 
                    """
    else:
        query = f"""select * from result_data as rd
                    left join net_table as nt
                    on rd.pq_id = nt.pq_id
                    left join project_meta as pm
                    on rd.pq_id = pm.pq_id 
                    where rd.pq_id like  '%{p_name}%'
                    and pm.question_text = '{q_code}'
    """
    print(query)
    df = db.query2df(query)
    
    return df

@router.get("/simple-graph")
async def transform(p_name, graph_type, Q_code: str = "", top_n : str = "50", emotion: Optional[str] = None):
    # pandas df 형태로 데이터 호출
    df = get_df_from_pname_pame(p_name, Q_code)
    
    # if Q_code == "":
    #     df=  data.copy()

    # else:
    #     dict_part = data[data['question_text'] == Q_code]
    #     df = pd.DataFrame(dict_part)
    
        # est: 모델 net 예측값, 'IDKEY'는 단순 count를 위한 아무열
    filtered_df = df[['idkey','net_text','emotion']].groupby(['net_text','emotion']).count().reset_index()
    filtered_df_sort = filtered_df.sort_values(by = 'idkey',ascending= False)
    # 없음/모름/무응답을 제외한 top 5를 보여주기 위한 방식. 
    # 이후 top 5 -> top n 으로 파라미터 화 가능
    filtered_df_sort = filtered_df_sort[filtered_df_sort['net_text']
                                        !='없음/모름/무응답']
    
    
    if top_n == "all" :
        pass
    elif top_n == "50":
        total_value = filtered_df_sort['idkey'].sum()
        filtered_df_sort = filtered_df_sort[filtered_df_sort['idkey'] > 0.01 * total_value]
    else:
        filtered_df_sort = filtered_df_sort[:int(top_n)]


    if graph_type == "bar":
        if (emotion == '긍정') or (emotion == '부정'):
            filtered_df_sort = filtered_df_sort[filtered_df_sort['emotion']==emotion]
        else:
            filtered_df_sort = filtered_df_sort.groupby('net_text').count().reset_index()
            
            
        labels = filtered_df_sort['net_text'].tolist()
        data = filtered_df_sort['idkey'].tolist()  
        print("labels:",labels)  
        print(data)
        dataset = [
            {
                'data' : data,
                'backgroundColor': 'rgba(230,125,126 , 0.5)',
                'borderColor': 'rgba(230,125,126 , 1)',
                'borderWidth': 1,
            }
        ]

        chartData = {
        'labels': labels,
        'datasets': dataset,
        }
    
        
        
    elif graph_type == "pie":
        
        filtered_df_sort = filtered_df_sort.groupby('net_text').sum().reset_index()
        filtered_df_sort = filtered_df_sort.sort_values('idkey')
        filtered_df_sort = filtered_df_sort.drop('emotion', axis = 1)
        filtered_df_sort  = filtered_df_sort.rename(columns = {'net_text':'label', 'idkey':'value'})
        filtered_df_sort = filtered_df_sort.reset_index()
        filtered_df_sort = filtered_df_sort.rename(columns = {'index':'id'})
        num_data_points = len(filtered_df_sort)
        total = len(df['idkey'].drop_duplicates())
        bg_colors = generate_fixed_alpha_rgba_strings(num_data_points, 0.5)

        border_color = generate_fixed_alpha_rgba_strings(num_data_points, 1)
 
        dataset = filtered_df_sort.to_dict(orient = 'records')
        print(dataset)
        chartData= dataset

    elif graph_type == "line":
        labels = filtered_df_sort['net_text'].tolist()
        data = filtered_df_sort['idkey'].tolist()    
        
        datasets= [
        {
            'label': 'Chart Example',
            'data': data,
            'backgroundColor': 'rgba(75, 192, 192, 0.6)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'type':'line',
            'display': 'false',
            'borderWidth': 1,
        },
        ]

        chartData = {
        'labels': labels,
        'datasets': datasets,
        }
        
    elif graph_type == "stacked":
        
        part_df = df[['emotion','net_text','idkey']]
        
        pos_df = part_df[part_df['emotion']=="긍정"].groupby('net_text').count().reset_index().sort_values(by = 'IDKEY',ascending= False)
        neg_df = part_df[part_df['emotion']=="부정"].groupby('net_text').count().reset_index().sort_values(by = 'IDKEY',ascending= False)
        nut_df = part_df[part_df['emotion']=="알수없음"].groupby('net_text').count().reset_index().sort_values(by = 'IDKEY',ascending= False)
        
        pos_df = pos_df['net_text'].tolist()
        neg_df = neg_df['net_text'].tolist()
        nut_df = nut_df['net_text'].tolist()
        # labels = filtered_df_sort['n_label'].tolist()
        # data = filtered_df_sort['IDKEY'].tolist()    
        
        chartData= [
        {
            'label': '긍정',
            'data': pos_df,
            'backgroundColor': 'rgba(75, 192, 192, 0.6)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1,
        },
                {
            'label': '알수없음',
            'data': nut_df,
            'backgroundColor': 'rgba(75, 192, 192, 0.6)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1,
        },
                        {
            'label': '부정',
            'data': neg_df,
            'backgroundColor': 'rgba(75, 192, 192, 0.6)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1,
        },
        ]

        # chartData = {
        # 'labels': labels,
        # 'datasets': datasets,
        # }
        
    elif graph_type == "sample":    
        
        filtered_df_sort = filtered_df_sort[filtered_df_sort['emotion']==emotion]
        # filtered_df_sort = filtered_df_sort.drop('emotion', axis= 1)
        labels = filtered_df_sort['net_text'].tolist()
        bar_data = filtered_df_sort['idkey'].tolist()    
        line_data = filtered_df_sort['idkey'].tolist()    
        
        
        
        # filtered_df_sort = filtered_df_sort[['id','net_text']].set_index('net_text')
        dataset = filtered_df_sort.to_dict(orient = 'records')
        
        chartData = dataset
        
        # datasets= [
            
        # {
        #     'label': 'line',
        #     'data': line_data,
        #     'backgroundColor': 'rgba(75, 192, 192, 0.6)',
        #     'borderColor': 'rgba(75, 192, 192, 1)',
        #     'type':'line',
        #     'borderWidth': 1,
        #     'datalabels': {
        #         'display': 'false'},
        # },
        # {          
        #     'label': 'bar',
        #     'data' : bar_data,
        #     'backgroundColor': 'rgba(121,173,210, 0.7)',
        #     'borderColor': 'rgba(121,173,210, 1)',
        #     'type':'bar',
        #     'borderWidth': 1,
        #     'datalabels': {
        #         'display': 'false'},

        # } 
        # ]

        # chartData = {
        # 'labels': labels,
        # 'datasets': datasets,
        # }
    return chartData


# DB에 파일 올라기
@router.post("/upload_file")
# async def upload_file(model_type, answer_file: UploadFile, question_file: UploadFile ):
async def upload_file(files:  list[UploadFile] ):
    answer_file = files[0]
    question_file = files[1]
    
    answer_contents = await answer_file.read()
    question_contents = await question_file.read()
    answer_filename, file_extension = os.path.splitext(answer_file.filename)
    if not  (answer_contents or question_contents):
        return {"message": "파일 형식을 확인 해주세요"}
    else:
        # try:
        upload_data = parse_xlsx_or_csv(io.BytesIO(answer_contents), answer_file.filename)   
        a_df = pd.DataFrame.from_dict(upload_data)
        # a_df.to_csv( '/home/aibd/webtest/app/sample/abc'+f"/raw_data/{answer_filename}.csv", index=False)
        upload_data = parse_xlsx_or_csv(io.BytesIO(question_contents), question_file.filename)
        q_df = pd.DataFrame.from_dict(upload_data)
        # q_df.to_csv( '/home/aibd/webtest/app/sample/abc'+f"/question/{answer_filename}.csv", index=False)
        
        open_question_indices = get_open_question_indices(q_df)
        whole_question_indices = q_df[q_df['문항 / 보기번호'].apply(is_numeric_string)].index.tolist()

        lengths_dict = get_question_lengths(whole_question_indices, open_question_indices, len(q_df))
        q_list = q_df['문항 / 보기번호'].loc[lengths_dict.keys()].apply(lambda x: x.split("_")[0])
        q_final = generate_question_numbers(q_list, lengths_dict)

        df = a_df[q_final]
        df.dropna(axis=1, how='all', inplace=True)
        df = df.fillna(" ")

        phone_cols = df.select_dtypes(include='object').apply(lambda col: col.str.match('\d{3}-\d{4}-\d{4}')).any()
        false_phone_cols = phone_cols.index[phone_cols].tolist()
        name_cols = df.select_dtypes(include='object').apply(lambda col: col.str.match('[가-힣]{0,3}$')).all()
        false_name_cols = name_cols.index[name_cols].tolist()

        num_temp = df.apply(pd.to_numeric, errors='coerce')
        num_temp.dropna(axis=1, how='all', inplace=True)

        numeric_cols = num_temp.select_dtypes(include=['int', 'float']).columns.tolist()
        numeric_cols.extend(false_phone_cols)
        numeric_cols.extend(false_name_cols)

        columns_to_drop = df.columns[~df.columns.isin(numeric_cols)].tolist()

        data_file = a_df[['IDKEY'] + columns_to_drop]
        column_order = ['IDKEY'] + [col for col in data_file.columns if col != 'IDKEY']

        data_file = data_file[column_order]
        new_list = [q_name.split("_")[0] for q_name in columns_to_drop]
        temp_new_q_list = [q_list[q_list == val].index[0]  for val in new_list if val in q_list.values]

        new_q_list = [[val]*(count-1) for val, count in lengths_dict.items() if val in temp_new_q_list]
        new_q_list = [item for sublist in new_q_list for item in sublist]

        survey_file = q_df['내용'].loc[new_q_list]
        survey_file = pd.DataFrame(survey_file)

        survey_file['SURVEY_QUESTION_CD'] = columns_to_drop
        survey_file = survey_file.reset_index()
        survey_file.columns = ['QUESTION_KEY','SURVEY_QUESTION_TXT','SURVEY_QUESTION_CD']
        survey_file = survey_file[['QUESTION_KEY','SURVEY_QUESTION_CD','SURVEY_QUESTION_TXT']]


        #pq_id(pj_name_q_code) project_name , question_code, question_text
        project_meta = survey_file[['SURVEY_QUESTION_CD','SURVEY_QUESTION_TXT']]
        project_meta.columns = ['question_code','question_text']
        project_meta['project_name'] = answer_filename
        project_meta['pq_id'] = project_meta['project_name'] + "_" + project_meta['question_code']
        data_to_add = project_meta.to_dict(orient="index")
        data_json = [value for _, value in data_to_add.items()]
        print(data_to_add)
        _ , data = update_table("project_meta", data_json)
        
        
        
        # data_to_add = { "project_name": answer_filename}
        # _ , data = update_table("project", data_to_add)
        # p_id = data[0]['project_id']
        # ## update datae to columns table
        # survey_file2 = survey_file[['SURVEY_QUESTION_CD','SURVEY_QUESTION_TXT']]
        # survey_file2.columns = ['question_code','question_text']
        # survey_file2['project_id'] = p_id
        # data_to_add = survey_file2.to_dict(orient="index")
        # survey_json = [value for _, value in data_to_add.items()]
        # _ , data = update_table("columns", survey_json)
        # colum_df = pd.DataFrame(data)
        # colum_df = colum_df[['question_code','q_id']]
        ## update data to data table
        data_file = data_file.replace({pd.NA: None})

        cols = data_file.columns.to_list()
        cols.remove("IDKEY")
        data_file2 = data_file.melt(id_vars=['IDKEY'],value_vars = cols, var_name='question_code', value_name='value')
        # data_file2['version_num'] = 0
        # data_file2 = data_file2.rename(columns = {"IDKEY":"idkey"})
        
        data_file2['pq_id'] = answer_filename + "_" + data_file2['question_code']
        print(data_file2)
        data_file2 = data_file2[['pq_id', 'IDKEY','value']]
        data_file2.columns = ['pq_id','idkey','value']
        # data_file2 = pd.merge(data_file2, colum_df, how = 'left', on = "question_code")
        # data_file2 = 
        # data_file2 = data_file2[['idkey','value','version_num','q_id']]

        data_json = data_file2.to_dict(orient= "index")
        data_json = [value for _, value in data_json.items()]

        update_table("raw_data", data_json)
        
        return "끝"
    
@router.post("/edit-raw")
# async def upload_file(model_type, answer_file: UploadFile, question_file: UploadFile ):
async def edit_raw(item : Annotated[str, Form()]):
    item_dict = json.loads(item)
    df = pd.DataFrame([item_dict])
    
    
    
    # data_file2['pq_id'] = answer_filename + "_" + data_file2['question_code']
    # print(data_file2)
    # data_file2 = data_file2[['pq_id', 'IDKEY','value']]
    # data_file2.columns = ['pq_id','idkey','value']
    # update_table("raw_data", data_json)
    # id = df['id'][0]
    # subnet = df['subnet'][0]
    # emotion = df['emotion'][0]
    # net_text = df['net_text'][0]
    # net_query = f"""select net_code from net_table where net_text = '{net_text}'"""

    # net = db.query2df(net_query)['net_code'][0]
    # query = f'''select process_data ('{id}',{net},'{subnet}','{emotion}');'''
    # df = db.query_call(query)
    return {"updated"}

@router.get("/run-model")
async def run_model(p_name, model):

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
    filename = response_json["result"]['response_filename']
    filename = filename.split(".")[0]
    filename = 'answer'
    format = "csv"
    url = "http://43.202.119.16:8000/download-csv"
    params = {"file_name": "answer", "format": format}
    response = requests.get(url, params=params)
    # directory = nas_path + '/result_data/'
    if response.status_code == 200:
        # Get the file name from the response headers
        content_disposition = response.headers.get("Content-Disposition")
        if content_disposition:
            filename_from_header = content_disposition.split("filename=")[1]
        else:
            filename_from_header = filename + ".csv"



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
            filename_from_header = filename + ".csv"

        # storage = directory2 + filename +"."+ format
        # Save the content to the local file
        # with open(storage, "wb") as file:
        #     file.write(response.content)

        file_like_object = io.BytesIO(response.content)
        code_frame_data = pd.read_csv(file_like_object)
            
        init_insert_result(p_name,actual_data,code_frame_data)
    return "끝"


@router.get("/raw_data/send")
async def send_raw(p_name, question_text):

    query = f'''
    SELECT CONCAT(rd.pq_id, '+', rd.idkey) AS id, value FROM raw_data AS rd
    LEFT JOIN project_meta AS pm
    ON rd.pq_id = pm.pq_id
    where pm.project_name = '{p_name}'
    and pm.question_text = '{question_text}'
    '''

    df = db.query2df(query)
    print(df)
    r_json = df.to_json(orient= 'index', force_ascii= False)
    return r_json
    
@router.post("/raw_data/change")
async def change_raw(item : Annotated[str, Form()]):
    item_dict = json.loads(item)
    df = pd.DataFrame([item_dict])
    u_id = df['id'].iloc[0]
    pq_id = u_id.split("+")[0]
    idkey = u_id.split("+")[1]
    value = df['value'].iloc[0]
    #E id, value isNEW
    update_query = f'''UPDATE raw_data
                    SET value = '{value}'
                    WHERE pq_id = '{pq_id}'
                    and idkey = '{idkey}';
                    '''
    print(update_query)
    db.query_call(update_query)
    
    
@router.get("/net_info")
async def net_info(p_name):
    # make sure from the query, get only the higest version of each net
    # which is filtered by p_id
    query = f"""select concat(pq_id, '+', net_code) as id, net_text from net_table 
    where pq_id like ('%{p_name}%')
                """
    data = db.query2df(query)

    data = data.to_dict(orient= "index")
    net_json = [value for _, value in data.items()]
    
    return net_json

@router.get("/file-list")
async def file_list():
    # make sure from the query, get only the higest version of each net
    # which is filtered by p_id
    query = f"""select project_name from project_meta
                """
    data = db.query2df(query)
    data = data.drop_duplicates()
    data = data.to_dict(orient= "index")
    net_json = [value for _, value in data.items()]
    
    return net_json


@router.get("/question-list")
async def question_list(p_name):
    # make sure from the query, get only the higest version of each net
    # which is filtered by p_id
    query = f"""select question_text from project_meta
                where project_name = '{p_name}'
                """
    data = db.query2df(query)

    data = data.to_dict(orient= "index")
    net_json = [value for _, value in data.items()]
    
    return net_json