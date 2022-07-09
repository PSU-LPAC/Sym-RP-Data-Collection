''' Process Single Symmetry Labeling Task Results '''
#%%
from glob import glob
import pandas as pd
import json
import os
import cv2
###
from process_sym import convertResult, visuResults, mergeAnnos,  addQualification
from util import visuSym
###


def convertLabel1(img, single_result):
    ''' 
        # ![Symmetry Labeling 1 Only] 
        Convert a labeling result string into an annotation dictionary 
    '''

    anno = {}
    for class_name, data in single_result.items():
        float_data = [float(i) for i in list(data.split(","))]
    
        if class_name.split(' ')[0] == 'Rotation': 
            # * 'Rotation ID': (x, y)
            rot_center = [int(float_data[0]*img.shape[1]), int(float_data[1]*img.shape[0])]
            anno[class_name] = rot_center
        elif class_name.split(' ')[0] == 'Reflection': 
            # * 'Reflection ID': (x1, y1, x2, y2)
            ref_ends = [int(float_data[0]*img.shape[1]), int(float_data[1]*img.shape[0]), int(float_data[2]*img.shape[1]), int(float_data[3]*img.shape[0])]
            anno[class_name] = ref_ends
    return anno

def loadBatchResults(batch_file_path, image_local_dir, batch_name = ''):
    ''' 
        Load the batch result .csv file. 
        Output an array contains all individual results
    '''

    data = pd.read_csv(batch_file_path)

    annos = []

    for idx, row in data.iterrows():
        # * skip the Rejected results
        if row['AssignmentStatus'] == 'Rejected':
            continue
        
        if batch_name == 'Symmetry Labeling 1':  
            worker_id = row['WorkerId']          
            img_url = row['Input.image_url']
            img_name = os.path.split(img_url)[-1]
            img_name = f'0{img_name}'       # * 001_xxx -> 0001_xxx
            img = cv2.imread(os.path.join(image_local_dir, img_name))
            worker_label = convertLabel1(img, json.loads(row['Answer.taskAnswers'])[0])
        else:
            worker_id = row['WorkerId']
            img_url = row['Input.img_url']
            img_name = os.path.split(img_url)[-1]
            img = cv2.imread(os.path.join(image_local_dir, img_name))

            single_result = json.loads(row['Answer.taskAnswers'])[0]
            if 'coordinates' not in single_result:
                worker_label = {}
            else:
                single_result['coordinates'] = json.loads(single_result['coordinates'])
                single_result['imageSize'] = json.loads(single_result['imageSize'])

                worker_label = convertResult(img, single_result)

        anno = {
            'WorkerId':worker_id, 
            'ImageUrl': img_url, 
            'ImageName': img_name,
            'WorkerLabel':worker_label, 
            'ImageSize':[img.shape[1], img.shape[0]]
            }
        
        annos.append(anno)

    return annos


    
#%%
if __name__ == "__main__":
    # %%
    # * Path Settings
    image_local_dir='E:/Lab Work/Datasets/Sym-RP-Collection/Images'
    save_folder = 'E:/Lab Work/Datasets/Sym-RP-Collection/Results'
    batch_folder = os.path.join(save_folder, 'Batch Results')
    os.makedirs(batch_folder, exist_ok=True)
    qual_file_path = 'E:/Lab Work/Datasets/Sym-RP-Collection/AWS csv/quals.csv'

    # %%
    # * Symmetry Labeling 1
    batch_name = 'Symmetry Labeling 1'
    batch_file_path='E:/Lab Work/Datasets/Sym-RP-Collection/Results/Raw Batch Results/Symmetry Labeling 1.csv'

    annos = loadBatchResults(batch_file_path, image_local_dir, batch_name)
    
    with open(os.path.join(batch_folder, f'{batch_name}.json'), 'w') as f:
        json.dump(annos, f, indent=4)

    # %%
    # * Symmetry Labeling Iter-2
    batch_name = 'Symmetry Labeling Iter-2'
    batch_file_path='E:/Lab Work/Datasets/Sym-RP-Collection/Results/Raw Batch Results/Symmetry Labeling Iter-2.csv'

    annos = loadBatchResults(batch_file_path, image_local_dir, batch_name)
    
    with open(os.path.join(batch_folder, f'{batch_name}.json'), 'w') as f:
        json.dump(annos, f, indent=4)
    
    # %%
    # * Symmetry Labeling Iter-2-205
    batch_name = 'Symmetry Labeling Iter-2-205'
    batch_file_path='E:/Lab Work/Datasets/Sym-RP-Collection/Results/Raw Batch Results/Symmetry Labeling Iter-2-205.csv'

    annos = loadBatchResults(batch_file_path, image_local_dir, batch_name)
    
    with open(os.path.join(batch_folder, f'{batch_name}.json'), 'w') as f:
        json.dump(annos, f, indent=4)
    
    # %%
    # * Symmetry Labeling Iter-2-205-2
    batch_name = 'Symmetry Labeling Iter-2-205-2'
    batch_file_path='E:/Lab Work/Datasets/Sym-RP-Collection/Results/Raw Batch Results/Symmetry Labeling Iter-2-205-2.csv'

    annos = loadBatchResults(batch_file_path, image_local_dir, batch_name)
    
    with open(os.path.join(batch_folder, f'{batch_name}.json'), 'w') as f:
        json.dump(annos, f, indent=4)


    # %%
    # * Symmetry Labeling Half-1 [In Process]
    batch_name = 'Symmetry Labeling Half-1'
    batch_file_path='E:/Lab Work/Datasets/Sym-RP-Collection/Results/Raw Batch Results/Symmetry Labeling Half-1.csv'

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
    # * Add Qualification
    with open(os.path.join(save_folder, 'merged_annos.json'), 'r') as f:
        merged_annos = json.load(f)
    
    merged_annos = addQualification(merged_annos, pd.read_csv(qual_file_path))
    with open(os.path.join(save_folder, 'merged_annos.json'), 'w') as f:
        json.dump(merged_annos, f, indent=4)

    # %%
    # * Visualize Results
    with open(os.path.join(save_folder, 'merged_annos.json'), 'r') as f:
        annos = json.load(f)
    visuResults(annos, image_local_dir, os.path.join(save_folder, 'visu'))
# %%
