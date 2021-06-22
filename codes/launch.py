import time
import os
import up_down # importing upload.py
import recreate # importing recreate.py
import cut_area

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

import torchvision
import torchvision.transforms as transforms

torch.set_printoptions(linewidth=120)
torch.set_grad_enabled(True)

from torch.autograd import Variable
from torch.utils.data import DataLoader

from PIL import Image
#import pymongo  #####################
from urllib.request import urlopen#################
import cv2
import urllib.parse

class Model(nn.Module):
    
    def __init__(self):
        super().__init__()
        self.pretrained_model = torchvision.models.resnet18(pretrained=True)
        classifier = [
            nn.Linear(self.pretrained_model.fc.in_features, 17)
        ]
        self.classifier = nn.Sequential(*classifier)
        self.pretrained_model.fc = self.classifier

    def forward(self, x):
        x = self.pretrained_model(x)
        return F.sigmoid(x)

@torch.no_grad()
def get_all_preds(model, loader):
    all_preds = torch.tensor([])
    for batch in loader:
        images = batch

        preds = model(images) # here network is the model that we usually used 
        all_preds = torch.cat(
            (all_preds, preds)
            ,dim=0
        )
    return all_preds

def Nmaxelements(list1): 
    final_list = [] 
  
    for i in range(0, 3):  
        max1 = 0
          
        for j in range(len(list1)):      
            if list1[j] > max1: 
                max1 = list1[j]; 
                  
        list1.remove(max1); 
        final_list.append(max1) 
          
    return final_list[2], final_list

def launch():

    raw_transforms = transforms.Compose([transforms.Resize(224),
                                        transforms.ToTensor()]) 

    PATH = "entire_model_resnet18.pt" 
    model = Model()
    model.load_state_dict(torch.load(PATH))
    model.eval()

    #SampleTable = Database.data # Table 
    #data = SampleTable.find( {} )
    data = up_down.download_images_for_checking()
    i = 0

    with torch.no_grad():
        # for checking purposes these files are created
        file1 = open("final_output_online.txt","w") 
        label_names = ["haze", "slash_burn", "selective_logging", "primary", "artisinal_mine", "bare_ground", "blooming", "partly_cloudy", "road", "water", "habitation", "blow_down", "cultivation", "conventional_mine", "agriculture", "cloudy", "clear"]
        #                  1         2                  3               4              5               6            7             8            9       10          11           12             13                 14              15           16        17
        for x in data: 
            # in the original system this should be the links to the photos
            #img_name = os.path.join('raw', str(i)) # data/train-jpg/train_1111
            #img = Image.open(img_name + '.jpg').convert('RGB')
            #print(x)
            i = i + 1
            url = x["url"]
            url = url.replace(" ", "+")  
            img = Image.open(urlopen(url)).convert('RGB')
            img = raw_transforms(img) # transformation is done here as mentioned in the main programm
            print(img.size())
            #img = cv2.resize(img, (224, 224))
            #import matplotlib.pyplot as plt
            #plt.imshow(img)
            #cv2.imwrite('fuck.png',img)
            pred = model(img.unsqueeze(dim=0))
            
            sum = 0
            for j in range(17):
                if(j != 3):
                    sum = sum + pred.squeeze()[j]
            mean = sum / 16
            #print(i)
            #print(mean)
            #print(pred.squeeze()) 
            temp_list = []
            for n in range(17):
                temp_list.append(pred.squeeze()[n])
            
            val, length = Nmaxelements(temp_list)
            #print("length", length)
            #print("min value", val)
            #final_list = []
            #file1.write(str(i)+"   ")
            destruct = 0 # this is to check whether that in the picture there is an destruction

            for k in range(17):
                #print(pred.squeeze()[k])
                if (pred.squeeze()[k] >= val):
                    #final_list.append(1)
                    file1.write(str(pred.squeeze()[k]))
                    file1.write(label_names[k])
                    file1.write(" & ") 
                    if( k == 9 or k == 11 or k == 13 or k == 15 ):
                        destruct = 1    

                #else:
                    #final_list.append(0)  
                
            file1.write("\n\n")    

            #print(final_list) 
            #print("                                     ")

            year = x["year"]
            month = x["month"]
            block = x["block"]
            name_of_the_collection = year + "_" + month + "_" + block
            #name_of_the_collection = "data"
            file_exits = 0
            if(destruct == 1):
                # call to photo recreate and spend the time to recreate the image
                recreate.create_before_cut(name_of_the_collection)
                # wait until the recreated image has been created
                while(file_exits == 0):
                    data = up_down.download_image_for_checking_the_existance(block)
                    if(data["name"] == "recreated_image.png"):
                        print("image exits")
                        file_exits = 1
                # call to cut area detection
                return_val = cut_area.mark_cut_area(i)
                if(return_val == 1):
                    print("destructed")
                    file1.write("destructed")

                else:
                    print("some thing went wrong") 
                    file1.write("error on the system")   
            else:
                # call to photo recreate and spend the time to recreate the image
                recreate.create_before_cut(name_of_the_collection)
                # wait until the recreated image has been created
                while(file_exits == 0):
                    data = up_down.download_image_for_checking_the_existance(block)
                    if(data["name"] == "recreated_image.png"):
                        file_exits = 1

                file1.write("not destructed")

        file1.close()             

def main():
    #print("hey im in the main method") 
    """
    connection_url = 'mongodb+srv://admin:admin@cluster0.d7sgl.mongodb.net/Forest_Protect?retryWrites=true&w=majority'
    client = pymongo.MongoClient(connection_url) 
    Database = client.get_database('Forest_Protect') # Database
    launch(Database) 
    """
    launch()
 
if __name__=="__main__": 
    main()         