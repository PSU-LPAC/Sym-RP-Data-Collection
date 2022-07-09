''' 
Script to convert new results to Chris's format 
Chris's format:
ImgSymLabels.json
[
{
    "fields": {
      "imgname": "real_rot.jpg",
      "num_Rot": 1,
      "mt_usr": "A2O5OJXCUFQ3FV",
      "num_Ref": 2,
      "start_time": "2015-06-17T01:23:11.830Z",
      "end_time": "2015-06-17T01:26:38.170Z",
      "symImage": 36780,
      "passed_over": false
    },
    "model": "symCaptcha.imgsymlabel",
    "pk": 1121
},
]

Languages.json
[
{
    "fields": { "name": "Afrikaans", "short_name": "af" },
    "model": "symCaptcha.language",
    "pk": 2
},
]

MTUsers.json
[
{
    "fields": {
      "labels": [
        1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162, 1163, 1164, 1167, 1168,
      ],
      "seen_images": [
        27, 28, 50, 51, 52, 53, 73, 103, 112, 124, 127, 152, 165, 178, 179, 180,
      ],
      "num_logins": 4,
      "education_level": "s",
      "num_pending": 101,
      "first_language": "English",
      "passes": 0,
      "cur_country": "US",
      "assignmentId": "3HHRAGRYX84JUEKU1USYQEM8KC1O9U",
      "country": "US",
      "comments": "",
      "num_labeled": 0,
      "num_test": 3,
      "turkSubmitTo": "https://www.mturk.com",
      "passed_test": 2,
      "ammount_owed": 2.0200000000000014,
      "accepted": true,
      "name": "A1FTGHYEU1T71Y",
      "gender": "f",
      "ammount_paid": 0.0,
      "num_paid": 0,
      "user_languages": [1],
      "hitId": "3HHRAGRYX84JUEKU1USYQEM8KC1O9U",
      "workerId": "A1FTGHYEU1T71Y",
      "repeats": 10,
      "age": "21-30"
    },
    "model": "symCaptcha.mtuser",
    "pk": 172
},
]


SymImages.json
[
{
    "fields": {
      "imgname": "COCO_test2014_000000454433.jpg",
      "num_Rot": 1,
      "human_not_confused": "y",
      "num_Ref": 1,
      "alg_fail": "y",
      "any_symmetries": "y",
      "passed": 2,
      "ground_truth": "[1,1]",
      "num_labels": 15
    },
    "model": "symCaptcha.symimage",
    "pk": 1
},
]

UserLabels.json
[
{
    "fields": {
      "kind": "rot",
      "imgname": "real_rot.jpg",
      "mt_usr": "A2O5OJXCUFQ3FV",
      "sympointY_line": -1.0,
      "sympointX": 177.171875,
      "sympointY": 200.0,
      "sympointX_line": -1.0,
      "ImgSymLabel": 1121,
      "date": "2015-07-09 18:06:10.702769",
      "symImage": 36780
    },
    "model": "symCaptcha.userlabel",
    "pk": 13721
},
]
'''

#%%
###
import os, json
from datetime import datetime
###

def convertImg(img_dir, start_idx = 0,img_num = 0):
    ''' Traverse the image folder, and convert to Chris's format '''

    sym_images = {} #* {img_name:sym_image_item, ...}

    for idx, img_name in enumerate(os.listdir(img_dir)[start_idx:]):
        if (img_num != 0 and idx >= img_num):
            break
        sym_image_item = createSymImageItem()
        sym_image_item['fields']['imgname'] = img_name

        sym_image_item['pk'] = len(sym_images) + 1
        sym_images[img_name] = sym_image_item

    return sym_images

def convertLanguages(languages_list):
    ''' Convert languages to Chris's format '''
    languages = {} #* {language:language_item, ...}
    for language in languages_list:
        language_item = createLanguageItem()
        language_name = language[:-4]
        short_name = language[-3:-1]
        language_item['fields']['name'] = language_name
        language_item['fields']['short_name'] = short_name

        language_item['pk'] = len(languages) + 1
        languages[language[:-1]] = language_item

    return languages

def convertMTUser(survey_json, languages):
    ''' Read the survey, and convert to Chris's format '''
    mtusers = {} #* {worker_id:mtuser_item, ...}

    for survey in survey_json:
        mtuser_item = createMTUserItem()
        worker_id = survey['WorkerId']
        mtuser_item['fields']['accepted'] = True

        mtuser_item['fields']['workerId'] = worker_id
        mtuser_item['fields']['name'] = worker_id
        mtuser_item['fields']['age'] = survey['Age']
        mtuser_item['fields']['gender'] = survey['Gender']
        mtuser_item['fields']['education_level'] = survey['Education']
        mtuser_item['fields']['cur_country'] = survey['Country']
        mtuser_item['fields']['country'] = survey['Country']
        mtuser_item['fields']['first_language'] = survey['First Language']

        user_languages = survey['Languages']
        user_language_pks = [languages[l]['pk'] for l in user_languages]
        mtuser_item['fields']['user_languages'] = user_language_pks

        mtuser_item['pk'] = len(mtusers) + 1
        mtusers[worker_id] = mtuser_item
    
    return mtusers

