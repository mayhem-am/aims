import cv2
import os
import io
import requests
import json
url_api = "https://api.ocr.space/parse/image"

def table_data_extract(image_file,actcolumns):
    _, compressedimage = cv2.imencode(".jpg", image_file)
    file_bytes = io.BytesIO(compressedimage)
    try:
        result = requests.post(url_api,
                           files={"screenshot.jpg": file_bytes},
                           data={"apikey": "8b2b1e3c0e88957",
                                 "language": "eng", "isOverlayRequired": True, "detectOrientation": False, 'isTable': True, "scale": True})
    except Exception as e:
        print("Check Internet Connection")
        exit()
    result = result.content.decode()
    result = json.loads(result)
    allitems = []
    if result != None and "ParsedResults" in result:
        parsed_results = result.get("ParsedResults")[0]
        text_detected = parsed_results.get("ParsedText")
        table_items = text_detected.strip().split('\n')
        for item in table_items:
            fields = item.strip().split('\t')
            if len(fields) == actcolumns:
                flag=0
                for ele in fields:
                    if ele == "" or " " in ele:
                        flag=1
                        break
                if flag==0:allitems.append(fields)
    return allitems

def itemparser(allitems,num_columns):
    products = []
    for item in allitems:
        ll = [None for _ in range(num_columns)]
        ll[0]= item[0].lower()
        try:
            x = item[1]
            x = x.replace('$','')
            x = x.split('.')[0]
            x=  int(x)
        except Exception as e:
            continue
        ll[1]=x
        try:
            x = int(item[2])
        except Exception as e:
            continue
        ll[2]=x
        try:
            x = item[3]
            x = x.replace('$', '')
            x = x.split('.')[0]
            x = int(x)
        except Exception as e:
            continue
        ll[3]=x
        products.append(ll)
    return products

