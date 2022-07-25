''' Some scripts for dataset '''
#%%
import json
import os, glob, csv, shutil, cv2

def get_csv_list(img_dir, csv_path, url_root_dir = ''):
    ''' Generate Image List from a folder (as a csv format) '''

    # writing to csv file 
    with open(csv_path, 'w', newline='') as f: 
        # creating a csv writer object 
        writer = csv.writer(f) 
        # writer.writerow(['image_url', 'index'])
        writer.writerow(['img_url'])    
        # writing the data rows 
        # rows = [[root_dir + img_name, idx] for idx, img_name in enumerate(os.listdir(img_dir)) ]

        rows = [[url_root_dir + img_name] for idx, img_name in enumerate(os.listdir(img_dir)) ]
        print(rows)
        writer.writerows(rows)

def get_csv_batch_list(img_dir, csv_path, url_root_dir = '', start_idx = 0,img_num = 0, duplicate = 0, basic_reward_rate = 0.5, per_reward = 0.12, time_range = [30,60]):
    ''' [Batch Hits] Generate Image List from a folder (as a csv format)'''
    img_urls = []
    for idx, img_name in enumerate(os.listdir(img_dir)[start_idx:]):
        if (img_num != 0 and idx >= img_num):
            break
        img_urls.append(url_root_dir + img_name)    
    # add duplicate images for self-validation
    for idx, img_name in enumerate(os.listdir(img_dir)[start_idx:]):
        if (idx >= duplicate):
            break
        img_urls.append(url_root_dir + img_name)    
    

    json_img_urls = json.dumps(img_urls, separators=(',', ':'))
    print (json_img_urls)

    # writing to csv file 
    with open(csv_path, 'w', newline='') as f: 
        # creating a csv writer object 
        writer = csv.writer(f) 

        writer.writerow(['img_urls', 'basic_reward_rate', 'per_reward', 'time_range'])    
        writer.writerow([json_img_urls, basic_reward_rate, per_reward, time_range])


def add_index(img_dir, new_img_dir, start_index = 0):
    ''' rename the images with index'''
    os.makedirs(new_img_dir, exist_ok=True)
    for i, img_name in enumerate(os.listdir(img_dir)):
        new_name = f'{start_index+i:04d}-{img_name}'
        shutil.copy(os.path.join(img_dir, img_name), os.path.join(new_img_dir, new_name))

def update_index(img_dir, new_img_dir):
    ''' rename the image with updated index (from 000 to 0000) '''
    os.makedirs(new_img_dir, exist_ok=True)
    for i, img_name in enumerate(os.listdir(img_dir)):
        new_name = f'0{img_name}'
        shutil.copy(os.path.join(img_dir, img_name), os.path.join(new_img_dir, new_name))


def get_img_size_json(img_dir, save_path):
    ''' Store the image size in json format '''
    result = {}
    
    for img_path in glob.glob(os.path.join(img_dir, '*.*')):
        img = cv2.imread(img_path)
        if img is not None:
            img_name = os.path.split(img_path)[-1]
            img_w, img_h = img.shape[1], img.shape[0]
            result[img_name] = [img_w, img_h ]
    
    with open(save_path, 'w') as f:
        json.dump(result, f, indent=4)

#%%
''' COCO-sym '''
for i in range(10):
    num_imgs = 50
    start_idx = i*num_imgs
    save_dir = "E:/Lab Work/Datasets/Sym-RP-Collection/AWS csv/sym-batch/coco"
    get_csv_batch_list(
        img_dir = 'D:/Dropbox/SymNet_journal_initial_submission/results_images/Reflection/im', 
        csv_path = os.path.join(save_dir, f' COCO Symmetry Labeling Iter {i+1} ({start_idx}-{start_idx+num_imgs-1}).csv'),
        url_root_dir = 'https://s3.amazonaws.com/sym-rp-data-collection/Dataset/COCO-sym/',
        start_idx = start_idx,
        img_num = 50,
        duplicate = 5,
        basic_reward_rate = 0.5,
        per_reward = 0.12,
        time_range = [30,60] 
    )

#%%
''' COCO-sym Img Size'''
get_img_size_json(img_dir = 'D:/Dropbox/SymNet_journal_initial_submission/results_images/Reflection/im', save_path= 'E:/Lab Work/Datasets/Sym-RP-Collection/coco_img_size.json')

#%%
get_img_size_json(img_dir = 'E:/Lab Work/Datasets/Sym-RP-Collection/Images', save_path= 'E:/Lab Work/Datasets/Sym-RP-Collection/img_size.json')

    # for i in range(10):
    #     num_imgs = 50
    #     start_idx = i*num_imgs
    #     save_dir = "E:/Lab Work/Datasets/Sym-RP-Collection/AWS csv/sym-batch"
    #     get_csv_batch_list(
    #         img_dir = 'E:/Lab Work/Datasets/Sym-RP-Collection/Images', 
    #         csv_path = os.path.join(save_dir, f' Batch Symmetry Labeling Iter {i+1} ({start_idx}-{start_idx+num_imgs-1}).csv'),
    #         url_root_dir = 'https://s3.amazonaws.com/sym-rp-data-collection/Dataset/Iter-2/',
    #         start_idx = start_idx,
    #         img_num = 50,
    #         duplicate = 5,
    #         basic_reward_rate = 0.5,
    #         per_reward = 0.12,
    #         time_range = [30,60] 
    #     )
    