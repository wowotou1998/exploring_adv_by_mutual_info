# import hub
# ds = hub.load("hub://activeloop/tiny-imagenet-validation")
# dataloader = ds.pytorch(num_workers=0, batch_size=4, shuffle=False)

# -*- coding: utf-8 -*-
"""TinyImageNetLoader.ipynb

Automatically generated by Colaboratory.


"""

# loads images as 3*64*64 tensors

# !wget http://cs231n.stanford.edu/tiny-imagenet-200.zip
# !unzip -q tiny-imagenet-200.zip

import torch
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
import os, glob
from torchvision.io import read_image, ImageReadMode
from PIL import Image

batch_size = 100
root_path = ''


def get_id_dict():
    id_dict = {}
    for i, line in enumerate(open('./DataSet/tiny-imagenet-200/wnids.txt', 'r')):
        id_dict[line.replace('\n', '')] = i
    # print(id_dict)
    return id_dict


class TrainTinyImageNetDataset(Dataset):
    def __init__(self, id, transform=None):
        self.filenames = glob.glob("./DataSet/tiny-imagenet-200/train/*/*/*.JPEG")
        self.transform = transform
        self.id_dict = id

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        img_path = self.filenames[idx]
        img_path = img_path.replace("\\", "/")
        image = Image.open(img_path).convert('RGB')
        label = self.id_dict[img_path.split('/')[4]]
        if self.transform:
            image = self.transform(image)
        return image, label


class TestTinyImageNetDataset(Dataset):
    def __init__(self, id, transform=None):
        self.filenames = glob.glob("./DataSet/tiny-imagenet-200/val/images/*.JPEG")
        self.transform = transform
        self.id_dict = id
        self.cls_dic = {}
        for i, line in enumerate(open('./DataSet/tiny-imagenet-200/val/val_annotations.txt', 'r')):
            a = line.split('\t')
            img, cls_id = a[0], a[1]
            self.cls_dic[img] = self.id_dict[cls_id]

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        img_path = self.filenames[idx]
        # 对路径做一点修改, 路径中含有太多的\\
        img_path = img_path.replace("\\", "/")
        # 无论是单通道还是3通道，一律转成RGB 3通道
        image = Image.open(img_path).convert('RGB')
        label = self.cls_dic[img_path.split('/')[-1]]
        if self.transform:
            # transform 中 不能有多个totensor
            image = self.transform(image)
        return image, label


if __name__ == '__main__':
    # transform = transforms.Normalize((122.4786, 114.2755, 101.3963), (70.4924, 68.5679, 71.8127))
    data_tf_tiny_imagenet = transforms.Compose([
        transforms.RandomCrop(64, padding=4, fill=0, padding_mode='constant'),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
    ])
    trainset = TrainTinyImageNetDataset(id=get_id_dict(), transform=data_tf_tiny_imagenet)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size, shuffle=True, num_workers=0)

    testset = TestTinyImageNetDataset(id=get_id_dict(), transform=data_tf_tiny_imagenet)
    testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size, shuffle=False, num_workers=0)
    print('hello')
    X, Y = next(iter(trainloader))
    import matplotlib.pyplot as plt
    import numpy as np

    image_i = X[0].permute(1, 2, 0).numpy()
    plt.imshow(image_i)
    plt.show()
