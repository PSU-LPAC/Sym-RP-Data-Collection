''' A script for Test & generate some stuff '''
import os,json
import pandas as pd 
import xmltodict
###
from process_sym import convert_result, visu_results
from util import setup_mturk, approve_bonus
###

approve_feedback = 'We will post more symmetry labeling tasks. We sincerely invite you to the coming tasks.'
survey_request = "Would you take 5 minutes to complete a background survey? The survey doesn't contain any personally identifying information. Here is the link: https://forms.gle/eAjfV8w85ZbA83gR7"

per_reward = 0.12
basic_reward = 3.3


img_local_dir='E:\Lab Work\Datasets\Sym-RP-Collection\Images'
save_dir = 'E:\Lab Work\Datasets\Sym-RP-Collection\Results\Batch\Batch Results\Test'

with open ('E:\Lab Work\Datasets\Sym-RP-Collection\img_size.json', 'r') as f:
    all_imgs_size = json.load(f)

sym_batch_dir = 'E:\Lab Work\Datasets\Sym-RP-Collection\AWS csv\sym-batch'
qual_file_path = 'E:/Lab Work/Datasets/Sym-RP-Collection/AWS csv/quals.csv'
qual_worker_ids = pd.read_csv(qual_file_path)['WorkerId'].values.tolist()

batch_HITs = {
    'Batch Symmetry Labeling Iter 1 (0-49)': '3S37Y8CWJJWYOBIZ7QL43TBJZTU4WN',
    'Batch Symmetry Labeling Iter 2 (50-99)': '3HO4MYYR2DKZBUX8VEZII3A0A5A6UY',
    'Batch Symmetry Labeling Iter 3 (100-149)': '3SZYX62S6RW1UFLYDNW2G5IG60357I',
    'Batch Symmetry Labeling Iter 4 (150-199)': '388CL5C1SUJCPTUVIJYLO7376TZHLK',
    'Batch Symmetry Labeling Iter 5 (200-249)': '3D06DR523GFHLO42CPP87YVST3ZAM4',
    'Batch Symmetry Labeling Iter 6 (250-299)': '37MQ8Z1JRPSSA2YCIDK4VBZ1QPL2YF',
    'Batch Symmetry Labeling Iter 7 (300-349)': '3QI9WAYOH17JWH54694I32SCPGF6SO',
    'Batch Symmetry Labeling Iter 8 (350-399)': '3OZ4VAIBF8BBC41FKN3CNTHOAQTJVC',
    'Batch Symmetry Labeling Iter 9 (400-449)': '3YOAVL4CBBD2I6N4ID5B2X51G48Z40',
    'Batch Symmetry Labeling Iter 10 (450-499)': '3RHLQY6EE40ZF5I8QVGEB5MYSMZ4D7',
}


# * Setup MTurk
client = setup_mturk(True)

print('AvailableBalance:', client.get_account_balance()['AvailableBalance'])

''' Bonus some workers '''
bonus_worker_list = {
    'Batch Symmetry Labeling Iter 2 (50-99)': 
    ['AHU90811PMIOD', 'A1KOG5Q6XX0DPU'],

    'Batch Symmetry Labeling Iter 3 (100-149)': 
    ['AUPNFXLSAET9G', 'A16J2CW30USNJI'],

    'Batch Symmetry Labeling Iter 4 (150-199)':
    ['AE2BOK50NTKFX', 'A26QYSN5BMPHPM'],

    'Batch Symmetry Labeling Iter 5 (200-249)':
    ['A1KOG5Q6XX0DPU'],

    'Batch Symmetry Labeling Iter 6 (250-299)': 
    ['AUPNFXLSAET9G', 'A2YM3APK5O3UKG', 'A26QYSN5BMPHPM'],

    'Batch Symmetry Labeling Iter 7 (300-349)':
    ['A3HP4BPBXGDM2F', 'A2GRA6N98ZPIQ1'],

    'Batch Symmetry Labeling Iter 8 (350-399)':
    ['AUPNFXLSAET9G', 'A2W4DO745WMPDO', 'AE2BOK50NTKFX', 'A2LGSLGNMXKNYY', 'A3HP4BPBXGDM2F', 'A34H7SANVXDBFA', 'A2BDTRZY47OG5S'],

    'Batch Symmetry Labeling Iter 9 (400-449)':
    ['AUPNFXLSAET9G', 'A2LGSLGNMXKNYY', 'A2BDTRZY47OG5S', 'AE2BOK50NTKFX', 'A1KH9VI2D0V43B', 'A2W4DO745WMPDO'],

    'Batch Symmetry Labeling Iter 10 (450-499)':
    ['AUPNFXLSAET9G', 'A1KOG5Q6XX0DPU', 'A3B2YRSMSC2J3T', 'A2GRA6N98ZPIQ1']
}

# * Process Batches
suggestions = []
annos = []
approve_status = []

for batch_name in batch_HITs:
    print (batch_name)

    # * Get the image_list & imgs_size
    img_urls = pd.read_csv(os.path.join(sym_batch_dir, f'{batch_name}.csv'))['img_urls'][0]
    img_urls = json.loads(img_urls)

    # * Get the assignments
    hit_id = batch_HITs[batch_name]
    response = client.list_assignments_for_hit(
        HITId=hit_id,
        AssignmentStatuses=['Approved'],
        MaxResults=100
    )

    assignments = response['Assignments']

    assign_num = 0
    idv_label_num = 0


    for assignment in assignments:
        worker_id = assignment['WorkerId']
        assignment_id = assignment['AssignmentId']

        if batch_name not in bonus_worker_list:
            continue
        if worker_id not in bonus_worker_list[batch_name]:
            continue
        answer_dict = xmltodict.parse(assignment['Answer'])
        answers = answer_dict['QuestionFormAnswers']['Answer']['FreeText']
        answers = json.loads(answers)[0]
        batch_results = json.loads(answers['annos'])

        # * Process Qualification
        qualified = True if worker_id in qual_worker_ids else False

        # * Process Labeling Results
        num_label = 0
        for img_url, single_result in zip (img_urls, batch_results):
            img_name = os.path.split(img_url)[-1]
            img_size = all_imgs_size[img_name]
            # img = cv2.imread(os.path.join(image_local_dir, img_name))

            worker_label = convert_result(single_result, img_size)
            if len(worker_label) > 0:
                num_label += 1
                idv_label_num += 1

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
            

        assign_num += 1

        if True:
            # * Get worker status: approve/reject, number of labeled images
            approved = True if qualified and num_label > 5 else False

            bonus_reward =  max(0, per_reward * num_label -  basic_reward) 
            token = f'{assignment_id}-{bonus_reward}'
            feedback = approve_feedback if qualified else survey_request

            print (len(token))
            if approved:
                approve_bonus(client, worker_id, assignment_id, hit_id, feedback, bonus_reward, num_label, in_production=True)