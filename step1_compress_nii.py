# 1. Decompress the zip files
# 2. Compress nii files to nii.gz files
# 3. Because we get expansion data from NACC, we need to merge them together

import gzip
import shutil
import zipfile
from tqdm import tqdm
import os
import sys
import functools
print = functools.partial(print, flush=True)
import argparse

# ------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--total_machine', type=int, default=-1)
parser.add_argument('--machine_num', type=int, default=-1)
parser.add_argument('--data', type=str, default='old')
args = parser.parse_args()
print('\n\n', args, '\n\n')

# ------------------------------------------------------------
MRI_PATH = ''
MRI_PATH_NEW = ''
SAVING = ''

MRI_PATH_all = MRI_PATH + 'all/nifti/'
MRI_PATH_1yr = MRI_PATH + '/within1yr/nifti/'

MRI_PATH_NEW_all = MRI_PATH_NEW + 'all/nifti/'
MRI_PATH_NEW_1yr = MRI_PATH_NEW + '/within1yr/nifti/'

if args.data == 'old':
    SAVING_PATH = SAVING + f'unzip_{args.machine_num}/'
elif args.data == 'new':
    SAVING_PATH = SAVING + f'unzip_new_{args.machine_num}/'

# ------------------------------------------------------------
try:
    if not os.path.exists(SAVING_PATH):
        os.makedirs(SAVING_PATH)
    print('Create saving_path')
except Exception as e:
    print('failed to create saving_path\n', e)

# ------------------------------------------------------------

def get_zip_file_name(path):
    zip_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.zip'):
                zip_files.append(file)
    return zip_files

def unzip_file(tmp_saving_path, MRI_PATH, FILE_NAME):
    # Unzip file
    if not os.path.exists(tmp_saving_path):
        os.makedirs(tmp_saving_path)

    with zipfile.ZipFile(MRI_PATH+FILE_NAME, 'r') as zip_ref:
        zip_ref.extractall(tmp_saving_path)
        print(f"finish unzip to {tmp_saving_path}")

def compress_nii(tmp_saving_path):
    for root, dirs, files in os.walk(tmp_saving_path):
        for file_name in files:
            if file_name.endswith(".nii"):
                file_path = os.path.join(root, file_name)

                with open(file_path, 'rb') as f_in:
                    with gzip.open(file_path+'.gz', 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(file_path)

def running_part(zip_files, all_path, within1yr_path, error_line, bad_file):
    for zip_file in tqdm(zip_files):
        tmp_file_name = zip_file.split('ni')[0]
        tmp_saving_path = SAVING_PATH + tmp_file_name

        try:
            unzip_file(tmp_saving_path, all_path, zip_file)
        except Exception as e:
            try:
                unzip_file(tmp_saving_path, within1yr_path, zip_file)
            except Exception as e:
                error_line.append(zip_file)
                bad_file.append(zip_file)
                print('Error:', zip_file, '.', e)
        
        try:
            compress_nii(tmp_saving_path)
        except Exception as e:
            error_line.append(zip_file)
            print('Error:', zip_file, '.', e)
        
    return error_line, bad_file

if __name__ == '__main__':

    old_data = get_zip_file_name(MRI_PATH_all)
    new_data = set(get_zip_file_name(MRI_PATH_NEW_all))
    new_data = list(new_data - set(old_data).intersection(new_data))
    old_data.sort()
    new_data.sort()


    error_line = []
    bad_file = []

    if args.data == 'old':
        print('Total file number:', len(old_data))
        intermediate = len(old_data) // args.total_machine + 1
        begin_num = (args.machine_num - 1) * intermediate
        finish_num = args.machine_num * intermediate

        if finish_num > len(old_data):
            finish_num = len(old_data)
        
        print('begin_num:', begin_num)
        print('finish_num:', finish_num, '\n')

        running_data = old_data[begin_num: finish_num]

        error_line, bad_file = running_part(running_data, MRI_PATH_all, MRI_PATH_1yr, error_line, bad_file)
    elif args.data == 'new':
        print('Total file number:', len(new_data))
        intermediate = len(new_data) // args.total_machine + 1
        begin_num = (args.machine_num - 1) * intermediate
        finish_num = args.machine_num * intermediate

        if finish_num > len(new_data):
            finish_num = len(new_data)
        
        print('begin_num:', begin_num)
        print('finish_num:', finish_num, '\n')
        running_data = new_data[begin_num: finish_num]
        error_line, bad_file = running_part(running_data, MRI_PATH_NEW_all, MRI_PATH_NEW_1yr, error_line, bad_file)

    if len(error_line) > 0:
        print(len(error_line))
        print(error_line)
    else:
        print('Do not have error.')

    if len(bad_file) > 0:
        print(len(bad_file))
        print(bad_file)
        