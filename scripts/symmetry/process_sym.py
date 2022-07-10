import os
import sys
module_path = os.path.abspath(os.path.join(__file__, '..', '..'))
if module_path not in sys.path:
    sys.path.append(module_path)
###
from util import *
###



def convert_result(single_result, img_size):
    ''' Convert the result to absolute coordinates based on original image'''
    anno = {}
    
    rot_idx, ref_idx = 0, 0
    if 'coordinates' not in single_result:
        return anno

    label_img_w, label_img_h = single_result['imageSize']
    img_w, img_h = img_size
    for label in single_result['coordinates']:
        if 'data' not in label or len(label['data']) == 0:
            continue
        if label['class'] == 'Rotation': 
            # * 'Rotation ID': (x, y)
            if len(label['data']) != 2:
                continue
         
            rot_center = [int(label['data'][0]/label_img_w*img_w), int(label['data'][1]/label_img_h*img_h)]
            anno[f'Rotation {rot_idx}'] = rot_center
            rot_idx += 1

        elif label['class'] == 'Reflection': 
            # * 'Reflection ID': (x1, y1, x2, y2)
            if len(label['data']) != 2:
                continue
            if len(label['data'][0]) != 2 or len(label['data'][1]) != 2:
                continue
            ref_ends = [int(label['data'][0][0]/label_img_w*img_w), int(label['data'][0][1]/label_img_h*img_h), int(label['data'][1][0]/label_img_w*img_w), int(label['data'][1][1]/label_img_h*img_h)]
            anno[f'Reflection {ref_idx}'] = ref_ends
            ref_idx += 1

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

        visu = visu_sym(img, worker_anno)

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


def merge_annos(batch_annos):
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

def process_batch(worker_answer, imgs_size, batch_name = '', quals = None):
    ''' 
        Process the batch answer containing an individual worker label of multiple images. 
    '''
    
    for img_size, single_result in zip (imgs_size, worker_answer):
        worker_label = convert_result(single_result, img_size)



def approve_and_bonus(client, workers_status, num_imgs = 55, basic_reward = 3.3, per_reward = 0.12, in_production = False):
    approve_feedback = 'We will post more symmetry labeling tasks. We sincerely invite you to the coming tasks.'
    survey_request = "Would you take 5 minutes to complete a background survey? The survey doesn't contain any personally identifying information. Here is the link: https://forms.gle/eAjfV8w85ZbA83gR7"

    

    for worker_id in workers_status:
        assignment_id = workers_status[worker_id]['assignment_id']
        num_label = workers_status[worker_id]['num_label']
        qualified = workers_status[worker_id]['qualified']

        bonus_reward =  max(0, per_reward * num_label -  basic_reward)

        token = f'{worker_id}-{assignment_id}-{bonus_reward}'

        feedback = approve_feedback if qualified else survey_request

        if workers_status[worker_id]['approved']:
            # * Approve
            try:
                if in_production:
                    response = client.approve_assignment(
                        AssignmentId=assignment_id,
                        RequesterFeedback=feedback,
                        OverrideRejection=True
                    )
                    print (f'Approve: {worker_id}')
                else:
                    print (f'[Will] approve: {worker_id}')
            except:
                print (f'Cannot Approve: {worker_id}')
            # * Bonus
            try:
                if worker_id == 'AS0EC2HIE974S' and assignment_id == '358010RM5QPFU84XRTNF2MKSH9WVXK':
                    continue

                if in_production:
                    response = client.send_bonus(
                        WorkerId= worker_id,
                        BonusAmount=f'{bonus_reward:.2f}',
                        AssignmentId=assignment_id,
                        Reason=f'Labeled {num_label} images',
                        UniqueRequestToken=token
                    )
                    print (f'Bonus: {worker_id} with {bonus_reward:.2f}')
                else:
                    print (f'[Will] bonus: {worker_id} with {bonus_reward:.2f}')
            except:
                print (f'Cannot Bonus: {worker_id} with {bonus_reward:.2f}')
