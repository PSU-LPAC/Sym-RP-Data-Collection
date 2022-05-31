''' Post Process of the workers result '''
###
import pandas as pd
import json
import os
###
from urllib.request import urlopen
import matplotlib.pyplot as plt
from sklearn.feature_extraction import img_to_graph
from visu import *
###

def readBatchResults(batch_file_path):
    data = pd.read_csv(batch_file_path)
    return data[['WorkerId', 'Input.image_url', 'Answer.taskAnswers']]


def convertResult_Iter1(img, anno_str):
    ''' [Iter-1 result] Convert a labeling result string into an annotation dictionary '''
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

def urlToLocalPath(img_dir, img_url):
    ''' Convert the image url to local directory '''
    img_name = os.path.split(img_url)[-1]
    
    return os.path.join(img_dir, img_name)

def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)

def visuSym(img, anno):
    ''' Visualization of the Symmetry Labeling with Roughly the Same Size'''
    img_w, img_h = img.shape[1], img.shape[0] 
    result = img.copy()
    result = ResizeWithAspectRatio(result, width=800)
    new_w, new_h = result.shape[1], result.shape[0] 

    # fig, ax = plt.subplots(figsize=(12,8), dpi=300)
    # ax.imshow(result)
    for class_name, data in anno.items():
        if class_name.split(' ')[0] == 'Rotation': 
            rot_center = (int(data[0]*new_w/img_w), int(data[1]*new_h/img_h))

            result = cv2.circle(result, rot_center, radius= 5, color=(255,255,255), thickness=3)
            result = cv2.circle(result, rot_center, radius= 5, color=(0,0,255), thickness=2)
        elif class_name.split(' ')[0] == 'Reflection': 

            start = (int(data[0]*new_w/img_w), int(data[1]*new_h/img_h))
            end = (int(data[2]*new_w/img_w), int(data[3]*new_h/img_h))

            result = cv2.line(result, start, end, color=(255, 255, 255), thickness= 3)
            result = cv2.line(result, start, end, color=(0, 255, 0), thickness= 2)

    return result



if __name__ == "__main__":

    # * Process the batch result .csv file, and save the visualization figures of each individual labeling

    image_local_dir = 'E:/Lab Work/Human Research/Dataset Collection/Iter-1'

    anno_save_dir = 'E:/Lab Work/Human Research/Dataset Collection/Results/Iter-1/anno'
    visu_save_dir = 'E:/Lab Work/Human Research/Dataset Collection/Results/Iter-1/visu'

    batch_file_path = 'D:/Downloads/Batch_4743917_batch_results (2).csv'
    

    os.makedirs(anno_save_dir, exist_ok=True)
    os.makedirs(visu_save_dir, exist_ok=True)

    batch_results = readBatchResults(batch_file_path)

    anno_dict = {}      # anno_dict stores the annotation based on ImageUrl (as keys)
    num_nolabel = 0
    for idx, row in batch_results.iterrows():
        # [worker, image_url, anno_string]
        worker_id = row['WorkerId']
        image_url = row['Input.image_url']
        img_name = os.path.split(image_url)[-1]
        img = cv2.imread(os.path.join(image_local_dir, img_name))

        worker_label = convertResult_Iter1(img, row['Answer.taskAnswers'])

        if len(worker_label) == 0:
            num_nolabel += 1

        # full annotation: {'WorkerId','ImageUrl', 'WorkerLabel', 'ImageSize':[w,h]}
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

        # save the visualization results
        
        cv2.imwrite(os.path.join(visu_save_dir ,f'{img_name_noext}_{worker_id}_{idx}.jpg') ,visu)

    print (num_nolabel)