import os
import datetime
import numpy as np
import matplotlib.pyplot as plt 
import schedule
import time
import datetime
from PIL import Image, ImageDraw
import numpy as np

# file uploades
import boto3
from botocore.exceptions import NoCredentialsError

ACCESS_KEY = 'AKIAJXWZR5NN64B5ATDQ'
SECRET_KEY = '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'


# mongo db configuration
import pymongo
import dns

client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.d7sgl.mongodb.net/Forest_Protect?retryWrites=true&w=majority")
database = client['Forest_Protect']

# this is to handle aws
def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def getimages():
    current_year = datetime.date.today().year
    current_month = datetime.date.today().month
    block = 1
    name_of_the_table = str(current_year) + "_" + str(current_month-1) + "_" + str(block)
    col = database[name_of_the_table]
    """
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts)
    time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    name = time.replace(":", "-")
    im.save(name+ '.png')
    """
    name = "recreated_image"
    name_url = name + "_" + str(current_year) + "_" + str(current_month-1) + "_" + str(block)
    upload_to_aws(name+'.png', 'karapinchauploadsdata', 'forest/'+name_url+'.png')
    #os.remove(name+ '.png')
    #print("File Removed!")
    url = 'https://karapinchauploadsdata.s3.us-east-2.amazonaws.com/forest/' + name_url+'.png'
    dic = {"name": name+'.png', "url": str(url), "year":str(current_year), "month":str(current_month), "block":str(block)}
    x = col.insert_one(dic)
    print(x)
"""
schedule.every(1).minutes.do(getimages)
while 1:
      schedule.run_pending()
      time.sleep(1)     
"""
def main():
    print("hey im in the main method") 
    getimages()
 
if __name__=="__main__": 
    main() 

