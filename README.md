# GI Tract Segmentation
__Author__: Fernández Hernández, Alberto

__Date__: 2022 - 07 - 13

## Summary 📖

The main purpose is create a model to __automatically segment the stomach and intestines (small and large) on MRI scans__, in order to outline the position of the stomach and intestines to adjust the direction of the x-ray beams to increase the dose delivery to the tumor and avoid main organs. A method to segment the stomach and intestines would make treatments much faster and would allow more patients to get more effective treatment. The MRI scans are from actual cancer patients who had 1-5 MRI scans on separate days during their radiation treatment.

## Architecture diagram

<p align="center">
<img src="https://github.com/AlbertoUAH/gi-tract-segmentation/blob/main/media/diagram.png" class="center" width="600" height="360"/>
</p>

## Deep learning model

Two models are proposed:

* __UNet VS Feature Pyramid Network (FPN)__
 
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
