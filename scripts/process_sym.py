''' Post Process of the workers result '''
###
import pandas as pd
import json
import os
###
from urllib.request import urlopen
import matplotlib.pyplot as plt
from visu import *
###

def readBatchResults(batch_file_path):
    data = pd.read_csv(batch_file_path)
    return data[['WorkerId', 'Input.image_url', 'Answer.taskAnswers']]


def stringToAnno(anno_str):
    ''' Convert an annotation string into annotation dictionary '''
    raw_anno = json.loads(anno_str)
    anno = {}
    for class_name, data in raw_anno[0].items():
        anno[class_name] = [float(i) for i in list(data.split(","))]
    
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
    ''' Visualization of the Symmetry Labeling '''
    result = img.copy()
    result = ResizeWithAspectRatio(result, width=800)

    # fig, ax = plt.subplots(figsize=(12,8), dpi=300)
    # ax.imshow(result)
    for class_name, data in anno.items():
        if class_name.split(' ')[0] == 'Rotation': 
            rot_center = (int(data[0]*result.shape[1]), int(data[1]*result.shape[0]))

            result = cv2.circle(result, rot_center, radius= 5, color=(255,255,255), thickness=3)
            result = cv2.circle(result, rot_center, radius= 5, color=(0,0,255), thickness=2)
        elif class_name.split(' ')[0] == 'Reflection': 

            start = (int(data[0]*result.shape[1]), int(data[1]*result.shape[0]))
            end = (int(data[2]*result.shape[1]), int(data[3]*result.shape[0]))

            result = cv2.line(result, start, end, color=(255, 255, 255), thickness= 3)
            result = cv2.line(result, start, end, color=(0, 255, 0), thickness= 2)

    return result



if __name__ == "__main__":
    image_local_dir = 'E:\Lab Work\Human Research\Dataset Collection\Iter-1'

    visu_save_dir = 'E:\Lab Work\Human Research\Dataset Collection\Results\Iter-1-visu'
    os.makedirs(visu_save_dir, exist_ok=True)

    batch_results = readBatchResults        (batch_file_path='D:\Downloads\Batch_4743917_batch_results (1).csv')

    for idx, row in batch_results.iterrows():
        # [worker, image_url, anno_string]
        worker_id = row['WorkerId']
        image_url = row['Input.image_url']
        anno = stringToAnno(row['Answer.taskAnswers'])

        print (worker_id)
        print (image_url)
        
        img_name = os.path.split(image_url)[-1]

        img = cv2.imread(os.path.join(image_local_dir, img_name))
        visu = visuSym(img, anno)

        # save the visualization results
        img_name_noext = os.path.splitext(img_name)[0]
        cv2.imwrite(os.path.join(visu_save_dir ,f'{img_name_noext}_{worker_id}.jpg') ,visu)
