# -- Streamlit application
# -- Author: Fernandez Hernandez, Alberto
# -- Date: 2022 - 07 - 14

# -- Libraries
from PIL                       import Image
from pprint                    import pprint
from google.cloud              import storage
from PyPDF2                    import PdfWriter, PdfReader
import matplotlib.gridspec     as gridspec
import matplotlib.patches      as mpatches
import matplotlib              as mpl
import matplotlib.pyplot       as plt
import pandas                  as pd
import numpy                   as np
import streamlit               as st
import google.auth.transport.requests
import google.oauth2.id_token
import requests
import base64
import json
import glob
import os
import io

# -- Application setup
st.title("Organs segmentation app ⚕️")
patient_id = st.text_input('Type patient id')
pdf_button = st.button('Generate PDF')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'plasma-crossbar-352308-52d3e97b8152.json'

client = storage.Client()
bucket_name = 'gi-tract-segmentation-bucket-output-masks'
show_masks = False

# -- API call (POST request)
def request_pred_masks(audience='https://europe-west1-plasma-crossbar-352308.cloudfunctions.net/get-masks', patient_id='sample'):
  request = google.auth.transport.requests.Request()
  TOKEN = google.oauth2.id_token.fetch_id_token(request, audience)

  r = requests.post(
      audience,
      headers={'Authorization': f"Bearer {TOKEN}", "Content-Type": "application/json"},
      data=json.dumps({"patient_id": "sample"})  # possible request parameters
  )
  return r

# -- Get mask statistics (area percentage by label)
def get_mask_stats(r):
  # -- Create stats DataFrame
  stats_dict_df = pd.DataFrame.from_dict(json.loads(r.content))
  stats_dict_df.index = ['Large bowel', 'Small bowel', 'Stomach']
  stats_dict_df = stats_dict_df.T
  stats_dict_df.reset_index(inplace=True)
  stats_dict_df['index'] = stats_dict_df['index'].apply(lambda x: x.zfill(5))
  stats_dict_df = stats_dict_df.sort_values('index')
  stats_dict_df_bool = stats_dict_df.copy()
  stats_dict_df_bool[['Large bowel', 'Small bowel', 'Stomach']] = stats_dict_df[['Large bowel', 'Small bowel', 'Stomach']]\
                                                                    .apply(lambda x: ["Yes" if x_aux else "No" for x_aux in x])
  stats_dict_df_bool.rename(columns={'index': 'Slice'}, inplace=True)

  # -- Generate table with masks boolean
  plt.figure()
  colors = []
  for _, row in stats_dict_df_bool.iterrows():
      colors_in_column = ["white", "deepskyblue", "lightgreen", "orange"]
      if row["Large bowel"] == "Yes":
          colors_in_column[1] = "green"
      else:
          colors_in_column[1] = "red"
      if row["Small bowel"] == "Yes":
          colors_in_column[2] = "green"
      else:
          colors_in_column[2] = "red"
      if row["Stomach"] == "Yes":
          colors_in_column[3] = "green"
      else:
          colors_in_column[3] = "red"
      colors.append(colors_in_column)

  cell_text = []
  for row in range(len(stats_dict_df_bool)):
      cell_text.append(stats_dict_df_bool.iloc[row])

  fig, ax = plt.subplots()
  ax.axis('tight')
  ax.axis('off')
  the_table = ax.table(cellText=cell_text,
                       colLabels=stats_dict_df_bool.columns,loc='center', cellColours=colors)
  plt.savefig(f"./tmp/table.jpg", dpi=300, bbox_inches='tight')
  plt.close(fig)

  # -- Percentage areas plot
  fig, (ax1, ax2, ax3) = plt.subplots(3,1,figsize=(12,18))
  plt.style.use('ggplot')
  stats_dict_df[stats_dict_df['Large bowel'] != 0]['Large bowel'].plot(kind='bar', ax=ax1, color='deepskyblue')
  stats_dict_df[stats_dict_df['Small bowel'] != 0]['Small bowel'].plot(kind='bar', ax=ax2, color='green')
  stats_dict_df[stats_dict_df['Stomach'] != 0]['Stomach'].plot(kind='bar', ax=ax3, color='orange')
  ax1.set_title('Large bowel')
  ax2.set_title('Small bowel')
  ax3.set_title('Stomach')
  ax1.grid(False)
  ax2.grid(False)
  ax3.grid(False)
  fig.add_subplot(111, frameon=False)
  # hide tick and tick label of the big axis
  plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)
  plt.title('AREA PERCENTAGE BY LABEL\n\n')
  plt.xlabel("\nSlices")
  plt.ylabel("Percentage area (%)")
  plt.grid(False)
  plt.savefig(f"./tmp/percentage_areas.jpg", dpi=300)
  plt.close(fig)


# -- Get output bucket from Google Cloud Storage
def get_bucket(bucket_name):
  bucket = client.get_bucket(bucket_name)
  blobs  = bucket.list_blobs(delimiter='/')
  blobs  = [blob.download_to_filename(f"./tmp/dicom_{i:05d}.jpg") for i, blob in enumerate(blobs)]

# -- Functions to generate PDF report (I)
def remove_dup_page(images_list, pdf_path):
  pages_to_keep = list(range(len(images_list)))[1:] # page numbering starts from 0
  infile = PdfReader(pdf_path, 'rb')
  output = PdfWriter()

  for i in pages_to_keep:
      p = infile.pages[i]
      output.add_page(p)

  with open(pdf_path, 'wb') as f:
      output.write(f)

# -- Functions to generate PDF report (II)
def create_pdf(folder_output_path):
  get_bucket('gi-tract-segmentation-bucket-output-masks')
  images_list =  glob.glob(folder_output_path)
  images_list.sort()
  images_list = ["./tmp/portrait.jpg", "./tmp/table.jpg", "./tmp/percentage_areas.jpg"] + images_list

  images = [
      Image.open(f).convert('RGB')
      for f in images_list
  ]
  images[0] = images[0].resize((1700,2500))
  pdf_path = "report.pdf"

  images[0].save(
      pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images
  )
  remove_dup_page(images_list, pdf_path)

# -- Main
if __name__ == "__main__":
  if (patient_id and pdf_button):
    with st.spinner('Generating images masks, please wait. It may take several minutes...'):
      r = request_pred_masks()
      get_mask_stats(r)
      create_pdf(folder_output_path='./tmp/dicom*.jpg')
      file = 'report.pdf'
      with open(file, "rb") as pdf_file:
        PDFbyte = pdf_file.read()
        st.success('Report generated successfully')
        st.download_button(label="Download Report",
                            data=PDFbyte,
                            file_name="report.pdf",
                            mime='application/octet-stream')
    show_masks = True

  files = glob.glob('./tmp/dicom*.jpg')
  if files:
    files.sort()
    number = st.slider("Pick a number", 0, len(files))
    image = Image.open(files[number])
    st.image(image)



