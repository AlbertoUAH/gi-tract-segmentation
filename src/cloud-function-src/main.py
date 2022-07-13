# -- Production code for masks predictions
# -- Author: Fernandez Hernandez, Alberto
# -- Date: 2022 - 07 - 10

# -- Libraries
import torch
from google.cloud import storage
import segmentation_models_pytorch as smp
import albumentations as A
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib        as mpl
import matplotlib.pyplot as plt
import numpy as np
import pydicom
import glob
import os
import gc
import cv2


IMG_SIZE = (256, 256)
data_transforms = {
    "test": A.Compose([
        A.CenterCrop(height=round(IMG_SIZE[0] * 0.85), width=round(IMG_SIZE[1] * 0.85)),
        A.Resize(*IMG_SIZE, interpolation=cv2.INTER_NEAREST)
    ], p=1.0)
}

# -- Utils class
class TractImageDataset(torch.utils.data.Dataset):
    def __init__(self, list_paths):
        self.list_paths = list_paths
        
    def __len__(self):
        return len(self.list_paths)
    
    def __load_img(self, path):
        img = pydicom.dcmread(path, force=True).pixel_array
        img = img.astype('float32') # original is uint16
        return cv2.resize(img, IMG_SIZE)

    def __getitem__(self, index):
        img_paths = self.list_paths[index]
        imgs = np.zeros((*IMG_SIZE, 3), dtype=np.uint16)
        index_list = [index, index + 1, index + 2]
        if index == len(self.list_paths) - 1:
            index_list = [index] * 3
        elif index == len(self.list_paths) - 2:
            index_list = [index] + [index + 1] * 2
        for i, index_ in enumerate(index_list):
            img = self.__load_img(self.list_paths[index_])
            imgs[..., i] = data_transforms['test'](image=img)['image']
        imgs = imgs / np.max(imgs, axis=(0,1))
        imgs = np.transpose(imgs, (2, 0, 1))
        return torch.FloatTensor(imgs)
    
def save_mask(or_img, pred_mask, image_index, output_bucket):
    or_img = torch.moveaxis(torch.squeeze(or_img), 0, -1)
    fig   = plt.figure(figsize=(10, 5))
    gs    = gridspec.GridSpec(nrows=1, ncols=1)
    
    colors1 = ['yellow']
    colors2 = ['green']
    colors3 = ['red']

    cmap1 = mpl.colors.ListedColormap(colors1)
    cmap2 = mpl.colors.ListedColormap(colors2)
    cmap3 = mpl.colors.ListedColormap(colors3)

    ax0 = fig.add_subplot(gs[0, 0])
    ax0.set_title("Predicted mask slice {}".format(image_index), fontsize=15, weight='bold', y=1.02)

    l0 = ax0.imshow(or_img[...,0], cmap='bone')
    l1 = ax0.imshow(np.ma.masked_where(pred_mask[0,...]== 0,  pred_mask[0,...]),cmap=cmap1)
    l2 = ax0.imshow(np.ma.masked_where(pred_mask[1,...]== 0,  pred_mask[1,...]),cmap=cmap2)
    l3 = ax0.imshow(np.ma.masked_where(pred_mask[2,...]== 0,  pred_mask[2,...]),cmap=cmap3)

    _ = [ax.set_axis_off() for ax in [ax0]]

    colors = [im.cmap(im.norm(1)) for im in [l1,l2, l3]]
    labels = ["Large Bowel", "Small Bowel", "Stomach"]
    patches = [ mpatches.Patch(color=colors[i], label=f"{labels[i]}") for i in range(len(labels))]

    plt.legend(handles=patches, bbox_to_anchor=(1.1, 0.65), loc=2, borderaxespad=0.4,fontsize = 14,
               title='Mask Labels', title_fontsize=14, edgecolor="black",  facecolor='#c5c6c7')
    plt.suptitle("", fontsize=20, weight='bold')
    output_filename = "/tmp/slice_{1:0{0}}.jpg" .format(5,image_index)
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    blob = output_bucket.blob(f'pred_slice_{image_index:05d}.jpg')
    blob.upload_from_filename(output_filename)
    os.remove(output_filename)
    plt.close(fig)

def pred_masks(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    patient_id = request_json['patient_id']
    client = storage.Client()
    bucket = client.get_bucket('gi-tract-segmentation-bucket')
    blobs = bucket.list_blobs(prefix='input_data/' + patient_id + '/', delimiter='/')
    blobs = [blob.download_to_filename(f"/tmp/dicom_{i:05d}.dcm") for i, blob in enumerate(blobs)]

    # -- Load model
    # load model
    model_path = "/tmp/model.pth"
    blobs = bucket.list_blobs(prefix='models/', delimiter='/')
    blobs = [blob.download_to_filename(model_path) for blob in blobs]
    del blobs
    gc.collect()

    # -- Load model
    model = torch.load(model_path, map_location='cpu')
    model.eval()

    def predict(img):
        with torch.no_grad():
            pred = torch.round(torch.sigmoid(model(img)))
        return pred

    # -- Data loader
    files_list = glob.glob('/tmp/*.dcm')
    files_list.sort()
    test_dataset = TractImageDataset(files_list)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1, shuffle=False, drop_last=False)

    # -- Test loop
    output_bucket = client.get_bucket('gi-tract-segmentation-bucket-output-masks')
    stats_dict = dict()
    image_index = 1
    for img in test_loader:
        pred = list(predict(img))[0]

        large_bowel = (int(torch.sum(pred[0])) / (IMG_SIZE[0] * IMG_SIZE[1])) * 100
        small_bowel = (int(torch.sum(pred[1])) / (IMG_SIZE[0] * IMG_SIZE[1])) * 100
        stomach     = (int(torch.sum(pred[2])) / (IMG_SIZE[0] * IMG_SIZE[1])) * 100
        stats_dict[str(image_index)] = [large_bowel, small_bowel, stomach]
        
        save_mask(img, pred, image_index, output_bucket)
        image_index += 1
        gc.collect()
    return stats_dict
