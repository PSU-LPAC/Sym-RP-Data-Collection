''' Some visualization functions'''
###
import matplotlib.pyplot as plt
import cv2
###

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
