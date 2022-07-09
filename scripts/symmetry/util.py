''' Some visualization functions'''
###
import matplotlib.pyplot as plt
import cv2
import boto3
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

def approve_bonus(client, worker_id, assignment_id, hit_id, feedback='', bonus_reward=0, num_label=0, in_production=False):
    ''' Approve & Bonus an assignment'''
    token = f'{worker_id}-{assignment_id}-{bonus_reward}'
    # * Approve
    try:
        if in_production:
            response = client.approve_assignment(
                AssignmentId=assignment_id,
                RequesterFeedback=feedback,
                OverrideRejection=True
            )
            print (f'\tApprove: {worker_id}')
        else:
            print (f'\t[Will] approve: {worker_id}')
    except:
        print (f'\tCannot Approve: {worker_id}')
    # * Bonus
    if bonus_reward:
        try:
            if in_production:
                response = client.send_bonus(
                    WorkerId= worker_id,
                    BonusAmount=f'{bonus_reward:.2f}',
                    AssignmentId=assignment_id,
                    Reason=f'Labeled {num_label} images',
                    UniqueRequestToken=token
                )
                print (f'\tBonus: {worker_id} with {bonus_reward:.2f}')
            else:
                print (f'\t[Will] bonus: {worker_id} with {bonus_reward:.2f}')
        except:
            print (f'\tCannot Bonus: {worker_id} with {bonus_reward:.2f}')

def drawRot(img, rot_gt):
    ''' Draw rotation center '''

    
    # fig, ax = plt.subplots(figsize=(12,8), dpi=300)
    # ax.set_axis_off()
    # ax.imshow(img)

    rot_center = [rot_gt[0]*img.shape[1], rot_gt[1]*img.shape[0]]
    
    # center_circle = plt.Circle(rot_center, 3, color='r')
    # ax.add_patch(center_circle)

    cv2.circle(img, rot_center, 3, color='r')
    return img
    return fig, ax

def drawRef(img, ref_gt):
    ''' Draw reflection line '''
    fig, ax = plt.subplots(figsize=(12,8), dpi=300)
    # ax.set_axis_off()
    ax.imshow(img)

    start = [ref_gt[0]*img.shape[1], ref_gt[1]*img.shape[0]]
    end = [ref_gt[2]*img.shape[1], ref_gt[3]*img.shape[0]]

    start_dot = plt.Circle(start, 3, color='g')
    ax.add_patch(start_dot)

    end_dot = plt.Circle(start, 3, color='g')
    ax.add_patch(end_dot)

    line = plt.Line2D(start, end, 3, color='g')
    ax.add_patch(line)

    return fig, ax

def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)

def visuSym(img, anno):
    ''' Visualization of the Symmetry Labeling with Roughly the Same Size'''
    img_w, img_h = img.shape[1], img.shape[0] 
    result = img.copy()
    result = ResizeWithAspectRatio(result, width=800)
    new_w, new_h = result.shape[1], result.shape[0] 

    # fig, ax = plt.subplots(figsize=(12,8), dpi=300)
    # ax.imshow(result)
    for class_name, data in anno.items():
        if class_name.split(' ')[0] == 'Rotation': 
            rot_center = (int(data[0]*new_w/img_w), int(data[1]*new_h/img_h))

            result = cv2.circle(result, rot_center, radius= 5, color=(255,255,255), thickness=3)
            result = cv2.circle(result, rot_center, radius= 5, color=(0,0,255), thickness=2)
        elif class_name.split(' ')[0] == 'Reflection': 

            start = (int(data[0]*new_w/img_w), int(data[1]*new_h/img_h))
            end = (int(data[2]*new_w/img_w), int(data[3]*new_h/img_h))

            result = cv2.line(result, start, end, color=(255, 255, 255), thickness= 3)
            result = cv2.line(result, start, end, color=(0, 255, 0), thickness= 2)

    return result