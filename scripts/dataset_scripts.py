''' Some scripts for dataset '''
import json
import os, glob, csv, shutil

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

def get_csv_batch_list(img_dir, csv_path, url_root_dir = '', img_num = 0, duplicate = 0):
    ''' [Batch Hits] Generate Image List from a folder (as a csv format)'''
    img_urls = []
    for idx, img_name in enumerate(os.listdir(img_dir)):
        if (img_num != 0 and idx >= img_num):
            break
        img_urls.append(url_root_dir + img_name)    
    # add duplicate images for self-validation
    for idx, img_name in enumerate(os.listdir(img_dir)):
        if (idx >= duplicate):
            break
        img_urls.append(url_root_dir + img_name)    
    

    json_img_urls = json.dumps(img_urls, separators=(',', ':'))
    print (json_img_urls)

    # writing to csv file 
    with open(csv_path, 'w', newline='') as f: 
        # creating a csv writer object 
        writer = csv.writer(f) 

        writer.writerow(['img_urls'])    
        writer.writerow([json_img_urls])


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

if __name__ == "__main__":
    # add_index(
    #     img_dir = 'E:/Lab Work/Datasets/Sym-RP-Collection/NRT Images/symmetry', 
    #     new_img_dir = 'E:/Lab Work/Datasets/Sym-RP-Collection/Rename-new', 
    #     start_index= 625
    #     )


    

    # get_csv_list(
    #     img_dir = 'E:/Lab Work/Datasets/Sym-RP-Collection/Rename', 
    #     csv_path = "E:/Lab Work/Datasets/Sym-RP-Collection/Iter-2.csv",
    #     url_root_dir='https://s3.amazonaws.com/sym-rp-data-collection/Dataset/Iter-2/'
    #     )
    
    get_csv_batch_list(
        img_dir = 'E:/Lab Work/Datasets/Sym-RP-Collection/Images', 
        csv_path = "E:/Lab Work/Datasets/Sym-RP-Collection/Batch-Iter-1.csv",
        url_root_dir = 'https://s3.amazonaws.com/sym-rp-data-collection/Dataset/Iter-2/',
        img_num = 10,
        duplicate= 0
    )
        
    