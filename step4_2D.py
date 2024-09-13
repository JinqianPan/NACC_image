import numpy as np
import nibabel as nib
# import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd
import os
from PIL import Image

import functools
print = functools.partial(print, flush=True)

DATA_PATH = ''
JSON_DATA_PATH = DATA_PATH + 'json_info.csv'
STRUCTURE_DATA_PATH = '../structure_data/investigator_mri_nacc65.csv'
IMAGE_PATH = os.path.join(DATA_PATH, 'data')

json_info = pd.read_csv(JSON_DATA_PATH, dtype=str)
json_info_columns_selected = json_info.loc[:, ['FILENAME', 'JSONName', 'BodyPartExamined']]

structure_data = pd.read_csv(STRUCTURE_DATA_PATH)
structure_data = structure_data[ ['NACCID', 'NACCMNUM'] ] 
structure_data['FILENAME'] = structure_data['NACCID'] + '_' + structure_data['NACCMNUM'].apply(lambda x: f"{x:02}")

merged_data = json_info_columns_selected.merge(structure_data, how='left', on='FILENAME').drop_duplicates()
merged_data = merged_data[~merged_data['BodyPartExamined'].isin(['LIVER', 'CSPINE'])].reset_index(drop=True)

def determine_scan_orientation(affine):
    z_vector = affine[:3, 2]
    major_axis = ['X', 'Y', 'Z'][np.argmax(np.abs(z_vector))]
    orientation = 'Head-to-Foot' if z_vector[2] > 0 else 'Foot-to-Head'
    return major_axis, orientation

def extract_slices(img, orientation, time_point=0):
    # extract data from nii.gz file
    try:
        data = img.get_fdata()
    except:
        rgb_data = np.array(img.dataobj)
        data = np.stack([rgb_data['R'], rgb_data['G'], rgb_data['B']], axis=-1)
    # If there are 4 dim, then make it as 3 dim
    if data.ndim == 4:
        if data.shape[2] < 5:
            data = data[:, :, time_point, :]
        else:
            data = data[:, :, :, time_point]

    if data.shape[0] < data.shape[1] and data.shape[0] < data.shape[2]:
        # the first dim is z-axis
        if orientation == 'Head-to-Foot':
            proximal_slice = data[0, :, :]
        else:
            proximal_slice = data[-1, :, :]
        middle_slice = data[data.shape[0] // 2, :, :]
    else:
        if orientation == 'Head-to-Foot':
            proximal_slice = data[:, :, 0]
        else:
            proximal_slice = data[:, :, -1]
        middle_slice = data[:, :, data.shape[2] // 2]
    return proximal_slice, middle_slice

def save_slice_as_image(slice_data, file_path, file_name):
    min_val = np.min(slice_data)
    max_val = np.max(slice_data)
    normalized_slice = (slice_data - min_val) / (max_val - min_val + 1e-10)
    image_data = (255 * normalized_slice).astype(np.uint8)
    
    image = Image.fromarray(image_data)
    
    # if image.size[0] > 256 or image.size[1] > 256:
    if image.size[0] >= 128 or image.size[1] >= 128:
        image = image.resize((256, 256), Image.Resampling.LANCZOS)
        file_paths = os.path.join(file_path, 'data', file_name)
    else:
        file_paths = os.path.join(file_path, 'small_data', file_name)

    image.save(file_paths)
    print(f'Saving image of size: {image.size} (Width x Height)')

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == '__main__':
    PROXIMAL_SAVING_PATH = os.path.join(DATA_PATH, '2D_image_v4', '2D_proximal')
    MIDDLE_SAVING_PATH = os.path.join(DATA_PATH, '2D_image_v4', '2D_middle')
    subdirs = ['small_data', 'data']

    for subdir in subdirs:
        create_directory(os.path.join(PROXIMAL_SAVING_PATH, subdir))
        create_directory(os.path.join(MIDDLE_SAVING_PATH, subdir))
    
    error_file = []
    for index in tqdm(range(merged_data.shape[0])):
        try:
            file_name = merged_data['FILENAME'][index]
            NACCID = merged_data['NACCID'][index]
            real_file_name = merged_data['JSONName'][index].split('.json')[0]
            nii_file_name = real_file_name + '.nii.gz'
            file_path = os.path.join(IMAGE_PATH, NACCID, file_name, nii_file_name)

            # Load file once
            image_data = nib.load(file_path)
            axis, orientation = determine_scan_orientation(image_data.affine)
            proximal_slice, middle_slice = extract_slices(image_data, orientation)

            proximal_file_name = file_name + '_' + real_file_name + '.jpg'
            middle_file_name = file_name + '_' + real_file_name + '.jpg'

            # Save images
            print()
            save_slice_as_image(proximal_slice, PROXIMAL_SAVING_PATH, proximal_file_name)
            save_slice_as_image(middle_slice, MIDDLE_SAVING_PATH, middle_file_name)
        
        except Exception as e:
            print(f'Error processing index {index}: {str(e)}')
            error_file.append(index)

    print(f'Indices with errors: {error_file}')