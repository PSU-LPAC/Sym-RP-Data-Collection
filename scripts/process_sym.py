''' Post Process of the workers result '''
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

def convertResult(img, anno_str):
    ''' Convert a labeling result string into an annotation dictionary '''
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

def ProcessOld(image_local_dir, save_dir, batch_file_path, batch_name = 'Iter-1', anno_dict = {}):
    ''' Process the batch result .csv file, and save the visualization figures of each individual labeling '''

    anno_save_dir = os.path.join(save_dir, batch_name, 'anno')
    visu_save_dir = os.path.join(save_dir, batch_name, 'visu')
    os.makedirs(anno_save_dir, exist_ok=True)
    os.makedirs(visu_save_dir, exist_ok=True)

    data = pd.read_csv(batch_file_path)

    num_nolabel = 0
    for idx, row in data.iterrows():
        # [worker, image_url, anno_string]
        # * skip the Rejected results
        if row['AssignmentStatus'] == 'Rejected':
            continue

        worker_id = row['WorkerId']
        image_url = row['Input.image_url']
        img_name = os.path.split(image_url)[-1]
        img_name = f'0{img_name}'
        
        img = cv2.imread(os.path.join(image_local_dir, img_name))

        worker_label = convertResult_Iter1(img, row['Answer.taskAnswers'])

        if len(worker_label) == 0:
            num_nolabel += 1

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


def Test():
    img = cv2.imread('E:/Lab Work/Human Research/Dataset Collection/Iter-1/000-201.jpg')
    data = pd.read_csv('D:/Downloads/testResult.csv')
    # convertResult(img, anno_str= '[{"coordinates": "[{\"class\":\"Rotation\",\"mode\":\"dot\",\"data\":[477,272]},{\"class\":\"Rotation\",\"mode\":\"dot\",\"data\":[515,279]}]", "imageSize": "[731, 485]"}]')

    for idx, row in data.iterrows():

        anno = convertResult(img, anno_str= row['Answer.taskAnswers'])

        visu = visuSym(img, anno)
        cv2.imwrite('test.jpg', visu)

if __name__ == "__main__":

    # Test()

    # anno_dict = ProcessOld(
    #     image_local_dir = 'E:/Lab Work/Datasets/Sym-RP-Collection/Images', 
    #     save_dir = 'E:/Lab Work/Datasets/Sym-RP-Collection/Results', 
    #     batch_file_path = 'D:/Downloads/Batch_4743917_batch_results (2).csv',
    #     batch_name = 'Iter-1',
    #     anno_dict = {}
    # )

    # anno_dict = ProcessNew(
    #     image_local_dir = 'E:/Lab Work/Datasets/Sym-RP-Collection/Images', 
    #     save_dir = 'E:/Lab Work/Datasets/Sym-RP-Collection/Results', 
    #     batch_file_path = 'D:/Downloads/Batch_4754060_batch_results.csv',
    #     batch_name = 'Iter-2-1',
    #     anno_dict = anno_dict
    # )

    with open('E:/Lab Work/Datasets/Sym-RP-Collection/Results/Iter-2-1/all_anno_dict.json', 'r') as f:
        anno_dict = json.load(f)

    anno_dict = ProcessNew(
        image_local_dir = 'E:/Lab Work/Datasets/Sym-RP-Collection/Images', 
        save_dir = 'E:/Lab Work/Datasets/Sym-RP-Collection/Results', 
        batch_file_path = 'D:/Downloads/Batch_4754201_batch_results (2).csv',
        batch_name = 'Iter-2-2-half',
        anno_dict = anno_dict
    )

    



    