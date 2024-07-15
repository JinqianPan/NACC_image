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
> Please make sure you have enough memory to save the new clean data.
>
> The final data should be about 650G. If you do not want to change my code, please make sure you have about 1.6T memory.

### Step 1:
