from importlib.resources import path
from tkinter import *
from tkinter import filedialog, ttk, messagebox
from PIL import ImageTk, Image, ExifTags, ImageChops
from optparse import OptionParser
from datetime import datetime
from matplotlib import image
from prettytable import PrettyTable
import numpy as np
import random
import sys
import cv2
import re
import os

from pyparsing import Opt

from ForgeryDetection import Detect
import copy_move_cfa
import splicing

# Global variables
IMG_WIDTH = 400
IMG_HEIGHT = 400
uploaded_image = None

# copy-move parameters
cmd = OptionParser("usage: %prog image_file [options]")
cmd.add_option('', '--imauto',
               help='Automatically search identical regions. (default: %default)', default=1)
cmd.add_option('', '--imblev',
               help='Blur level for degrading image details. (default: %default)', default=8)
cmd.add_option('', '--impalred',
               help='Image palette reduction factor. (default: %default)', default=15)
cmd.add_option(
    '', '--rgsim', help='Region similarity threshold. (default: %default)', default=5)
cmd.add_option(
    '', '--rgsize', help='Region size threshold. (default: %default)', default=1.5)
cmd.add_option(
    '', '--blsim', help='Block similarity threshold. (default: %default)', default=200)
cmd.add_option('', '--blcoldev',
               help='Block color deviation threshold. (default: %default)', default=0.2)
cmd.add_option(
    '', '--blint', help='Block intersection threshold. (default: %default)', default=0.2)
opt, args = cmd.parse_args()
# if not args:
#     cmd.print_help()
#     sys.exit()


def getImage(path, width, height):
    """
    Function to return an image as a PhotoImage object
    :param path: A string representing the path of the image file
    :param width: The width of the image to resize to
    :param height: The height of the image to resize to
    :return: The image represented as a PhotoImage object
    """
    img = Image.open(path)
    img = img.resize((width, height), Image.ANTIALIAS)

    return ImageTk.PhotoImage(img)


def browseFile():
    """
    Function to open a browser for users to select an image
    :return: None
    """
    # Only accept jpg and png files
    filename = filedialog.askopenfilename(title="Select an image", filetypes=[("image", ".jpeg"),("image", ".png"),("image", ".jpg")])

    # No file selected (User closes the browsing window)
    if filename == "":
        return

    global uploaded_image

    uploaded_image = filename

    progressBar['value'] = 0   # Reset the progress bar
    fileLabel.configure(text=filename)     # Set the path name in the fileLabel

    # Display the input image in imagePanel
    img = getImage(filename, IMG_WIDTH, IMG_HEIGHT)
    imagePanel.configure(image=img)
    imagePanel.image = img

    # Display blank image in resultPanel
    blank_img = getImage("images/output.png", IMG_WIDTH, IMG_HEIGHT)
    resultPanel.configure(image=blank_img)
    resultPanel.image = blank_img

    # Reset the resultLabel
    resultLabel.configure(text="READY TO SCAN", foreground="green")


def copy_move_forgery():
    # Retrieve the path of the image file
    path = uploaded_image
    eps = 60
    min_samples = 2

    # User has not selected an input image
    if path is None:
        # Show error message
        messagebox.showerror('Error', "Please select image")
        return

    detect = Detect(path)
    key_points, descriptors = detect.siftDetector()
    forgery = detect.locateForgery(eps, min_samples)

    # Set the progress bar to 100%
    progressBar['value'] = 100

    if forgery is None:
        # Retrieve the thumbs up image and display in resultPanel
        img = getImage("images/no_copy_move.png", IMG_WIDTH, IMG_HEIGHT)
        resultPanel.configure(image=img)
        resultPanel.image = img

        # Display results in resultLabel
        resultLabel.configure(text="ORIGINAL IMAGE", foreground="green")
    else:
        # Retrieve the output image and display in resultPanel
        img = getImage("images/copy_move.png", IMG_WIDTH, IMG_HEIGHT)
        resultPanel.configure(image=img)
        resultPanel.image = img

        # Display results in resultLabel
        resultLabel.configure(text="Image Forged", foreground="red")
        # cv2.imshow('Original image', detect.image)
        cv2.imshow('Forgery', forgery)
        wait_time = 1000
        while(cv2.getWindowProperty('Forgery', 0) >= 0) or (cv2.getWindowProperty('Original image', 0) >= 0):
            keyCode = cv2.waitKey(wait_time)
            if (keyCode) == ord('q') or keyCode == ord('Q'):
                cv2.destroyAllWindows()
                break
            elif keyCode == ord('s') or keyCode == ord('S'):
                name = re.findall(r'(.+?)(\.[^.]*$|$)', path)
                date = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
                new_file_name = name[0][0]+'_'+str(eps)+'_'+str(min_samples)
                new_file_name = new_file_name+'_'+date+name[0][1]

                vaue = cv2.imwrite(new_file_name, forgery)
                print('Image Saved as....', new_file_name)


