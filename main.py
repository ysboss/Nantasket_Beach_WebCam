from __future__ import print_function
import os, time
import cv2
import numpy as np
import urllib.request
from ipywidgets import Button, Box, Text, IntSlider, VBox, Label, Layout, Tab, Dropdown
from PIL import ImageFont, ImageDraw, Image
from datetime import datetime
import pytz 

folderText = Text(value = 'images')
intervalSlider = IntSlider(value = 0, min = 1, max = 60, step = 1)
totalTimeSlider = IntSlider(value = 0, min = 1, max = 120, step = 1)
downloadBtn = Button(description = 'Download')
timezoneList = Dropdown(options=pytz.all_timezones) 

def download_btn_clicked(a):
    rootfolder = folderText.value
    interval = intervalSlider.value
    totalTime = totalTimeSlider.value
    
    if not os.path.exists(rootfolder):
        os.makedirs(rootfolder)
    
    for gap in range (int(totalTime*60/interval)):
        process("http://173.166.108.66/mjpg/video.mjpg", rootfolder)
        time.sleep(interval*60)
    
downloadBtn.on_click(download_btn_clicked)    
  
def process(imageurl, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    try:
        stream=urllib.request.urlopen(imageurl)
        bytes=b''
        flag = True
        while flag:
            bytes+=stream.read(1024)
            a = bytes.find(b'\xff\xd8') # JPEG start
            b = bytes.find(b'\xff\xd9') # JPEG end
            if a!=-1 and b!=-1:
                jpg = bytes[a:b+2] # actual image
                bytes= bytes[b+2:] # other informations
                now_time = datetime.now(pytz.timezone(timezoneList.value))
                imageName = 'nantasket_' + now_time.strftime("%b-%d-%Y-%H-%M-%S") + '.jpg'
                # decode to colored image ( another option is cv2.IMREAD_GRAYSCALE )
                img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR) 
                cv2.imwrite(folder + '/' + imageName, img)
                flag = False
  
        print ("Successfully download " + imageName)
        
        
    except Exception as ex_results:
        print ('Error: ', ex_results)
        
    pass

tab0_items = [
    Box([Label(value = "Saving Image Folder:", layout = Layout(width = '200px')), folderText]),
    Box([Label(value = "Downloading Interval (min):", layout = Layout(width = '200px')), intervalSlider]),
    Box([Label(value = "Downloading Time (hr):", layout = Layout(width = '200px')), totalTimeSlider]),
    Box([Label(value = "Time Zone:", layout = Layout(width = '200px')), timezoneList]),
    Box([downloadBtn])
]
tab0Box = VBox(tab0_items)


imgsDicText = Text()
videoNameText = Text(value = 'output')
fpsSlider = IntSlider(value = 2, min = 2, max = 30, step = 2)
cvtBtn = Button(description = 'Convert')


def imgCvtVideo(img_dir,fps):
    images = []
    for img in os.listdir(img_dir):
        if img.endswith('.jpg'):
            images.append(img)
    images.sort()
    img_path = os.path.join(img_dir, images[0])
    frame = cv2.imread(img_path)
    height, width, channels = frame.shape
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(videoNameText.value + '.mp4', fourcc, fps, (width, height))
    for img in images:
        img_path = os.path.join(img_dir, img)
        frame = cv2.imread(img_path)
        out.write(frame)
    
    out.release()
    
def convert_btn_clicked(a):
    try:
        imgCvtVideo(imgsDicText.value, fpsSlider.value)
        print ("Successfully convert images to " + videoNameText.value + '.mp4')
    
    except Exception as ex_results:
        print ('Error: ', ex_results)
    
cvtBtn.on_click(convert_btn_clicked)


    
tab1_items = [
    Box([Label(value = "Images Folder:", layout = Layout(width = '200px')), imgsDicText]),
    Box([Label(value = "Video Name:", layout = Layout(width = '200px')), videoNameText]),
    Box([Label(value = "Frames Per Second:", layout = Layout(width = '200px')), fpsSlider]),
    Box([cvtBtn])
]
tab1Box = VBox(tab1_items)





tab_nest = Tab()
tab_nest.children = [tab0Box, tab1Box]
tab_nest.set_title(0, 'Download')
tab_nest.set_title(1, 'ImgsToVideo')

display(tab_nest)
    
    
