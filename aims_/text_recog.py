import pytesseract
from pytesseract import Output
import numpy as np
import regex as re
import cv2
import os

"""

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

image_path = 'static/invoices/invoice2.jpg'
large = cv2.imread(image_path)
print(large.shape[0],large.shape[1])
h = large.shape[0]
w = large.shape[1]
rgb = cv2.resize(large, (700, 1000))   
# cv2.imwrite("Annotate.jpg", rgb)

cv2.imshow('rects', rgb)
cv2.waitKey(0)
cv2.destroyAllWindows()


small = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
img = large
img2 = small
# cv2.imwrite("in.jpg",small)
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
kernel = np.ones((1, 9), np.uint8)
grad = cv2.morphologyEx(small, cv2.MORPH_GRADIENT, kernel)
_, bw = cv2.threshold(grad, 0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 1))
connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (12,1))
#connected = cv2.dilate(connected,kernel2, iterations = 1)

# cv2.imwrite("/Users/nishith/cv/Lib/site-packages/i1.jpg",connected)
# using RETR_EXTERNAL instead of RETR_CCOMP
contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

mask = np.zeros(bw.shape, dtype=np.uint8)
count=0

TEXT = list()
abc = np.copy(rgb)
tmp = np.copy(rgb)
for idx in range(len(contours)):
    x, y, w, h = cv2.boundingRect(contours[idx])
    mask[y:y+h, x:x+w] = 0
    cv2.drawContours(mask, contours, idx, (255, 255, 255), -1)
    r = float(cv2.countNonZero(mask[y:y+h, x:x+w])) / (w * h)
    
    if r > 0.4 and w > 2 and h > 2:    #hardcoded
        cv2.rectangle(abc, (x-2, y-2), (x+w+2, y+h+2), (0, 0, 255), 1)
        #sub_image = tmp[y-2:y+h+2, x-2:x+w+2]
        #cv2.imshow("out", sub_image)
        #cv2.waitKey()
        TEXT.append((x,y,w,h))
        #d = pytesseract.image_to_data(sub_image, output_type=Output.DICT, lang='eng', config='--psm 6')
        #print(d['text'])
        


# cv2.imwrite("/Users/nishith/cv/Lib/site-packages/mod_img.jpg",abc)
        
cv2.imshow('rects', abc)
cv2.waitKey(0)
cv2.destroyAllWindows()


TEXT.sort(key = lambda x:(x[1], x[0]))
grps = list()
i = 0
while i < len(TEXT)-1:
    tlist = list()
    tlist.append(TEXT[i])
    while i < len(TEXT)-1 and abs((TEXT[i][1]+TEXT[i][3]//2)-(TEXT[i+1][1]+TEXT[i+1][3]//2))<=10:
        tlist.append(TEXT[i+1])
        i+=1
    grps.append(tlist)
    if i==len(TEXT)-2 and TEXT[i]!=TEXT[i+1]:
        tlist = list()
        tlist.append(TEXT[i+1])
        grps.append(tlist)
    i+=1
    
tmp2 = np.copy(rgb)
new_crd = list()
for txts in grps:
    xmin = min(txts, key = lambda x:x[0])[0]
    ymin = min(txts, key = lambda x:x[1])[1]
    x1, x2, x3, x4  = max(txts, key = lambda x:x[0]+x[2])[:]
    xmax = x1 + x3
    y1, y2, y3 ,y4 = max(txts, key = lambda x:x[1]+x[3])[:]
    ymax = y2 + y4
    new_crd.append((xmin, ymin, xmax, ymax))
    cv2.rectangle(tmp2, (xmin-1, ymin-1), (xmax+1, ymax+1), (0, 0, 255), 1)
    
    
cv2.imshow("rows", tmp2)
cv2.waitKey()
cv2.destroyAllWindows()


NO_OF_COLS = 3   #*************     MENTION NO. OF COLS ****************************
tmp3 = np.copy(rgb)
#***********************************************************************************************************

def colfilter(crds):
    x,y,x1,y1 = crds
    sub_image1 = tmp3[y:y1,x:x1]
    sub_image = cv2.cvtColor(sub_image1, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(sub_image, 0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    kernel = np.ones((3, 11), np.uint8)
    th = cv2.erode(th, kernel, iterations = 2)
    th = np.pad(th, ((10,10),(10,10)), mode = 'constant',constant_values = ((255,255),(255,255)))
    th = 255-th
    contours, hierarchy = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    mask = np.zeros(th.shape, dtype=np.uint8)
    ct=0
    sbi = np.pad(sub_image1, ((10,10),(10,10),(0,0)), mode = 'constant',constant_values = ((255,255),(255,255),(0,0)))
    li = list()
    for idx in range(len(contours)):
        x, y, w, h = cv2.boundingRect(contours[idx])
        mask[y:y+h, x:x+w] = 0
        cv2.drawContours(mask, contours, idx, (255, 255, 255), -1)
        r = float(cv2.countNonZero(mask[y:y+h, x:x+w])) / (w * h)
        if r > 0.4 and w > 2 and h > th.shape[0]//4:
#            cv2.rectangle(sbi, (x,y),(x+w, y+h), (0,0,255), 1)
            li.append((x,y,w,h))
            ct+=1

    li.sort(key = lambda x:-x[2]-x[3])
    i = 0
    while i < len(li):
        x1, y1, w1, h1 = li[i]
        flg = False
        for j in range(len(li)):
            x , y, w, h = li[j]
            if i==j:
                continue
            if x1>=x and y1>=y and x1+w1<=x+w:
                li.remove(li[i])
                flg = True
                break
        if not flg:
            i+=1            
    for ele in li:
        x,y,w,h = ele
        cv2.rectangle(sbi, (x,y),(x+w, y+h), (0,0,255), 1)
#    cv2.imshow("i3", sbi)         #Uncomment to see each img strip and b-box
#    cv2.imshow("i4", 255-th)
#    cv2.waitKey()
#    print(ct,end = '  ')
#    print(len(li))
    if len(li) == NO_OF_COLS:
        return True
    else:
        return False
    
#*************************************************************************************************************
    
new_crd = list(filter(colfilter, new_crd))
table_data = []
tmp3 = np.copy(rgb)
for crds in new_crd:
    x,y,x1,y1 = crds
    sub_image = tmp3[y-2:y1+2, x-2:x1+2]
    d = pytesseract.image_to_data(sub_image, output_type=Output.DICT, lang='eng', config='--psm 6')
    cv2.rectangle(tmp3, (x-1, y-1), (x1+1, y1+1), (0, 0, 255), 1)
    temp_text = ''
    for t in d['text']:
        #print(t, end='  ')
        temp_text += t + ' '
    table_data.append(temp_text.strip())   
    
print(table_data)    

# cv2.imshow("I2", tmp3)
# cv2.waitKey()
# cv2.destroyAllWindows()

# cv2.imwrite("result.jpg", tmp3)
"""    
    
