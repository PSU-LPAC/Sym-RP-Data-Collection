''' Test Script '''
#%%
''' Load Packages '''
###
import os
import sys
module_path = os.path.abspath(os.path.join(__file__, '..', '..'))
if module_path not in sys.path:
    sys.path.append(module_path)
###
import cv2, json
###
from process_rp import convert_result
from util import visu_rp
###

#%%
''' Plot Labels '''
img_dir = 'E:/Lab Work/Code/Sym-RP-Data-Collection/RecurringPattern/figures/examples'
save_dir = 'E:/Lab Work/Code/Sym-RP-Data-Collection/RecurringPattern/figures/examples'
img_name = 'new789.jpg'

coordinates = '[{\"class\":\"RP 1\",\"mode\":\"polygon\",\"data\":[[17,174],[113,179],[113,312],[23,322]]},{\"class\":\"RP 1\",\"mode\":\"polygon\",\"data\":[[118,182],[123,310],[197,303],[195,185]]},{\"class\":\"RP 1\",\"mode\":\"polygon\",\"data\":[[206,183],[209,300],[266,296],[268,185]]},{\"class\":\"RP 1\",\"mode\":\"polygon\",\"data\":[[278,188],[278,297],[325,289],[328,192]]},{\"class\":\"RP 1\",\"mode\":\"polygon\",\"data\":[[335,192],[338,289],[379,286],[379,193]]},{\"class\":\"RP 1\",\"mode\":\"polygon\",\"data\":[[385,196],[385,282],[424,280],[422,197]]}]'

label_img_size = [646, 485]

single_result = {'coordinates': json.loads(coordinates), 'imageSize':label_img_size}

img = cv2.imread(os.path.join(img_dir, img_name))
img_size = [img.shape[1], img.shape[0]]

# anno = convert_result(single_result, img_size)
# visu = visu_rp(img, anno)

# cv2.imwrite(os.path.join(save_dir, f'labeled_{img_name}'), visu)

#%%
''' Make Gif '''
import imageio, glob
from util import resize_with_aspect_ratio

img_dir = 'E:/Lab Work/Code/Sym-RP-Data-Collection/RecurringPattern/figures/examples'


img_names = ['new027', 'new036', 'new632', 'new653', 'new705', 'new789']

for img_name in img_names:
    imgs = []
    for idx, img_path in enumerate(glob.glob(os.path.join(img_dir, f'*{img_name}.jpg'))):
        img = cv2.imread(img_path)
        img = resize_with_aspect_ratio(img, width=800, height=800)
        cv2.imwrite(img_path, img)
        imgs.append(imageio.imread(img_path))
    imageio.mimwrite(os.path.join(img_dir, f'{img_name}_label.gif'), imgs, format='GIF', fps=1)

# os.system(f'ffmpeg -f image2 -framerate 1 -i "{img_dir}/{img_name}_%01d.jpg"  {img_dir}/{img_name}_label.gif')

# %%
