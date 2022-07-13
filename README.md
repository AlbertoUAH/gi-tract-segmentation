# GI Tract Segmentation
__Author__: Fernández Hernández, Alberto

## Summary 📖

The main purpose is create a model to __automatically segment the stomach and intestines (small and large) on MRI scans__. The MRI scans are from actual cancer patients who had 1-5 MRI scans on separate days during their radiation treatment.

## Architecture diagram

<p align="center">
<img src="https://github.com/AlbertoUAH/gi-tract-segmentation/blob/main/media/diagram.png" class="center" width="600" height="360"/>
</p>
 
 
## Preview
<img src="https://github.com/AlbertoUAH/gi-tract-segmentation/blob/main/media/readme-video.gif"/>

## Dataset source 

<p align="center">
<img src="https://brand.wisc.edu/content/uploads/2016/11/uw-crest-color-300x180.png" width="300" height="150"/>
</p>

[UW-Madison GI Tract Image Segmentation - Kaggle dataset](https://www.kaggle.com/competitions/uw-madison-gi-tract-image-segmentation)


## Tools

* __Storage__: Google Cloud Storage
* __Code__: Python 3.7 + Google Cloud functions
* __Libraries__:
  * PyTorch
  * Albumentations
  * Image Segmentation Models (smp) library
  * Pydicom
  * Sci-kit Learn
  * Matplotlib
  * Skimage
  * tqdm
  * wandb
  * OpenCV
  * Numpy
  * Google-cloud