def convertAnno(annos_json, sym_images, mtusers):
    ''' Read the new annotation, and convert to Chris's format '''
    img_sym_labels = []
    user_labels = []

    # each anno is one worker's labels for an image
    for anno in annos_json:
        worker_id = anno['WorkerId']
        assign_id = anno['AssignmentId']
        hit_id = anno['HITId'] 
        img_name = anno['ImageName']
        labels = anno['WorkerLabel']

        num_rot, num_ref = 0, 0
        sym_img_pk = sym_images[img_name]['pk']
        
        # update the mtuser
        if worker_id not in mtusers:
            mtusers[worker_id] = createMTUserItem()
            
        mtusers[worker_id]['fields']['labels'].append(sym_img_pk)
        mtusers[worker_id]['fields']['seen_images'].append(sym_img_pk)

        # * Image Sym Label Item
        img_sym_label_item = createImgSymLabelItem()
        img_sym_label_item['fields']['imgname'] = img_name
        img_sym_label_item['fields']['mt_usr'] = worker_id
        img_sym_label_item['fields']['symImage'] = sym_img_pk

        img_sym_label_item['fields']['start_time'] = f'{datetime.now()}' 
        img_sym_label_item['fields']['end_time'] = f'{datetime.now()}' 

        img_sym_label_pk = len(img_sym_labels) + 1
        img_sym_label_item['pk'] = img_sym_label_pk

        # * Check each Label
        for label_name, label_data in labels.items():
            label_type = 'None'
            if label_name.split(' ')[0] == 'Rotation': 
                if len(label_data) == 2:
                    label_type = 'rot'
                    num_rot += 1
            elif label_name.split(' ')[0] == 'Reflection':
                 if len(label_data) == 4:
                    label_type = 'ref'
                    num_ref += 1

            if label_type != 'None':
                pk = len(user_labels) + 1

                # * User Label Item
                user_label_item = createUserLabelItem()
                user_label_item['fields']['kind'] = label_type
                user_label_item['fields']['imgname'] = img_name
                user_label_item['fields']['mt_usr'] = worker_id
                
                user_label_item['fields']['sympointX'] = label_data[0]
                user_label_item['fields']['sympointY'] = label_data[1]

                if  label_type == 'ref':
                    user_label_item['fields']['sympointX_line'] = label_data[2]
                    user_label_item['fields']['sympointY_line'] = label_data[3]

                user_label_item['fields']['date'] = f'{datetime.now()}'

                user_label_item['fields']['ImgSymLabel'] = img_sym_label_pk    
                user_label_item['fields']['symImage'] = sym_images[img_name]['pk']

                user_label_item['pk'] = len(user_labels) + 1
                user_labels.append(user_label_item)
        
        # update the img_sym_label
        img_sym_label_item['fields']['num_Rot'] = num_rot
        img_sym_label_item['fields']['num_Ref'] = num_ref

        img_sym_labels.append(img_sym_label_item)
        
    return img_sym_labels, user_labels, mtusers


def createImgSymLabelItem():
    ''' Create a default ImgSymLabel item '''
    img_sym_label_item = {'fields':{}, 'model':'symCaptcha.imgsymlabel', 'pk':0}

    img_sym_label_item['fields']['imgname'] = ''
    img_sym_label_item['fields']['mt_usr'] = ''
    img_sym_label_item['fields']['num_Rot'] = 0
    img_sym_label_item['fields']['num_Ref'] = 0
    img_sym_label_item['fields']['start_time'] = ''
    img_sym_label_item['fields']['end_time'] = ''
    img_sym_label_item['fields']['symImage'] = 0   # pk of symImage item
    img_sym_label_item['fields']['passed_over'] = False

    return img_sym_label_item.copy()

def createLanguageItem():
    ''' Create a default Language item '''
    language_item = {'fields':{}, 'model':'symCaptcha.language', 'pk':0}

    language_item['fields']['name'] = ''
    language_item['fields']['short_name'] = ''
    
    return language_item.copy()

def createMTUserItem():
    ''' Create a default MTUser item '''
    mtuser_item = {'fields':{}, 'model':'symCaptcha.mtuser', 'pk':0}

    mtuser_item['fields']['workerId'] = ''
    mtuser_item['fields']['assignmentId'] = ''
    mtuser_item['fields']['hitId'] = ''

    mtuser_item['fields']['labels'] = []        #* [img_pk, ... ]
    mtuser_item['fields']['seen_images'] = []   #* [img_pk, ... ]
    mtuser_item['fields']['num_logins'] = 0
    mtuser_item['fields']['num_labeled'] = 0
    mtuser_item['fields']['num_pending'] = 0
    mtuser_item['fields']['repeats'] = 10
    mtuser_item['fields']['passes'] = 0
    mtuser_item['fields']['ammount_owed'] = 0

    mtuser_item['fields']['accepted'] = False
    mtuser_item['fields']['num_test'] = 0
    mtuser_item['fields']['passed_test'] = 0

    mtuser_item['fields']['ammount_paid'] = 0.0
    mtuser_item['fields']['num_paid'] = 0

    mtuser_item['fields']['comments'] = ''

    mtuser_item['fields']['name'] = ''
    mtuser_item['fields']['age'] = ''
    mtuser_item['fields']['gender'] = ''
    mtuser_item['fields']['education_level'] = ''
    mtuser_item['fields']['cur_country'] = ''
    mtuser_item['fields']['country'] = ''
    mtuser_item['fields']['first_language'] = ''
    mtuser_item['fields']['user_languages'] = []
    
    mtuser_item['fields']['turkSubmitTo'] = 'https://www.mturk.com'
    
    return mtuser_item.copy()

