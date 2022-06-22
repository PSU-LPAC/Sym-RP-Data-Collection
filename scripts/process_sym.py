''' Post Process of the workers result '''
###
import pandas as pd
import json
import os

from util import *
###

def convertResult(img, single_result):
    ''' Convert the result to absolute coordinates based on original image'''
    anno = {}
    
    rot_idx, ref_idx = 0, 0

    if 'coordinates' not in single_result:
        return anno

    label_img_w, label_img_h = single_result['imageSize']
    for label in single_result['coordinates']:
        if label['class'] == 'Rotation': 
            # * 'Rotation ID': (x, y)
         
            rot_center = [int(label['data'][0]/label_img_w*img.shape[1]), int(label['data'][1]/label_img_h*img.shape[0])]
            anno[f'Rotation {rot_idx}'] = rot_center
            rot_idx += 1

        elif label['class'] == 'Reflection': 
            # * 'Reflection ID': (x1, y1, x2, y2)
            ref_ends = [int(label['data'][0][0]/label_img_w*img.shape[1]), int(label['data'][0][1]/label_img_h*img.shape[0]), int(label['data'][1][0]/label_img_w*img.shape[1]), int(label['data'][1][1]/label_img_h*img.shape[0])]
            anno[f'Reflection {ref_idx}'] = ref_ends
            ref_idx += 1

    return anno

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