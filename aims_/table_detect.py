import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import interpolation as inter
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from pytesseract import Output
"""
from utils import convert_key_value_pairs
#from border-removal import border_removal
pytesseract.pytesseract.tesseract_cmd = r'E:DownloadsTesseract OCR\tesseract.exe'
"""

def load_img(path):
    img = cv2.imread(path,1)
    img = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    #img = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    """
    plt.imshow(img)
    plt.title("Loaded image")
    plt.show()
    """
    return img
    
def image_threshold(img):
    _,thresh = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
    """
    plt.imshow(thresh)
    plt.title("Threshold image")
    plt.show()
    """
    return thresh

def image_morphology(img):
    kernel = np.ones((5,5),np.uint8)
    
    #opening = cv2.erode(img,kernel,iterations=2)
    
    #opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    
    #Single line kernel
    kernel = np.ones((4,15),np.uint8)

    #double line kernel
    kernel = np.ones((1,2),np.uint8)
    img = cv2.dilate(img,kernel)
    kernel = np.ones((2,35),np.uint8)
    # single line
    #opening = cv2.erode(img,kernel,iterations=2)
    
    #double line
    opening = cv2.erode(img,kernel,iterations=1)
    """
    plt.imshow(opening)
    plt.title("Morphology open")
    plt.show()
    """
    return opening


    

def group_contours(contours,img):
    y_pos = {}
    # single line
    # min_height = 15
    # max_height = 27

    # double line
    min_height = 5
    max_height = 50


    predicted_text = []
    new_img = img.copy()

    for cnt in contours:
        x,y,w,h = cv2.boundingRect(cnt)
        if h>min_height and h<=max_height:
            h_list = [y+i for i in range(-15,15)]
            flag=False
            for i in h_list:
                if i in y_pos.keys():
                    y_pos[i].append(cnt)
                    flag=True
                    break
            if flag==False:
                y_pos[y] = []
                y_pos[y].append(cnt)
    
    
    for k in y_pos.keys():
        x1=[]
        x2=[]
        y1=[]
        y2=[]
        
        count = 0
        for cnt in y_pos[k]:
            
            count+=1
            x,y,w,h = cv2.boundingRect(cnt)
            x1.append(x)
            x2.append(x+w)
            y1.append(y)
            y2.append(y+h)
        
        x_min = min(x1)
        x_max = max(x2)
        y_min = min(y1)
        y_max = max(y2)
        w = x_max-x_min
        h = y_max-y_min
        new_img = cv2.rectangle(new_img,(x_min-1,y_min-1),(x_max+1,y_max+1),(0,255,0), 1)
        text = find_text_in_image(img[y_min-2:y_max,x_min-2:x_max])
        predicted_text.append(text)
       
    """    
    ############################# Change this path ##############################################
    cv2.imwrite('./Sample images/res.jpg',new_img)
    #############################################################################################
    plt.imshow(new_img)
    plt.title("grouped contours")
    plt.show()
    """

    #print(predicted_text)
    return predicted_text

def correct_skew(path):
    import numpy as np
    image = cv2.imread(path)

    # convert the image to grayscale and flip the foreground
    # and background to ensure foreground is now "white" and
    # the background is "black"
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)

    # threshold the image, setting all foreground pixels to
    # 255 and all background pixels to 0
    thresh = cv2.threshold(gray, 0, 255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # grab the (x, y) coordinates of all pixel values that
    # are greater than zero, then use these coordinates to
    # compute a rotated bounding box that contains all
    # coordinates
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]

    # the `cv2.minAreaRect` function returns values in the
    # range [-90, 0); as the rectangle rotates clockwise the
    # returned angle trends to 0 -- in this special case we
    # need to add 90 degrees to the angle
    if angle < -45:
        angle = -(90 + angle)

    # otherwise, just take the inverse of the angle to make
    # it positive
    else:
        angle = -angle

    # rotate the image to deskew it
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
        flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # draw the correction angle on the image so we can validate it
    cv2.putText(rotated, "Angle: {:.2f} degrees".format(angle),
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # show the output image
    """
    print("[INFO] angle: {:.3f}".format(angle))
    plt.imshow(image)
    plt.title("Input")
    plt.show()

    plt.imshow(rotated)
    plt.title("Rotated")
    plt.show()
    """
    return rotated

def find_text_in_image(img):
    # @param: img - The subimage for which text should be recognized.
    kernel = np.array([[-1,-1,-1], 
                       [-1, 9,-1],
                       [-1,-1,-1]])

    #Sharpen the image for better text recognition
    print(img.shape)
    # sharpened = cv2.medianBlur(img,3)
    # sharpened = cv2.filter2D(img, -1, kernel)
    
    text = pytesseract.image_to_string(image=img)
    """
    plt.imshow(img)
    plt.title(text)
    plt.show()
    """
    return text
    
def find_contours(path):
    
    img = load_img(path)
    thresh = image_threshold(img)
    opening = image_morphology(thresh)
    
    
    contours,hierarchy = cv2.findContours(opening,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    
    min_height_threshold = 5
    max_height_threshold = 12
    
    min_width_threshold = 10
    max_width_threshold = 300
    
    
    
    required_contours = []
    for cnt in contours:
        x,y,w,h = cv2.boundingRect(cnt)
        
        if h>min_height_threshold and h<max_height_threshold and w>min_width_threshold and w<max_width_threshold:
            required_contours.append(cnt)
    
    predicted_text = group_contours(contours,img)
    return predicted_text
    """
    img = cv2.drawContours(img, contours, -1, (0,255,0), 1)
    plt.imshow(img)
    plt.title("Contours in the image")
    plt.show()
    """
    
    
####################################################   MAIN PROGRAM ####################################
    
# path to image
# path = './Sample images/invoice3a.JPG'
# find_contours(path)