import os
import torch
import pandas as pd
import numpy as np
from torch.utils.data import Dataset
from PIL import Image

"""
in the planetdata method all the methods are called when creating the object
this is common method of creating the data provision in pytorch
"""

def get_labels(fname):
    with open(fname,'r') as f:
        labels = [t.strip() for t in f.read().split(',')] # seperate from the comma and all the white spaces are removed in the word
        
    # getting label number and name for the label as mentioned in the text file and return dictionaries 
    # for dictonaries it is needed both id and the value which is given by the enumerate function
    labels2idx = {t:i for i,t in enumerate(labels)}
    idx2labels = {i:t for i,t in enumerate(labels)}
    # return list, dic, dic
    return labels,labels2idx,idx2labels

class ForestData(Dataset):
    # all these three methods are called automatically first one is the constructor and other two methods are magic methods

    def __init__(self, csv_file, root_dir, labels_file, transform=None):
        self.data = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.labels, self.labels2idx, self.idx2labels = get_labels(labels_file)
        self.n_labels = len(self.labels)
        self.transform = transform


    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir, self.data.iloc[idx, 0]) # data/train-jpg/train_1111
        img = Image.open(img_name + '.jpg').convert('RGB')
        labels = self.data.iloc[idx, 1] # this is the label given in words
        target = torch.zeros(self.n_labels)
        label_idx = torch.LongTensor([self.labels2idx[tag] for tag in labels.split(' ')])
        target[label_idx] = 1
        if self.transform:
            img = self.transform(img) # transformation is done here as mentioned in the main programm
        return img, target
