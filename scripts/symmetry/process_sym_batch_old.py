''' Process Batch Symmetry Labeling Task Results '''
#%%
from glob import glob
import boto3
import pandas as pd
import json
import os
import cv2
###
from process_sym import convert_result, visu_results, mergeAnnos
###

def setup_mturk(client_in_production=False):
    # * Setup the MTurk Client
    environments = {
    "production": {
        "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
        "preview": "https://www.mturk.com/mturk/preview"
    },
    "sandbox": {
        "endpoint": 
            "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
        "preview": "https://workersandbox.mturk.com/mturk/preview"
    },
    }
    mturk_environment = environments["production"] if client_in_production else environments["sandbox"]

    session = boto3.Session(profile_name='mturk')
    client = session.client(
        service_name='mturk',
        region_name='us-east-1',
        endpoint_url=mturk_environment['endpoint'],
    )
    print ('client_in_production:', client_in_production)
    return client

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

    
def loadBatchResults(batch_file_path, imgs_size, batch_name = '', quals = None, process_assignment_type = 'Approved'):
    ''' 
        Load the batch result .csv file. 
        Output an array contains all individual results
    '''

    data = pd.read_csv(batch_file_path)

    annos = []
    suggestions = []
    workers_status = {}
    qual_worker_ids = []
    if quals is not None:
        qual_worker_ids = quals['WorkerId'].values.tolist()

    for idx, row in data.iterrows():
        if row['AssignmentStatus'] != process_assignment_type:
            continue
        
        worker_id = row['WorkerId']
        assignment_id = row['AssignmentId']
        hit_id = row['HITId']

        work_time = row['WorkTimeInSeconds']
        submit_time = row['SubmitTime']

        img_urls = json.loads(row['Input.img_urls'])
        answers = json.loads(row['Answer.taskAnswers'])[0]
        batch_results = json.loads(answers['annos'])

        print (f'Start WorkerId: {worker_id}')

        # * Process Suggestion
        suggestion = ''
        if 'suggestions' in answers:
            suggestion = answers['suggestions']
        suggestions.append({'WorkerId':worker_id, 'Suggestion': suggestion})

        # * Process Qualification
        qualified = True if worker_id in qual_worker_ids else False

        # * Process Labeling Results
        num_label = 0
        for img_url, single_result in zip (img_urls, batch_results):
            img_name = os.path.split(img_url)[-1]
            img_size = imgs_size[img_name]
            # img = cv2.imread(os.path.join(image_local_dir, img_name))

            worker_label = convert_result(single_result, img_size)
            if len(worker_label) > 0:
                num_label += 1
            anno = {
                'WorkerId':worker_id, 
                'AssignmentId':assignment_id,
                'HITId':hit_id,
                'ImageUrl':img_url, 
                'ImageName':img_name,
                'WorkerLabel':worker_label, 
                'ImageSize':img_size,
                'Qualified':qualified,
                }
        
            annos.append(anno)

        # * Get worker status: approve/reject, number of labeled images
        approved = True if qualified and num_label > 5 else False
        workers_status[worker_id] = {'num_label':num_label, 'qualified':qualified, 'approved':approved,'assignment_id':assignment_id}
        

    return annos, suggestions, workers_status

if __name__ == "__main__":
        
        
    #%%
    # * Path Settings
    image_local_dir='E:/Lab Work/Datasets/Sym-RP-Collection/Images'
    qual_file_path = 'E:/Lab Work/Datasets/Sym-RP-Collection/AWS csv/quals.csv'

    batch_name = 'Batch Symmetry Labeling Iter 2 (50-99)'
    batch_file_path='D:\Downloads\Batch_4767297_batch_results (1).csv'

    save_folder = 'E:/Lab Work/Datasets/Sym-RP-Collection/Results/Batch'
    batch_folder = os.path.join(save_folder, batch_name)
    suggestion_folder = os.path.join(batch_folder, 'Suggestions')
    os.makedirs(batch_folder, exist_ok=True)
    os.makedirs(suggestion_folder, exist_ok=True)
        

    #%%
    # * Process Batch Results

    annos, suggestions, workers_status = loadBatchResults(
        batch_file_path, image_local_dir, batch_name, 
        pd.read_csv(qual_file_path), continue_flag = True)

    with open(os.path.join(batch_folder, f'{batch_name}.json'), 'w') as f:
        json.dump(annos, f, indent=4)

    print (suggestions)
    # with open(os.path.join(suggestion_folder, f'suggestion.json'), 'w') as f:
    #     json.dump(suggestions, f, indent=4)

    print ('Qualified:', len(workers_status['Qualified']))
    print ('Not Qualified:', len(workers_status['Not Qualified']))


    #%%
    # * Approve & Reward
    num_imgs = 55
    basic_reward = 3.3
    per_reward = 0.12

    with open(os.path.join(batch_folder, f'{batch_name}.json'), 'r') as f:
        annos = json.load(f)

    showWorkerReward(annos, num_imgs, basic_reward, per_reward)

    #%%
    # * Merge Annotations
    # anno_files = glob(os.path.join(batch_folder, '*.json'))
    anno_files = [os.path.join(batch_folder, f'{batch_name}.json')]
    all_annos = []
    for anno_file in anno_files:
        with open(anno_file, 'r') as f:
            annos = json.load(f)
            all_annos.append(annos)

    merged_annos = mergeAnnos(all_annos)
    with open(os.path.join(batch_folder, 'merged_annos.json'), 'w') as f:
        json.dump(merged_annos, f, indent=4)

    #%%
    # * Visualize Results

    with open(os.path.join(batch_folder, f'merged_annos.json'), 'r') as f:
        annos = json.load(f)
    visu_results(annos, image_local_dir, os.path.join(batch_folder, 'visu'))