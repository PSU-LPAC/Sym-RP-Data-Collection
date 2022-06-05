''' Some scripts for dataset '''
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


    

    get_csv_list(
        img_dir = 'E:/Lab Work/Datasets/Sym-RP-Collection/Rename', 
        csv_path = "E:/Lab Work/Datasets/Sym-RP-Collection/Iter-2.csv",
        url_root_dir='https://s3.amazonaws.com/sym-rp-data-collection/Dataset/Iter-2/'
        )
        
    