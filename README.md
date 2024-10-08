# NACC MRI Data Processing

Due to the row MRI data from NACC is too messy, this repo is working for **handling the MRI data**.

>[!TIP]
> For how to `download the image data` from NACC AWS S3 bucket, please browse [my guide](https://github.com/JinqianPan/NACC_img_download).

---
## Before coding:
### Some explanation:
1. The row data from NACC are a large amount of zip files; after decompression, there will be a nested folder, representing all the MRI data of each patient after an encounter (including `*.nii and *.json`).
2. The `*.nii` files always could be compressed as `*.nii.gz`
3. Because we can find information from JSON files and structure data, we could read the information from JSON and rebuild the folder by using structure data (`investigator_mri_nacc65.csv`).
4. The NACC data is still updating. They would give `some overlap data` (For our version, the overlap is around 5,000 files). In the code, we also will handle these data.

After processing, the folder tree would be like:
```
FOLDER
    |- data
        |- {NACCID 001}
            |- {NACCID 001}_{encounter times 01}
                |- *.nii.gz
                |- *.json
            |- {NACCID 001}_{encounter times 02}
        |- {NACCID 002}
            |- {NACCID 002}_{encounter times 01}
    |- All JSON extracted information (csv file)
    |- Readme
```

### Package
We are using the package below.
```
pip install gzip
pip install zipfile
pip install tqdm
pip install argparse
pip install pandas
pip install json
```

## Coding part

>[!IMPORTANT]
> 1. Please make sure you have enough memory to save the new clean data. The final data should be about 650G. If you do not want to change my code, please make sure you have about 1.6T memory.
> 2. Please change the path in three code files.

### Step 1: decompressing the whole zip file and compressing the `*.nii` to `*.nii.gz`

Usage:
```python
python step1_compress_nii.py --total_machine 20 --machine_num 1 --data old
```
Due to bunch of files, the first step uses several machines (use slurm to run).

* total_machine: how many machine you gonna to use.
* machine_num: the number of machine in this way (e.g. if total_machine == 20, then machine_num $\in$[1, 20]).
* data: which version data you used.

### Step 2: rebuild our folder tree
The example folder tree is shown above. In this step, we rebuild the folder tree.

```python
python step2_move_data.py
```

if you do not want to have the dummy data file, please change line45 from `shutil.copytree` to `shutil.movetree`

### Step 3: extract JSON files
Extracting all of JSON files to a dataframe (csv file).
```python
python step3_extract_json.py
```

>[!NOTE]
> Please browse line52-58 to delete the intermediate files.
>
> OR you can use command line: `rm -rf {filename}` to delete the files

### Step 4: Get the 2D image
Extracting 2D MRI data from the 3D MRI data.

```python
python step4_2D.py
```

## Citation
If you use MRISeqClassifier in your research, please cite our paper:

```
@article {Pan2024.09.19.24313976,
	author = {Pan, Jinqian and Chen, Qi and Sun, Chengkun and Liang, Renjie and Bian, Jiang and Xu, Jie},
	title = {MRISeqClassifier: A Deep Learning Toolkit for Precise MRI Sequence Classification},
	elocation-id = {2024.09.19.24313976},
	year = {2024},
	doi = {10.1101/2024.09.19.24313976},
	publisher = {Cold Spring Harbor Laboratory Press},
	URL = {https://www.medrxiv.org/content/early/2024/09/22/2024.09.19.24313976},
	journal = {medRxiv}
}

```
