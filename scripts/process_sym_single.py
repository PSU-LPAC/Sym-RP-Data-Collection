''' Process Single Symmetry Labeling Task Results '''
#%%
from glob import glob
import pandas as pd
import json
import os
import cv2
###
from util import visuSym


def convertAnnoStrLabel1(img, anno_str):
    ''' 
        # ![Symmetry Labeling 1 Only] 
        Convert a labeling result string into an annotation dictionary 
    '''
    raw_anno = json.loads(anno_str)
    anno = {}
    for class_name, data in raw_anno[0].items():
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

def convertAnnoStr(img, anno_str):
    ''' Convert an annotation string into an annotation dictionary '''
    raw_anno = json.loads(anno_str)
    anno = {}
    # res = ast.literal_eval(anno_str)
    # raw_anno = json.dumps(anno_str, separators=(',', ':'))
    if len(raw_anno) == 0:
        return anno
    raw_anno = raw_anno[0]
    if 'coordinates' not in raw_anno:
        return anno
    raw_anno['coordinates'] = json.loads(raw_anno['coordinates'])
    
    rot_idx, ref_idx = 0, 0

    label_img_w, label_img_h = json.loads(raw_anno['imageSize'])
    for label in raw_anno['coordinates']:
        if label['class'] == 'Rotation': 
            # * 'Rotation ID': (x, y)
         
            rot_center = [int(label['data'][0]/label_img_w*img.shape[1]), int(label['data'][1]/label_img_h*img.shape[0])]
            anno[f'Rotation {rot_idx}'] = rot_center
            rot_idx += 1

        elif label['class'] == 'Reflection': 
            # * 'Reflection ID': (x1, y1, x2, y2)
            ref_ends = [int(label['data'][0][0]/label_img_w*img.shape[1]), int(label['data'][0][1]/label_img_h*img.shape[0]), int(label['data'][1][0]/label_img_w*img.shape[1]), int(label['data'][1][1]/label_img_h*img.shape[0])]
            anno[f'Reflection {rot_idx}'] = ref_ends
            ref_idx += 1

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
            worker_label = convertAnnoStrLabel1(img, anno_str= row['Answer.taskAnswers'])
        else:
            worker_id = row['WorkerId']
            img_url = row['Input.img_url']
            img_name = os.path.split(img_url)[-1]
            img = cv2.imread(os.path.join(image_local_dir, img_name))

            worker_label = convertAnnoStr(img, anno_str= row['Answer.taskAnswers'])

        anno = {
            'WorkerId':worker_id, 
            'ImageUrl': img_url, 
            'ImageName': img_name,
            'WorkerLabel':worker_label, 
            'ImageSize':[img.shape[1], img.shape[0]]
            }
        
        annos.append(anno)

    return annos


def mergeAnnos(batch_annos):
    ''' 
        Merge the annotations from different batches
    '''
    merged_annos = []
    iter_dict = {}     # store the iterations of same image labeled by the same worker
    for annos in batch_annos:
        print (f"{len(annos)} annotations")
        for single_anno in annos:
            img_name = single_anno['ImageName']  
            worker_id = single_anno['WorkerId']

            if worker_id not in iter_dict:
                iter_dict[worker_id] = {}
                iter_dict[worker_id][img_name] = 1
            else:
                if img_name not in iter_dict[worker_id]:
                    iter_dict[worker_id][img_name] = 1
                else:
                    iter_dict[worker_id][img_name] += 1
                    # print (worker_id, img_name, iter_dict[worker_id][img_name])

            single_anno['Iter'] = iter_dict[worker_id][img_name]

            merged_annos.append(single_anno.copy())

    print (f"Merged {len(merged_annos)} annotations")
    return merged_annos

def addQualification(annos, quals):
    ''' Add the qualifcaition status of worker for each individual annotation '''
    for anno in annos:
        worker_id = anno['WorkerId']
        worker_ids = quals['WorkerId'].values.tolist()
        if worker_id in worker_ids:
            anno['Qualification'] = 1
        else:
            anno['Qualification'] = 0
    
    return annos



def visuResults(annos, image_local_dir, visu_save_dir):
    ''' 
        Visualize the individual results and sort by {img_name, worker_id} categories 
    '''
    for single_anno in annos:
        img_name = single_anno['ImageName']  
        worker_id = single_anno['WorkerId']
        iter =  single_anno['Iter']   # iterations of the annotation from the same worker
        worker_anno = single_anno['WorkerLabel']

        img = cv2.imread(os.path.join(image_local_dir, img_name))

        visu = visuSym(img, worker_anno)

        img_name_noext = os.path.splitext(img_name)[0]

        visu_img_name = f'{img_name_noext}_{worker_id}_{iter}.jpg'

        # * save together
        save_path = os.path.join(visu_save_dir, 'together', visu_img_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path ,visu)

        # * save by image name 
        save_path = os.path.join(visu_save_dir, 'image', img_name_noext, visu_img_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path ,visu)

        # * save by worker id
        save_path = os.path.join(visu_save_dir, 'worker', worker_id, visu_img_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path ,visu)

    
#%%
if __name__ == "__main__":
    # %%
    # * Path Settings
    image_local_dir='E:/Lab Work/Datasets/Sym-RP-Collection/Images'
    save_folder = 'E:/Lab Work/Datasets/Sym-RP-Collection/Results'
    # %%
    # * Symmetry Labeling Half-1 [In Process]
    batch_name = 'Symmetry Labeling Half-1'
    batch_file_path='E:/Lab Work/Datasets/Sym-RP-Collection/Results/Raw Batch Results/Symmetry Labeling Half-1.csv'

    annos = loadBatchResults(batch_file_path, image_local_dir, batch_name)
    with open(os.path.join(save_folder, f'{batch_name}.json'), 'w') as f:
        json.dump(annos, f, indent=4)

    # %%
    # * Merge Annotations
    all_annos = []
    for anno_file in glob(os.path.join(save_folder, 'Batch Results', '*.json')):
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
    qual_file_path = 'E:/Lab Work/Datasets/Sym-RP-Collection/AWS csv/quals.csv'
    merged_annos = addQualification(merged_annos, pd.read_csv(qual_file_path))
    with open(os.path.join(save_folder, 'merged_annos.json'), 'w') as f:
        json.dump(merged_annos, f, indent=4)

    # %%
    # * Visualize Results
    with open(os.path.join(save_folder, 'merged_annos.json'), 'r') as f:
        annos = json.load(f)
    visuResults(annos, image_local_dir, os.path.join(save_folder, 'visu'))