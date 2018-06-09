# CS 168 Spring 2018 Class Project

# Ali Hatamizadeh , Sean Kim

In this class project, we compared the level-set method and deep learning for the task of human lung segmentation and identify the strengths and weaknesses of each technique. 

We have created an interactive tool, which is based on the morphological level-set method, than can be used for any medical image segmentation application. Here's the demo for lung segmentaion: 


![alt text](https://github.com/ahatamiz/CS168_Project/blob/master/ezgif.com-crop.gif)



In order to use the interactive segmentation tool, first intall all the requirments and then initiate he GUI accordingly as explaind: 

# Installation 

pip install -r requirements.txt

# Command-Line 

python gui.py

# General Instructions 

The interactive tool accepts an input image file in the format of Nifty (nii.gz). The user should select a point inside the area of interest to be segmented and click on the run button for the segmentation process to start. The output of saving the segmentation can be specified in GUI.



