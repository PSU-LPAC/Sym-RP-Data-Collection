''' MTurk Related Functions '''
import os, json, csv
import boto3
import xmltodict
import json
import pandas as pd
import cv2
###
from process_sym import convertResult

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
    print('AvailableBalance:', client.get_account_balance()['AvailableBalance'])


def process_assignment(annos):
    # * Approve/Reject the assignment, and/or set Bonus reward

    workers_status = {}
    for anno in annos:
        worker_id = anno['WorkerId']
        assignment_id = anno['AssignmentId']
        qualified = anno['Qualification']
        if worker_id not in workers_status:
            workers_status[worker_id] = {'num_label':0, 'qualified':qualified, 'assignment_id':assignment_id}
        if len(anno['WorkerLabel']) != 0:
            workers_status[worker_id]['num_label'] += 1

    for worker_id in workers_status:
        num_label = workers_status[worker_id]['num_label']
        qualified = workers_status[worker_id]['qualified']
        bonus_reward =  max(0, per_reward * num_label -  basic_reward)

        workers_status[worker_id]['bonus_reward'] = bonus_reward
        workers_status[worker_id]['approve'] = True if qualified == 1 else False

    return workers_status
    # show the workers_status
    for worker_id in workers_status:
        print (worker_id, workers_status[worker_id])


#%%
# * Approve specific workers
# approve_workers = ['ATRRW34VN38IX', 'A1XVZ4TW03BMF1', 'A3G4GV7ALSAGGF', 'A2HMEGTAFO0CS8', ]
# for worker_id in approve_workers:
#     workers_status[worker_id]['approve'] = True

# for worker_id in workers_status:
#     if workers_status[worker_id]['approve']:
#         print (worker_id)

# * Approve and Send Bonus
def approve_and_bonus(client, workers_status, num_imgs = 55, basic_reward = 3.3, per_reward = 0.12):
    approve_feedback = 'We will post more symmetry labeling tasks. We sincerely invite you to the coming tasks.'
    survey_request = "Would you take 5 minutes to complete a background survey? The survey doesn't contain any personally identifying information. Here is the link: https://forms.gle/eAjfV8w85ZbA83gR7"

    bonus_reward =  max(0, per_reward * num_label -  basic_reward)

    for worker_id in workers_status:
        assignment_id = workers_status[worker_id]['assignment_id']
        bonus_reward = workers_status[worker_id]['bonus_reward']
        num_label = workers_status[worker_id]['num_label']
        qualified = workers_status[worker_id]['qualified']

        token = f'{worker_id}-{assignment_id}-{bonus_reward}'

        feedback = approve_feedback if qualified else survey_request

        if workers_status[worker_id]['approve']:
            # Approve
            try:
                response = client.approve_assignment(
                    AssignmentId=assignment_id,
                    RequesterFeedback=feedback,
                    OverrideRejection=False
                )
                print (f'Approve: {worker_id}')
            except:
                print (f'Cannot Approve: {worker_id}')
            # Bonus
            try:
                if worker_id == 'AS0EC2HIE974S' and assignment_id == '358010RM5QPFU84XRTNF2MKSH9WVXK':
                    continue
                response = client.send_bonus(
                    WorkerId= worker_id,
                    BonusAmount=f'{bonus_reward:.2f}',
                    AssignmentId=assignment_id,
                    Reason=f'Labeled {num_label} images',
                    UniqueRequestToken=token
                )
                print (f'Bonus: {worker_id} with {bonus_reward:.2f}')
            except:
                print (f'Cannot Bonus: {worker_id}')

    print('AvailableBalance:', client.get_account_balance()['AvailableBalance'])

# %%
# * Reject
reject_feedback = 'Please follow the tutorial to label symmetry properly.'
for worker_id in workers_status:
    assignment_id = workers_status[worker_id]['assignment_id']

    if not workers_status[worker_id]['approve']:
        response = client.reject_assignment(
            AssignmentId=assignment_id,
            RequesterFeedback=reject_feedback
        )

        print (f'Reject {worker_id}')


#%%
# * Approve & Reject Offline
reject_feedback = 'Please follow the tutorial to label symmetry properly.'
csv_path = 'E:/Lab Work/Datasets/Sym-RP-Collection/AWS csv/update_status.csv'
with open(csv_path, 'w', newline='') as f: 
    writer = csv.writer(f) 
    writer.writerow(['AssignmentId', 'HITId', 'Approve', 'Reject'])
    
    for worker_id in workers_status:
        assignment_id = workers_status[worker_id]['assignment_id']
        if workers_status[worker_id]['approve']:
            writer.writerow([assignment_id, 'x', ''])
        else:
            writer.writerow([assignment_id, '', reject_feedback])


#%%
# * TEST
worker_id = 'A12BZA2BD1WTFG'
assignment_id = '33LK57MYL51O7BN8YG371AZ98KEZST'
bonus = 0.01
token = f'{worker_id}-{assignment_id}-{bonus}'
# response = client.send_bonus(
#     WorkerId= worker_id,
#     BonusAmount=f'{bonus}',
#     AssignmentId=assignment_id,
#     Reason='test',
#     UniqueRequestToken=f'token'
# )

response = client.reject_assignment(
    AssignmentId=assignment_id,
    RequesterFeedback='Test Reject'
)

# response = client.approve_assignment(
#     AssignmentId=assignment_id,
#     RequesterFeedback='Test Approve',
#     OverrideRejection=True
# )

# %%