def extract_table_data(image_file, columns):    
    
    image_path = 'static/invoices/invoice2.jpg'
    large = cv2.imread(image_file)
    # print(large.shape[0],large.shape[1])
    h = large.shape[0]
    w = large.shape[1]
    rgb = cv2.resize(large, (700, 1000))   
    # cv2.imwrite("Annotate.jpg", rgb)
    """
    cv2.imshow('rects', rgb)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    """
    
    small = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
    img = large
    img2 = small
    # cv2.imwrite("in.jpg",small)
    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    kernel = np.ones((1, 9), np.uint8)
    grad = cv2.morphologyEx(small, cv2.MORPH_GRADIENT, kernel)
    _, bw = cv2.threshold(grad, 0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 1))
    connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
    connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (12,1))
    #connected = cv2.dilate(connected,kernel2, iterations = 1)
    
    # cv2.imwrite("/Users/nishith/cv/Lib/site-packages/i1.jpg",connected)
    # using RETR_EXTERNAL instead of RETR_CCOMP
    contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    mask = np.zeros(bw.shape, dtype=np.uint8)
    count=0
    
    TEXT = list()
    abc = np.copy(rgb)
    tmp = np.copy(rgb)
    for idx in range(len(contours)):
        x, y, w, h = cv2.boundingRect(contours[idx])
        mask[y:y+h, x:x+w] = 0
        cv2.drawContours(mask, contours, idx, (255, 255, 255), -1)
        r = float(cv2.countNonZero(mask[y:y+h, x:x+w])) / (w * h)
        
        if r > 0.4 and w > 2 and h > 2:    #hardcoded
            cv2.rectangle(abc, (x-2, y-2), (x+w+2, y+h+2), (0, 0, 255), 1)
            #sub_image = tmp[y-2:y+h+2, x-2:x+w+2]
            #cv2.imshow("out", sub_image)
            #cv2.waitKey()
            TEXT.append((x,y,w,h))
            #d = pytesseract.image_to_data(sub_image, output_type=Output.DICT, lang='eng', config='--psm 6')
            #print(d['text'])
            
    
    
    # cv2.imwrite("/Users/nishith/cv/Lib/site-packages/mod_img.jpg",abc)
    """        
    cv2.imshow('rects', abc)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    """
    
    TEXT.sort(key = lambda x:(x[1], x[0]))
    grps = list()
    i = 0
    while i < len(TEXT)-1:
        tlist = list()
        tlist.append(TEXT[i])
        while i < len(TEXT)-1 and abs((TEXT[i][1]+TEXT[i][3]//2)-(TEXT[i+1][1]+TEXT[i+1][3]//2))<=10:
            tlist.append(TEXT[i+1])
            i+=1
        grps.append(tlist)
        if i==len(TEXT)-2 and TEXT[i]!=TEXT[i+1]:
            tlist = list()
            tlist.append(TEXT[i+1])
            grps.append(tlist)
        i+=1
        
    tmp2 = np.copy(rgb)
    new_crd = list()
    for txts in grps:
        xmin = min(txts, key = lambda x:x[0])[0]
        ymin = min(txts, key = lambda x:x[1])[1]
        x1, x2, x3, x4  = max(txts, key = lambda x:x[0]+x[2])[:]
        xmax = x1 + x3
        y1, y2, y3 ,y4 = max(txts, key = lambda x:x[1]+x[3])[:]
        ymax = y2 + y4
        new_crd.append((xmin, ymin, xmax, ymax))
        cv2.rectangle(tmp2, (xmin-1, ymin-1), (xmax+1, ymax+1), (0, 0, 255), 1)
        
    """    
    cv2.imshow("rows", tmp2)
    cv2.waitKey()
    cv2.destroyAllWindows()
    """
    
    NO_OF_COLS = columns   #*************     MENTION NO. OF COLS ****************************
    tmp3 = np.copy(rgb)
    #***********************************************************************************************************
    
    def colfilter(crds):
        x,y,x1,y1 = crds
        sub_image1 = tmp3[y:y1,x:x1]
        sub_image = cv2.cvtColor(sub_image1, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(sub_image, 0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        kernel = np.ones((3, 11), np.uint8)
        th = cv2.erode(th, kernel, iterations = 2)
        th = np.pad(th, ((10,10),(10,10)), mode = 'constant',constant_values = ((255,255),(255,255)))
        th = 255-th
        contours, hierarchy = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        mask = np.zeros(th.shape, dtype=np.uint8)
        ct=0
        sbi = np.pad(sub_image1, ((10,10),(10,10),(0,0)), mode = 'constant',constant_values = ((255,255),(255,255),(0,0)))
        li = list()
        for idx in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[idx])
            mask[y:y+h, x:x+w] = 0
            cv2.drawContours(mask, contours, idx, (255, 255, 255), -1)
            r = float(cv2.countNonZero(mask[y:y+h, x:x+w])) / (w * h)
            if r > 0.4 and w > 2 and h > th.shape[0]//4:
    #            cv2.rectangle(sbi, (x,y),(x+w, y+h), (0,0,255), 1)
                li.append((x,y,w,h))
                ct+=1
    
        li.sort(key = lambda x:-x[2]-x[3])
        i = 0
        while i < len(li):
            x1, y1, w1, h1 = li[i]
            flg = False
            for j in range(len(li)):
                x , y, w, h = li[j]
                if i==j:
                    continue
                if x1>=x and y1>=y and x1+w1<=x+w:
                    li.remove(li[i])
                    flg = True
                    break
            if not flg:
                i+=1            
        for ele in li:
            x,y,w,h = ele
            cv2.rectangle(sbi, (x,y),(x+w, y+h), (0,0,255), 1)
    #    cv2.imshow("i3", sbi)         #Uncomment to see each img strip and b-box
    #    cv2.imshow("i4", 255-th)
    #    cv2.waitKey()
    #    print(ct,end = '  ')
    #    print(len(li))
        if len(li) == NO_OF_COLS:
            return True
        else:
            return False
        
    #*************************************************************************************************************
        
    new_crd = list(filter(colfilter, new_crd))
    table_data = []
    tmp3 = np.copy(rgb)
    for crds in new_crd:
        x,y,x1,y1 = crds
        sub_image = tmp3[y-2:y1+2, x-2:x1+2]
        d = pytesseract.image_to_data(sub_image, output_type=Output.DICT, lang='eng', config='--psm 6')
        cv2.rectangle(tmp3, (x-1, y-1), (x1+1, y1+1), (0, 0, 255), 1)
        temp_text = ''
        for t in d['text']:
            # print(t, end='  ')
            temp_text += t + ' '
        table_data.append(temp_text.strip())    
        # print()
    return table_data    
    
    # cv2.imshow("I2", tmp3)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    
    # cv2.imwrite("result.jpg", tmp3)
