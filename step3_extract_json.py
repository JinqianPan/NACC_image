import os
import pandas as pd
import shutil
from tqdm import tqdm
import json

import warnings
warnings.filterwarnings("ignore")

import functools
print = functools.partial(print, flush=True)

BASEPATH = ''
BASEDIR = os.path.join(BASEPATH, 'data')
saving_file_name = 'json_info.csv'

if __name__ == '__main__':
    paths = []
    for root, dirs, files in os.walk(BASEDIR):
        for file_name in files:
            if file_name.endswith(".json"):
                file_path = os.path.join(root, file_name)
                paths.append(file_path)
    print(len(paths))

    json_data = []
    error_line = []
    for file_path in tqdm(paths):
        try:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            except json.JSONDecodeError:
                # If initial JSON load fails, read again and replace '-nan' with '0', '-inf' with '0', 'nan' with '0'
                with open(file_path, 'r', encoding='utf-8') as file:
                    tmp_data = file.read().replace('-nan', '0').replace('-inf', '0').replace('nan', '0')
                    data = json.loads(tmp_data)

            json_name = file_path.split('/')[-1]
            FILENAME = file_path.split('/')[-2]
            data['FILENAME'] = FILENAME
            data['JSONName'] = json_name
            json_data.append(data)
        except Exception as e:
                error_line.append(file_path)
                print('Error:', file_path, '.', e)
    df = pd.DataFrame(json_data)
    print(error_line)

    df.to_csv(BASEPATH + saving_file_name, index=False, header=True)

    #################################################
    # Remove the tmp data, please open this comment #
    #################################################
    
    # data_folders = [f'unzip_{i}' for i in range(1, 21)] + [f'unzip_new_{i}' for i in range(1, 6)]
    # for data_folder in data_folders:
    #     shutil.rmtree(os.path.join(BASEPATH, data_folder))