def createSymImageItem():
    ''' Create a default SymImage item '''
    
    sym_image_item = {'fields':{}, 'model':'symCaptcha.symimage', 'pk':0}

    sym_image_item['fields']['imgname'] = ''
    
    sym_image_item['fields']['num_Rot'] = 0
    sym_image_item['fields']['num_Ref'] = 0
    sym_image_item['fields']['num_labels'] = 0
    sym_image_item['fields']['passed'] = 0
    sym_image_item['fields']['ground_truth'] = ''
    
    sym_image_item['fields']['human_not_confused'] = 'y'
    sym_image_item['fields']['any_symmetries'] = 'y'
    sym_image_item['fields']['alg_fail'] = 'n'

    return sym_image_item.copy()

def createUserLabelItem():
    ''' Create a default UserLabel item '''
    
    user_label_item = {'fields':{}, 'model':'symCaptcha.userlabel', 'pk':0}

    user_label_item['fields']['kind'] = ''
    user_label_item['fields']['imgname'] = ''
    user_label_item['fields']['mt_usr'] = ''
    user_label_item['fields']['sympointX'] = -1.0
    user_label_item['fields']['sympointY'] = -1.0
    user_label_item['fields']['sympointX_line'] = -1.0
    user_label_item['fields']['sympointY_line'] = -1.0
    user_label_item['fields']['ImgSymLabel'] = 0   # pk of corresponding ImgSymLabel item
    user_label_item['fields']['date'] =  ''
    user_label_item['fields']['symImage'] = 0   # pk of symImage item

    return user_label_item.copy()

#%%
if __name__ == "__main__":
    batch_list = [
        'Batch Symmetry Labeling Iter 1 (0-49)',
        'Batch Symmetry Labeling Iter 2 (50-99)',
        'Batch Symmetry Labeling Iter 3 (100-149)',
        'Batch Symmetry Labeling Iter 4 (150-199)',
        'Batch Symmetry Labeling Iter 5 (200-249)',
        'Batch Symmetry Labeling Iter 6 (250-299)'
    ]
    
    batch_name = batch_list[0]
    start_idx = 0

    save_dir = "E:\Lab Work\Datasets\Sym-RP-Collection\Results\Chris's format"

    os.makedirs(os.path.join(save_dir, batch_name), exist_ok=True)

    #%%
    language_file_path = 'E:\Lab Work\Datasets\Sym-RP-Collection\Results\languages.txt'
    with open(language_file_path, 'r') as f:
        languages_list = f.readlines()
    languages = convertLanguages(languages_list)

    with open(os.path.join(save_dir, batch_name, 'Languages.json'), 'w') as f:
        json.dump(list(languages.values()), f, indent=4)

    #%%
    survey_file_path = 'E:/Lab Work/Datasets/Sym-RP-Collection/Results/background_survey.json'
    with open(survey_file_path, 'r') as f:
        survey_json = json.load(f)
    mtusers = convertMTUser(survey_json, languages)

    with open(os.path.join(save_dir, batch_name, 'MTUsers.json'), 'w') as f:
        json.dump(list(mtusers.values()), f, indent=4)

    #%%
    img_dir = 'E:/Lab Work/Datasets/Sym-RP-Collection/Images'
    sym_images = convertImg(img_dir, start_idx=start_idx, img_num=50)

    with open(os.path.join(save_dir, batch_name, 'SymImages.json'), 'w') as f:
        json.dump(list(sym_images.values()), f, indent=4)

    #%%
    annos_file_path = f'E:\Lab Work\Datasets\Sym-RP-Collection\Results\Batch\{batch_name}\{batch_name}.json'
    with open(annos_file_path, 'r') as f:
        annos_json = json.load(f)

    img_sym_labels, user_labels, updated_mtusers = convertAnno(annos_json, sym_images, mtusers)

    with open(os.path.join(save_dir, batch_name, 'ImgSymLabels.json'), 'w') as f:
        json.dump(img_sym_labels, f, indent=4)

    with open(os.path.join(save_dir, batch_name, 'UserLabels.json'), 'w') as f:
        json.dump(user_labels, f, indent=4)    

    with open(os.path.join(save_dir, batch_name, 'MTUsers.json'), 'w') as f:
        json.dump(list(updated_mtusers.values()), f, indent=4)
# %%
