''' Process Batch Symmetry Labeling Task Results '''
#%%
from glob import glob
import pandas as pd
import json
import os
import cv2
###
from process_sym import convertResult, visuResults, mergeAnnos
from util import visuSym
###

def loadBatchResults(batch_file_path, image_local_dir, batch_name = ''):
    ''' 
        Load the batch result .csv file. 
        Output an array contains all individual results
    '''

    data = pd.read_csv(batch_file_path)

    annos = []
    suggestions = []

    for idx, row in data.iterrows():
        # * skip the Rejected results
        if row['AssignmentStatus'] == 'Rejected':
            continue
        
        worker_id = row['WorkerId']
        img_urls = json.loads(row['Input.img_urls'])
        answers = json.loads(row['Answer.taskAnswers'])[0]
        batch_results = json.loads(answers['annos'])
        suggestion = answers['suggestions']


        for img_url, single_result in zip (img_urls, batch_results):
            img_name = os.path.split(img_url)[-1]
            img = cv2.imread(os.path.join(image_local_dir, img_name))

            worker_label = convertResult(img, single_result)

            anno = {
                'WorkerId':worker_id, 
                'ImageUrl': img_url, 
                'ImageName': img_name,
                'WorkerLabel':worker_label, 
                'ImageSize':[img.shape[1], img.shape[0]]
                }
        
            annos.append(anno)

        suggestions.append({'WorkerId':worker_id, 'Suggestion': suggestion})

    return annos


    
# %%
if __name__ == "__main__":
    # * Path Settings
    image_local_dir='E:/Lab Work/Datasets/Sym-RP-Collection/Images'
    save_folder = 'E:/Lab Work/Datasets/Sym-RP-Collection/Results/Test'
    batch_folder = os.path.join(save_folder, 'Batch Results')
    os.makedirs(batch_folder, exist_ok=True)

    # %%
    # * Batch Test
    batch_name = 'Test_Batch'
    batch_file_path='D:\Downloads\Batch_358008_batch_results.csv'

    annos = loadBatchResults(batch_file_path, image_local_dir, batch_name)
    with open(os.path.join(batch_folder, f'{batch_name}.json'), 'w') as f:
        json.dump(annos, f, indent=4)

    # %%
    # * Merge Annotations
    all_annos = []
    for anno_file in glob(os.path.join(batch_folder, '*.json')):
        with open(anno_file, 'r') as f:
            annos = json.load(f)
            all_annos.append(annos)

    merged_annos = mergeAnnos(all_annos)
    with open(os.path.join(save_folder, 'merged_annos.json'), 'w') as f:
        json.dump(merged_annos, f, indent=4)

    # %%
    # * Visualize Results
    with open(os.path.join(save_folder, f'merged_annos.json'), 'r') as f:
        annos = json.load(f)
    visuResults(annos, image_local_dir, os.path.join(save_folder, 'visu'))

    # %%