def splicing_method():
    # Retrieve the path of the image file
    path = uploaded_image

    # User has not selected an input image
    if path is None:
        # Show error message
        messagebox.showerror('Error', "Please select an image")
        return

    # Call the splicing detection and classification function
    spliced_region_counter=splicing.detect_splicing(path)
    threshold = 0.6 
    if spliced_region_counter >=threshold:
        # Retrieve the thumbs up image and display in resultPanel
        
        resultLabel.configure(text="Image spliced", foreground="red")
        img = getImage("images/imageSpliced.png", IMG_WIDTH, IMG_HEIGHT)
        resultPanel.configure(image=img)
        resultPanel.image = img

    else:
        resultLabel.configure(text="ORIGINAL IMAGE", foreground="green")
        img = getImage("images/notSpliced.png", IMG_WIDTH, IMG_HEIGHT)
        resultPanel.configure(image=img)
        resultPanel.image = img

    # Set the progress bar to 100%
    progressBar['value'] = 100
    




# Initialize the app window
root = Tk()
root.configure(bg="#EEE3CB") 
root.title("IMAGE-FORGERY Detector")
root.iconbitmap('images/favicon.ico')

# Ensure the program closes when window is closed
root.protocol("WM_DELETE_WINDOW", root.quit)

# Maximize the size of the window
root.state("zoomed")

# Add the GUI into the Tkinter window
# GUI(parent=root)

# Label for the results of scan
resultLabel = Label(text="IMAGE FORGERY DETECTOR", font=("sans-serif",50),background="#EEE3CB")
resultLabel.grid(row=0, column=0, columnspan=3)
# resultLabel.grid(row=0, column=1, columnspan=2)

# Get the blank image
input_img = getImage("images/download.png", IMG_WIDTH, IMG_HEIGHT)
middle_img = getImage("images/middle.png", IMG_WIDTH, IMG_HEIGHT)
output_img = getImage("images/arrow-up.png", IMG_WIDTH, IMG_HEIGHT)

# Displays the input image
imagePanel = Label(image=input_img)
imagePanel.image = input_img
imagePanel.grid(row=1, column=0, padx=5)

# Label to display the middle image
middle = Label(image=middle_img)
middle.image = middle_img
middle.grid(row=1, column=1, padx=5)

# Label to display the output image
resultPanel = Label(image=output_img)
resultPanel.image = output_img
resultPanel.grid(row=1, column=2, padx=5)

# Label to display the path of the input image
fileLabel = Label(text="No file selected", fg="grey", font=("Times", 15))
fileLabel.grid(row=2, column=1)
# fileLabel.grid(row=2, column=0, columnspan=2)


# Progress bar
progressBar = ttk.Progressbar(length=500)
progressBar.grid(row=3, column=1)
# progressBar.grid(row=3, column=0, columnspan=2)


# Configure the style of the buttons
s = ttk.Style()
s.theme_use("clam")
s.configure("my.TButton",background="#00DFA2",foreground="black", font=('Times', 15,"bold"),padding="10",border="1px solid")

# Button to upload images
uploadButton = ttk.Button(
    text="Upload Image", style="my.TButton", command=browseFile)
uploadButton.grid(row=4, column=1, sticky="nsew", pady=5)


# Button to run the Splicing detection algorithm
splicingButton = ttk.Button(
    text="Splicing Method", style="my.TButton", command=splicing_method, compound="center")
splicingButton.grid(row=5, column=0, columnspan=1, pady=25)



# Button to run the Copy-Move  detection algorithm
copy_move = ttk.Button(text="Copy-Move Method", style="my.TButton", command=copy_move_forgery,compound="center")
copy_move.grid(row=5, column=2, columnspan=1, pady=20)




# Button to exit the program
style = ttk.Style()
style.configure('W.TButton', font = ('calibri', 12, 'bold'),foreground = 'red')

quitButton = ttk.Button(text="Exit program", style = 'W.TButton', command=root.quit)
quitButton.grid(row=6, column=2, pady=5)
# quitButton.grid(row=6, column=0, columnspan=2, sticky="e", pady=5)

# Open the GUI
root.mainloop()
