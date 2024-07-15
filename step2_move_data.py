import os
import pandas as pd
import shutil
from tqdm import tqdm
import functools
print = functools.partial(print, flush=True)

import warnings
warnings.filterwarnings("ignore")

STRUCTURE_DATA_PATH = '../structure_data/investigator_mri_nacc65.csv'
base_path = '/orange/bianjiang/NACC/IMAGE/MRI_clean_data_Jinqian_create/'
base_dir = base_path + 'data/'

if __name__ == '__main__':
# ------------------------------------------------------------
    structure_data = pd.read_csv(STRUCTURE_DATA_PATH)

    structure_data = structure_data[ ['NACCID', 'NACCMRFI', 'NACCNMRI', 'NACCMNUM'] ] 
    structure_data['NACCMRFI'] = structure_data['NACCMRFI'].str.split('.').str[0]
    structure_data['FILENAME'] = structure_data['NACCID'] + '_' + structure_data['NACCMNUM'].apply(lambda x: f"{x:02}")

# ------------------------------------------------------------
    data_folders = [f"unzip_{i}" for i in range(1, 21)] + [f"unzip_new_{i}" for i in range(1, 6)]
    error_line = []

    for folder in data_folders:
        # folder: unzip_1
        folder_path = os.path.join(base_path, folder)
        # folder_path: data/unzip_1/
        if os.path.exists(folder_path):
            subdirectories = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
            # subdirectories: all file names in data/unzip_1/NACCID/
            for sub in tqdm(subdirectories):
                # sub: one file name in data/unzip_1/NACCID/
                matched_rows = structure_data[structure_data['NACCMRFI'] == sub]
                if not matched_rows.empty:
                    # for _, row in matched_rows.iterrows():
                    if len(matched_rows) == 1:
                        row = matched_rows.iloc[0]
                        source_path = os.path.join(folder_path, sub)
                        target_dir = os.path.join(base_dir, row['NACCID'], row['FILENAME'])
                        # target_dir: data/unzip_1/NACCID/NACCID_01/
                        if not os.path.exists(target_dir):
                            shutil.copytree(source_path, target_dir)
                            print(f'     Finish copy {source_path}')
                            print(f'            to {target_dir}')
                            # Move all files from subdirectories to the main directory
                            for root, dirs, files in os.walk(target_dir, topdown=False):
                                for name in files:
                                    file_path = os.path.join(root, name)
                                    new_path = os.path.join(target_dir, name)
                                    shutil.move(file_path, new_path)  # Move file to the main directory
                                # Remove empty directories
                                if root != target_dir:  # Ensure we do not delete the main directory itself
                                    if not os.listdir(root):
                                        os.rmdir(root)  # Remove the directory if it is empty
                                    else:
                                        print('root != target_folder ', root)
                            print('     Finish move files.')
                        else:
                            print(target_dir)
                else:
                    print(sub)
                    print(matched_rows)
                    error_line.append(sub)
        print('finish ' + folder)

    print(error_line)