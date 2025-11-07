import sys
import glob
import pandas as pd
import json
import re
import os
# read csv data into data frames with schemas dynamically

# glob => to get filenames

files_glob=glob.glob('data/retail_db/**',recursive=True)

files_glob=glob.glob('data/retail_db/*/*',recursive=True)

src_file_names=glob.glob('data/retail_db/*/part-*',recursive=True)



def get_columns_name(schemas,ds_name,sorting_key='column_position'):
    column_details=schemas[ds_name]
    columns=sorted(column_details,key=lambda col:col[sorting_key])
    return [col['column_name'] for col in columns]

# modularize file format converter for dataset

def file_converter(src_base_dir,tgt_base_dir,ds_name):

    schemas=json.load(open(f'{src_base_dir}/schemas.json'))
    files=glob.glob(f'{src_base_dir}/{ds_name}/part-*')
    if len(files)==0:
        raise NameError(f'No files found for dataset  === {ds_name} === in source directory')
    for file in files:
        df=read_csv(file,schemas)
        file_name=re.split('[/\\\]',file)[-1]
        to_json(df,tgt_base_dir,ds_name,file_name)

def process_files(ds_names=None):
    src_base_dir=os.environ.get('SRC_BASE_DIR')
    tgt_base_dir=os.environ.get('TGT_BASE_DIR')
    schemas=json.load(open(f'{src_base_dir}/schemas.json'))
    if not ds_names:
        ds_names=schemas.keys()
    for ds_name in ds_names:
        try:
            print(f'processing dataset: {ds_name}')
            file_converter(src_base_dir,tgt_base_dir,ds_name)
        except Exception as e:
            print(f'Error processing dataset {ds_name}: {e}')
            pass
        
           

def read_csv(file,schemas):
    file_path_list=re.split('[/\\\]',file)
    ds_name=file_path_list[-2]
    columns=get_columns_name(schemas,ds_name)
    df=pd.read_csv(file,names=columns)
    return df


def to_json(df,tgt_base_dir,ds_name,file_name):
    json_file_path=f'{tgt_base_dir}/{ds_name}/{file_name}'
    os.makedirs(f'{tgt_base_dir}/{ds_name}',exist_ok=True)
    df.to_json(
        json_file_path,
        orient='records',
        lines=True
        )
    

if __name__=='__main__':
    if len(sys.argv)==2: 
        ds_names=json.loads(sys.argv[1])
        process_files(ds_names)
    else:
        process_files()








# 1. set env variables to run 
# $Env:SRC_BASE_DIR = "data/retail_db" and $Env:TGT_BASE_DIR="data/retail_db_json"
# python hello.py '[\"orders\",\"order_items\"]'
# 2.(JSON arrays as arguments => python hello.py '[\"orders\",\"order_items\"]') ds_names=json.loads(sys.argv[1])
    # process_files(ds_names)
# 3. Pass Data Sets as Run Time Arguments to File Format Converter =>