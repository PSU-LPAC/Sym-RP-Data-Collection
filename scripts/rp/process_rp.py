import os
import sys
module_path = os.path.abspath(os.path.join(__file__, '..', '..'))
if module_path not in sys.path:
    sys.path.append(module_path)
    
import json
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
