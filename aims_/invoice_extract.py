"""
contains function to extract text from image
input : image_file, coordinates file
output : list of all the text (can be made to JSON as well)
"""

# import libraries
import cv2
import matplotlib.pyplot as plt
import pytesseract
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from pytesseract import Output
from table_detect import find_contours
from text_recog import extract_table_data
import pandas as pd
import json,math

def get_annotations_xlsx(path):
    """
    Input:
        @param path - The full path to the excel template
    
    Output:
        A dictionary of the following format

        {
            "page 1":[
                {
                    "label1 name":(x1,y1,x2,y2),
                    "label2 name": (x1,y1,x2,y2)
                }
            ]

            "page 2":[
                {
                    "label1 name":(x1,y1,x2,y2),
                    "label2 name": (x1,y1,x2,y2)
                }
            ]
        }
    """


    #path = './Sample images/Data.csv'
    df = pd.read_excel(path,header=None)
    
    annotate_dict = {}
    number_of_rows = df.shape[0]
    # print(number_of_rows)
    for r in range(1,number_of_rows):
        row1 = df.iloc[r,:]
        # print(type(row1))
        curr_row = row1.tolist()
        # print(type(curr_row))
        # print(curr_row)
        # print(row1['height'].values[0])
        # print(row1)
        annotate_dict['page '+str(r+1)] = []
        label = curr_row[4]
        x1 = int(curr_row[2])
        x2 = x1 + int(curr_row[0])
        y1 = int(curr_row[3])
        y2 = y1 + int(curr_row[1])
        # print(type(y2), type(label))
        annotate_dict['page '+str(r+1)].append(
                    {
                        label:(x1,y1,x2,y2)
                    }
                )
    return annotate_dict


def plot_image(img):
    """
    Input:
        @param img - sub image for which text has to be predicted from tesseract

    Output:
        Image with title predicted by tesseract
        plt.imshow(img)
        plt.title(text)
    """

    import cv2 as cv
    import numpy as np
    from matplotlib import pyplot as plt

    text = pytesseract.image_to_string(img)
    """
    plt.imshow(img)
    #Set title of the image as the extracted text
    plt.title(text)
    plt.show()
    """
    return text


def predict_invoice(path,excel_path):


    img = cv.imread(path,0)
    """
    plt.imshow(img)
    plt.show()
    """
    annotations = get_annotations_xlsx(excel_path)

    # for now the text will be in list
    # further change it to json or as required
    data = []
    columns = 0
    
    
    for k in annotations.keys():
        annotations_list = annotations[k]
        for i in range(len(annotations_list)):
            
            for label in annotations_list[i]:
                x1,y1,x2,y2 = annotations_list[i][label]

                sub_image = img[y1:y2,x1:x2]
                
                if label != "Start of Table" and label!='No of Columns':
                    temp_dict = {}
                    text = plot_image(sub_image)
                    temp_dict[label] = text
                    data.append(temp_dict)
                    
                if label == 'No of Columns':
                    columns = x1
                
                """
                text = plot_image(sub_image)
                data.append(text)
                """
    table_data = extract_table_data(path, columns)   

    return (data,table_data) 


image_path = ''
excel_path = ''

(data, table_data) = predict_invoice(image_path, excel_path)
