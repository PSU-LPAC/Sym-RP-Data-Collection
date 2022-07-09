''' Script for Batch Result Process '''
#%%
import os, json
import pandas as pd
import xmltodict
from process_sym_batch import setup_mturk, approve_and_bonus, loadBatchResults
from process_sym import visu_results

# * Path Settings
image_local_dir='E:/Lab Work/Datasets/Sym-RP-Collection/Images'
qual_file_path = 'E:/Lab Work/Datasets/Sym-RP-Collection/AWS csv/quals.csv'
with open ('E:\Lab Work\Datasets\Sym-RP-Collection\img_size.json', 'r') as f:
    imgs_size = json.load(f)

batch_list = [
    'Batch Symmetry Labeling Iter 1 (0-49)',
    'Batch Symmetry Labeling Iter 2 (50-99)',
    'Batch Symmetry Labeling Iter 3 (100-149)',
    'Batch Symmetry Labeling Iter 4 (150-199)',
    'Batch Symmetry Labeling Iter 5 (200-249)',
    'Batch Symmetry Labeling Iter 6 (250-299)',
    'Batch Symmetry Labeling Iter 7 (300-349)',
    'Batch Symmetry Labeling Iter 8 (350-399)',
    'Batch Symmetry Labeling Iter 9 (400-449)',
    'Batch Symmetry Labeling Iter 10 (450-499)',
]

HITIds = [
    '3S37Y8CWJJWYOBIZ7QL43TBJZTU4WN',
    '3HO4MYYR2DKZBUX8VEZII3A0A5A6UY',
    '3SZYX62S6RW1UFLYDNW2G5IG60357I',
    '388CL5C1SUJCPTUVIJYLO7376TZHLK',
    '3D06DR523GFHLO42CPP87YVST3ZAM4',
    '36V4Q8R5ZWWCVO9CRNRWLI5MUXSMQX'
]

batch_folder = 'E:\Lab Work\Datasets\Sym-RP-Collection\Results\Batch'

#%%
# * Setup MTurk
client = setup_mturk(True)

print('AvailableBalance:', client.get_account_balance()['AvailableBalance'])

#%%
# * Process Each Batch
visu_flag = False
# process_assignment_type = 'Approved'
process_assignment_type = 'Submitted'
batch_workers_status = []
for batch_name in batch_list:
    print (batch_name)
    # * Get the assignments
    # response = client.list_assignments_for_hit(
    #     HITId=HITId,
    #     AssignmentStatuses=['Submitted']
    # )

    # assignments = response['Assignments']
    # for assignment in assignments:
    #     answer_dict = xmltodict.parse(assignment['Answer'])
    #     answer = answer_dict['QuestionFormAnswers']['Answer']['FreeText']
    #     print (answer)

    batch_file_path = os.path.join(batch_folder, 'MTurk Results',f'{batch_name}.csv')
    if not os.path.isfile(batch_file_path):
        print (f"File {batch_file_path} doesn't exist!")
        continue

    annos, suggestions, workers_status = loadBatchResults(
        batch_file_path, imgs_size, batch_name, 
        pd.read_csv(qual_file_path), process_assignment_type)

    os.makedirs(os.path.join(batch_folder, batch_name), exist_ok=True)
    with open(os.path.join(batch_folder, batch_name, f'{batch_name}.json'), 'w') as f:
        json.dump(annos, f, indent=4)

    print (suggestions)
    batch_workers_status.append(workers_status)

    if visu_flag:
        # visualize
        visu_results(annos, image_local_dir, os.path.join(batch_folder, batch_name, 'visu')) 
print ('-------------------------------')
print (batch_workers_status)

#%%
# * Approve and Bonus
in_production = True
for workers_status in batch_workers_status:
    approve_and_bonus(client, workers_status, in_production=in_production)

print('New AvailableBalance:', client.get_account_balance()['AvailableBalance'])

# %%
# * Get statistic
import numpy as np 

all_annos = []
for batch_name in batch_list:
    with open(os.path.join(batch_folder, batch_name, f'{batch_name}.json'), 'r') as f:
        annos = json.load(f)
        all_annos.extend(annos)

print ('All annotations:', len(all_annos))

worker_dict = {}
img_dict = {}
for anno in all_annos:
    worker_id = anno['WorkerId']
    img_name = anno['ImageName']
    
    if worker_id not in worker_dict:
        worker_dict[worker_id] = []
    worker_dict[worker_id].append(anno)

    if img_name not in img_dict:
        img_dict[img_name] = []
    img_dict[img_name].append(anno)

img_idv_labeled = [len(img_annos) for img_annos in img_dict.values()]
img_idv_mean = np.mean(np.array(img_idv_labeled))
img_idv_std = np.std(np.array(img_idv_labeled))
print (f'Each Image is labeled by {img_idv_mean:.2f} $\pm$ {img_idv_std:.2f}')

worker_labeled = [len(worker_annos) for worker_annos in worker_dict.values()]
worker_idv_mean = np.mean(np.array(worker_labeled))
worker_idv_std = np.std(np.array(worker_labeled))
print (f'Each worker label {worker_idv_mean:.2f} $\pm$ {worker_idv_std:.2f}')

# %%
