''' Read the survey csv file and conver it to JSON file '''
#%%
import os, json
import pandas as pd

survey_file_path = 'D:\Downloads\Symmetry Qualification Background Survey (Responses) - Form Responses 1 (3).csv'
save_dir = 'E:\Lab Work\Datasets\Sym-RP-Collection\Results'

data = pd.read_csv(survey_file_path)
surveys = {}    #* {worker_id: survey_dict, ...}


for idx, row in data.iterrows():
    worker_id = row[1]
    languages = [l.lstrip() for l in row[7].split(',')]
    if worker_id not in surveys:
        survey_dict = {
            'WorkerId':worker_id,
            'Age':row[2],
            'Gender':row[3],
            'Education':row[4],
            'Country':row[5],
            'First Language':row[6],
            'Languages':languages
        }

        surveys[worker_id] = survey_dict

with open(os.path.join(save_dir, 'background_survey.json'), 'w') as f:
    json.dump(list(surveys.values()), f, indent=4)


#%%
''' Plot the Statistics '''
import os, json
import pandas as pd
survey_file_path = 'D:\Downloads\Symmetry Qualification Background Survey (Responses) - Form Responses 1 (3).csv'
data = pd.read_csv(survey_file_path)

workers = []
# get the unique rows
row_ids = []
for idx, row in data.iterrows():
    worker_id = row[1]
    if worker_id not in workers:
        row_ids.append(idx)
        workers.append(worker_id)

df = data.loc[row_ids]

keys = df.keys()

for i in [2,3]:
    df_group = df[[keys[0], keys[i]]].groupby([keys[i]])
    print (df_group.count())
    
for key in keys[4:]:
    df_group = df[[keys[0], key]].groupby([key])
    print (df_group.count())
    df_group.count().plot(kind='bar', subplots=True)
# %%
