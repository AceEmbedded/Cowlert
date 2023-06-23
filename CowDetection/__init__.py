import torch
import os,numpy as np
import cv2
cd = os.curdir



workin_dir = os.getcwd()
path_location = workin_dir
filename = "cow"
model= []
model = torch.hub.load('ultralytics/yolov5', 'custom', path='/Users/parallelscore/Desktop/projects/ACE/Cowlert/person.pt'.format(path_location,filename))



def cow(npimg):
    original = npimg
    imgs = [npimg[..., ::-1]]
    # Inference
    results = model(imgs).xyxy[0].cpu().numpy()
    allcows = {'bb': [], "confidence":[]}
    for p in results:
        if p[-1] == 0:
            x, y, x1, y1 = [round(i) for i in p[:4]]
            if p[4] > 0.5:
                allcows["bb"].append([x, y, x1-x, y1-y])
                allcows["confidence"].append(p[4])
    return allcows
  


def plot_many_box(frame, bbs, color=(128, 128, 128), label="cow", line_thickness=3):
    label = label*len(bbs)
    for i, bb in enumerate(bbs):
        x, y, w, h = bb
        pt1 = (x, y)
        pt2 = (x + w, y + h)
        frame = cv2.rectangle(frame, pt1, pt2, color, 2)
        frame = cv2.putText(frame, label[i], pt1, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, line_thickness)
    return frame
