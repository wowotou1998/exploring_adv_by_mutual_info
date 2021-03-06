import torchvision.models.alexnet
from torchviz import make_dot
from Models.CIFAR10 import WideResNet
# from torchsummary import summary
import torch
from Models.MNIST import FC_Sigmoid, Net_mnist, FC_2
from Models.CIFAR10 import LeNet_3_32_32, WideResNet, VGG_s, RestNet18, net_cifar10
import argparse

# Model, Model_Name = FC_2(Activation_F=nn.ReLU()), 'FC_2'
# Model, Model_Name = LeNet_3_32_32(), 'LeNet_3_32_32'
# Model, Model_Name = net_cifar10(), 'net_cifar10'
# Model, Model_Name = VGG_s(), 'VGG_s_11'
# Model, Model_Name = resnet18(pretrained=False, num_classes=10), 'resnet18'
# Model, Model_Name = resnet34(pretrained=False, num_classes=10), 'resnet34'
# Model, Model_Name = vgg11(pretrained=False)
Model, Model_Name = WideResNet(depth=1 * 6 + 4, num_classes=10, widen_factor=1, dropRate=0.0), 'WideResNet_CIFAR10'
# # Model, Model_Name = WideResNet_CIFAR10(depth=1 * 6 + 4, num_classes=10, widen_factor=2, dropRate=0.0), 'WideResNet_CIFAR10'
# Model.eval()
# # summary(Model, (3, 32, 32), device="cpu")
#
# x = torch.randn(1, 3, 32, 32).requires_grad_(True)  # 定义一个网络的输入值
# y = Model(x)  # 获取网络的预测值
#
# MyConvNetVis = make_dot(y, params=dict(list(Model.named_parameters()) + [('x', x)]))
# MyConvNetVis.format = "pdf"
# # 指定文件生成的文件夹
# MyConvNetVis.directory = "Structure"
# # 生成文件
# MyConvNetVis.view()

# import hiddenlayer as h

import torch
import hiddenlayer as h

# from torchvision.models import resnet18  # 以 resnet18 为例

myNet = Model  # 实例化 resnet18
x = torch.randn(16, 3, 32, 32)  # 随机生成一个输入
myNetGraph = h.build_graph(myNet, x)  # 建立网络模型图
myNetGraph.theme = h.graph.THEMES['blue']  # blue 和 basic 两种颜色，可以不要
myNetGraph.save(path='Structure/demoModel.pdf', format='pdf')  # 保存网络模型图，可以设置 png 和 pdf 等

# import torch.nn as nn
# import torch
# from Models.CIFAR10 import VGG_s
#
#
# class SE_VGG(nn.Module):
#     def __init__(self, num_classes):
#         super().__init__()
#         self.num_classes = num_classes
#         # define an empty for Conv_ReLU_MaxPool
#         net = []
#
#         # block 1
#         net.append(nn.Conv2d(in_channels=3, out_channels=64, padding=1, kernel_size=3, stride=1))
#         net.append(nn.ReLU())
#         net.append(nn.Conv2d(in_channels=64, out_channels=64, padding=1, kernel_size=3, stride=1))
#         net.append(nn.ReLU())
#         net.append(nn.MaxPool2d(kernel_size=2, stride=2))
#
#         # block 2
#         net.append(nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, stride=1, padding=1))
#         net.append(nn.ReLU())
#         net.append(nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3, stride=1, padding=1))
#         net.append(nn.ReLU())
#         net.append(nn.MaxPool2d(kernel_size=2, stride=2))
#
#         # block 3
#         net.append(nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, padding=1, stride=1))
#         net.append(nn.ReLU())
#         net.append(nn.Conv2d(in_channels=256, out_channels=256, kernel_size=3, padding=1, stride=1))
#         net.append(nn.ReLU())
#         net.append(nn.Conv2d(in_channels=256, out_channels=256, kernel_size=3, padding=1, stride=1))
#         net.append(nn.ReLU())
#         net.append(nn.MaxPool2d(kernel_size=2, stride=2))
#
#         # block 4
#         net.append(nn.Conv2d(in_channels=256, out_channels=512, kernel_size=3, padding=1, stride=1))
#         net.append(nn.ReLU())
#         net.append(nn.Conv2d(in_channels=512, out_channels=512, kernel_size=3, padding=1, stride=1))
#         net.append(nn.ReLU())
#         net.append(nn.Conv2d(in_channels=512, out_channels=512, kernel_size=3, padding=1, stride=1))
#         net.append(nn.ReLU())
#         net.append(nn.MaxPool2d(kernel_size=2, stride=2))
#
#         # block 5
#         net.append(nn.Conv2d(in_channels=512, out_channels=512, kernel_size=3, padding=1, stride=1))
#         net.append(nn.ReLU())
#         net.append(nn.Conv2d(in_channels=512, out_channels=512, kernel_size=3, padding=1, stride=1))
#         net.append(nn.ReLU())
#         net.append(nn.Conv2d(in_channels=512, out_channels=512, kernel_size=3, padding=1, stride=1))
#         net.append(nn.ReLU())
#         net.append(nn.MaxPool2d(kernel_size=2, stride=2))
#
#         # add net into class property
#         self.extract_feature = nn.Sequential(*net)
#
#         # define an empty container for Linear operations
#         classifier = []
#         # classifier.append(nn.Linear(in_features=512 * 7 * 7, out_features=4096))
#         classifier.append(nn.Linear(in_features=512, out_features=4096))
#         classifier.append(nn.ReLU())
#         classifier.append(nn.Dropout(p=0.5))
#         classifier.append(nn.Linear(in_features=4096, out_features=4096))
#         classifier.append(nn.ReLU())
#         classifier.append(nn.Dropout(p=0.5))
#         classifier.append(nn.Linear(in_features=4096, out_features=self.num_classes))
#
#         # add classifier into class property
#         self.classifier = nn.Sequential(*classifier)
#
#     def forward(self, x):
#         feature = self.extract_feature(x)
#         feature = feature.view(x.size(0), -1)
#         classify_result = self.classifier(feature)
#         return classify_result
#

# Model = VGG_s_extra_features()
from torchvision.models import vgg11

# Model = vgg11(pretrained=False, num_classes=10)
# Model = VGG_s()
#
# summary(Model, (3, 32, 32), device="cpu")

# if __name__ == "__main__":
#     x = torch.rand(size=(8, 3, 224, 224))
#     vgg = SE_VGG(num_classes=1000)
#     out = vgg(x)
#     print(out.size())
