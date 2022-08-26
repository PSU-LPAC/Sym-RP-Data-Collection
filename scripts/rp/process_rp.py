import os
import sys
module_path = os.path.abspath(os.path.join(__file__, '..', '..'))
if module_path not in sys.path:
    sys.path.append(module_path)
    
import json
import cv2
from util import visu_rp

def convert_result(single_result, img_size):
    ''' Convert the result to absolute coordinates based on original image'''
    anno = {}

    if 'coordinates' not in single_result:
        return anno

    label_img_w, label_img_h = single_result['imageSize']
    img_w, img_h = img_size

    rx = img_w / float(label_img_w)
    ry = img_h / float(label_img_h)

    for label in single_result['coordinates']:
        if 'data' not in label or len(label['data']) == 0:
            continue
        rp_class = label['class']

        inst = []
        if label['mode'] == 'bbox':
            if len(label['data']) != 2:
                continue
            lt_x,lt_y = label['data'][0]
            rb_x,rb_y = label['data'][1]

            x, y, w, h = rx*lt_x, ry*lt_y, rx*(rb_x-lt_x), ry*(rb_y-lt_y)

            if w==0 or h==0:
                continue

            # * convert the bbox into polygon format
            inst.append({'x':x, 'y':y})
            inst.append({'x':x+w, 'y':y})
            inst.append({'x':x+w, 'y':y+h})
            inst.append({'x':x, 'y':y+h})

        elif label['mode'] == 'polygon':
            for pt in label['data']:
                if len(pt) != 2:
                    continue
                inst.append({'x':pt[0]*rx, 'y':pt[1]*ry})
        
        if rp_class not in anno:
            anno[rp_class] = []
        anno[rp_class].append(inst)
    
    return anno


def visu_results(annos, image_local_dir, visu_save_dir, iter_flag = False):
    ''' 
        Visualize the individual results and sort by {img_name, worker_id} categories 
    '''
    for single_anno in annos:
        img_name = single_anno['ImageName']  
        worker_id = single_anno['WorkerId']
        if iter_flag:
            iter =  single_anno['Iter']   # iterations of the annotation from the same worker
        else:
            iter = 0
        worker_anno = single_anno['WorkerLabel']

        img = cv2.imread(os.path.join(image_local_dir, img_name))

        visu = visu_rp(img, worker_anno)

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