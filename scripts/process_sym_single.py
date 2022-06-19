''' Process Single Symmetry Labeling Task Results '''
###
import pandas as pd
import json
import os
import ast
###
from urllib.request import urlopen
import matplotlib.pyplot as plt
from sklearn.feature_extraction import img_to_graph
from visu import *
###

def ProcessNew(image_local_dir, save_dir, batch_file_path, batch_name = 'Iter-2', anno_dict = {}):
    ''' Process the batch result .csv file, and save the visualization figures of each individual labeling '''

    anno_save_dir = os.path.join(save_dir, batch_name, 'anno')
    visu_save_dir = os.path.join(save_dir, batch_name, 'visu')
    os.makedirs(anno_save_dir, exist_ok=True)
    os.makedirs(visu_save_dir, exist_ok=True)

    data = pd.read_csv(batch_file_path)

    num_nolabel = 0

    for idx, row in data.iterrows():
        # * skip the Rejected results
        if row['AssignmentStatus'] == 'Rejected':
            continue

        worker_id = row['WorkerId']
        image_url = row['Input.img_url']
        img_name = os.path.split(image_url)[-1]
        img = cv2.imread(os.path.join(image_local_dir, img_name))
        worker_label = convertResult(img, anno_str= row['Answer.taskAnswers'])

        anno = {'WorkerId':worker_id, 'ImageUrl': image_url, 'WorkerLabel':worker_label, 'ImageSize':[img.shape[1], img.shape[0]]}

        idx = 0
        if image_url not in anno_dict:
            anno_dict[image_url] = {}
            anno_dict[image_url][worker_id] = {0:worker_label}
        else:
            if worker_id not in anno_dict[image_url]:
                anno_dict[image_url][worker_id] = {0:worker_label}
            else:
                idx = len(anno_dict[image_url][worker_id])
                anno_dict[image_url][worker_id] = {idx:worker_label}

        print (worker_id)
        print (image_url)
        img_name_noext = os.path.splitext(img_name)[0]

        # save the individual labeling as a json file
        with open(os.path.join(anno_save_dir ,f'{img_name_noext}_{worker_id}_{idx}.json'), 'w') as f:
            json.dump(anno, f, indent=4)

        visu = visuSym(img, worker_label)

        # save the visualization results (together)
        cv2.imwrite(os.path.join(visu_save_dir ,f'{img_name_noext}_{worker_id}_{idx}.jpg') ,visu)

        # save the visualization results (by worker)
        save_path = os.path.join(save_dir, 'worker', worker_id, f'{img_name_noext}_{worker_id}_{idx}.jpg')

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path ,visu)

        # save the visualization results (by image)
        save_path = os.path.join(save_dir, 'image', img_name_noext, f'{img_name_noext}_{worker_id}_{idx}.jpg')

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path ,visu)

   
    print (num_nolabel)

    # save the whole anno_dict for further usage
    with open(os.path.join(save_dir, batch_name, 'all_anno_dict.json'), 'w') as f:
        json.dump(anno_dict, f, indent=4)

    return anno_dict