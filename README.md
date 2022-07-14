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

<style>
    .heatMap {
        width: 70%;
        text-align: center;
    }
    .heatMap th {
        background: grey;
        word-wrap: break-word;
        text-align: center;
    }
    .heatMap tr:nth-child(1) { background: red; }
    .heatMap tr:nth-child(2) { background: orange; }
    .heatMap tr:nth-child(3) { background: green; }
</style>

<div class="heatMap">
 | \# Model                                | Number of parameters | Backbone | Inference Time (GPU) - seconds |
 |----------------------------------------|------------|------------|------------|
 | \# Unet | 8.7 M      | Efficientnet-B1 | 0.0 |
 | \# FPN | 8.2 M      | Efficientnet-B1 | 0.0 |
</div>

__Non empty masks__

| \# Model                                | Dice score large bowel | Dice score small bowel | Dice score stomach |
|----------------------------------------|------------|------------|------------|
| \# __Unet__ | __0.81__      | __0.79__     | __0.90__      |
| \# FPN | 0.73      | 0.73      | 0.89      |


__Empty masks__

| \# Model                                | Dice score large bowel | Dice score small bowel | Dice score stomach |
|----------------------------------------|------------|------------|------------|
| \# __Unet__ | __0.99__      | __0.99__      | __0.99__      |
| \# FPN | 0.95      | 0.95      | 0.99      |

<p align="center">
<img src="https://github.com/AlbertoUAH/gi-tract-segmentation/blob/main/media/deep_learning_architecture.jpg"  width="510" height="190"/>
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
  * Streamlit
  * Skimage
  * tqdm
  * wandb
  * OpenCV
  * Numpy
  * Google-cloud
  
## References

[UW-Madison GI Tract Image Segmentation - Kaggle dataset](https://www.kaggle.com/code/albertouah/uw-madison-gi-tract-image-segmentation-3-unet/edit)

[Segmentation models PyTorch libraries](https://github.com/qubvel/segmentation_models.pytorch)

[A prior knowledge guided deep learning based semi-automatic segmentation for complex anatomy on MRI](https://www.redjournal.org/article/S0360-3016%2822%2900543-0/fulltext)

[A2-FPN for Semantic Segmentation of Fine-Resolution Remotely Sensed Images
](https://arxiv.org/abs/2102.07997)

[Weight and Biases](https://wandb.ai/site)
