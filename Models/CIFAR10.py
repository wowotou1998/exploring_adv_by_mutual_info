import torch
import torch.nn.functional as F
from torch import nn

'''LeNet_3_32_32 in PyTorch.'''

# codes are import from https://github.com/xternalz/WideResNet-pytorch/blob/master/wideresnet.py
# original author: xternalz

import math


class BasicBlock(nn.Module):
    def __init__(self, in_planes, out_planes, stride, dropRate=0.0):
        super(BasicBlock, self).__init__()
        """
        总的来说, WideResNet的基本结构就是:两次卷积
        BatchNorm->LeakyReLU->Conv->BatchNorm->LeakyReLU->Conv
        两次卷积结束, 看看两次卷积的结果和输入是不是一样, 如果不一样, 就进行升维操作
        """
        self.bn1 = nn.BatchNorm2d(in_planes)
        self.relu1 = nn.LeakyReLU(0.1, inplace=True)
        self.conv1 = nn.Conv2d(in_planes,
                               out_planes,
                               kernel_size=3, stride=stride, padding=1,
                               bias=False)

        self.bn2 = nn.BatchNorm2d(out_planes)
        self.relu2 = nn.LeakyReLU(0.1, inplace=True)
        self.conv2 = nn.Conv2d(out_planes,
                               out_planes,
                               kernel_size=3, stride=1, padding=1,
                               bias=False)

        self.drop_rate = dropRate

        self.In_equal_Out = (in_planes == out_planes)
        # convShortcut 就是1*1卷积, 用于跳跃分支对x进行升维和降维
        self.convShortcut = (not self.In_equal_Out) and nn.Conv2d(in_planes,
                                                                  out_planes,
                                                                  kernel_size=1, stride=stride, padding=0,
                                                                  bias=False) or None

    def forward(self, x):

        # if not self.In_equal_Out:
        #     x = self.relu1(self.bn1(x))
        # else:
        #     out = self.relu1(self.bn1(x))
        #
        # out = self.relu2(self.bn2(self.conv1(out if self.In_equal_Out else x)))
        #
        # if self.drop_rate > 0:
        #     out = F.dropout(out, p=self.drop_rate, training=self.training)
        # out = self.conv2(out)
        # # 这个torch.add 很重要
        # return torch.add(x if self.In_equal_Out else self.convShortcut(x), out)
        # -------------------------
        """
        x->bn1->relu1->y->conv1->->bn2->relu2->conv2->out
                       |                              |
                       +------->conv(y)---------------+
        """

        y = self.relu1(self.bn1(x))

        if self.In_equal_Out:
            res = x
        else:
            res = self.convShortcut(y)

        out = self.relu2(self.bn2(self.conv1(y)))
        if self.drop_rate > 0:
            out = F.dropout(out, p=self.drop_rate, training=self.training)
        out = self.conv2(out)
        return torch.add(out, res)


# NetworkBlock 的作用只想当与一个函数, 用来产生网络中几个大组件模块
class NetworkBlock(nn.Module):
    def __init__(self, layer_repeat, in_planes, out_planes, block, stride, dropRate=0.0):
        super(NetworkBlock, self).__init__()
        self.layer = self._make_layer(block, in_planes, out_planes, layer_repeat, stride, dropRate)

    def _make_layer(self, block, in_planes, out_planes, layer_repeat, stride, dropRate):
        layers = []
        for i in range(int(layer_repeat)):
            layers.append(block(i == 0 and in_planes or out_planes,
                                out_planes,
                                i == 0 and stride or 1,
                                dropRate))
        return nn.Sequential(*layers)

    def forward(self, x):
        return self.layer(x)


class WideResNet(nn.Module):
    def __init__(self, depth, num_classes, widen_factor=1, dropRate=0.0):
        super(WideResNet, self).__init__()
        nChannels = [16, 16 * widen_factor, 32 * widen_factor, 64 * widen_factor]
        assert ((depth - 4) % 6 == 0)
        layer_repeat = (depth - 4) / 6
        block = BasicBlock
        # 1st conv before any network block
        self.conv1 = nn.Conv2d(3, nChannels[0],
                               kernel_size=3, stride=1, padding=1,
                               bias=False)
        # 1st block
        self.block1 = NetworkBlock(layer_repeat, nChannels[0], nChannels[1], block, 1, dropRate)
        # 2nd block
        self.block2 = NetworkBlock(layer_repeat, nChannels[1], nChannels[2], block, 2, dropRate)
        # 3rd block
        self.block3 = NetworkBlock(layer_repeat, nChannels[2], nChannels[3], block, 2, dropRate)
        # global average pooling and classifier
        self.bn1 = nn.BatchNorm2d(nChannels[3])
        self.relu = nn.LeakyReLU(0.1, inplace=True)
        self.fc = nn.Linear(nChannels[3], num_classes)
        self.nChannels = nChannels[3]

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
            elif isinstance(m, nn.Linear):
                m.bias.data.zero_()

        self.modules_to_hook = ('conv1',
                                'block1.layer.0.relu1',
                                'block2.layer.0.relu1',
                                'block3.layer.0.relu1',
                                'fc')
        # self.modules_to_hook = (torch.nn.LeakyReLU,)

    def forward(self, x, _eval=False):
        if _eval:
            # switch to eval mode
            self.eval()
        else:
            self.train()

        out = self.conv1(x)
        out = self.block1(out)
        out = self.block2(out)
        out = self.block3(out)
        out = self.relu(self.bn1(out))
        out = F.avg_pool2d(out, 8)
        out = out.view(-1, self.nChannels)

        return self.fc(out)


class Expression(nn.Module):
    def __init__(self, func):
        super(Expression, self).__init__()
        self.func = func

    def forward(self, input):
        return self.func(input)


class Model(nn.Module):
    def __init__(self, i_c=1, n_c=10):
        super(Model, self).__init__()

        self.conv1 = nn.Conv2d(i_c, 32, 5, stride=1, padding=2, bias=True)
        self.pool1 = nn.MaxPool2d((2, 2), stride=(2, 2), padding=0)

        self.conv2 = nn.Conv2d(32, 64, 5, stride=1, padding=2, bias=True)
        self.pool2 = nn.MaxPool2d((2, 2), stride=(2, 2), padding=0)

        self.flatten = Expression(lambda tensor: tensor.view(tensor.shape[0], -1))
        self.fc1 = nn.Linear(7 * 7 * 64, 1024, bias=True)
        self.fc2 = nn.Linear(1024, n_c)

    def forward(self, x_i, _eval=False):

        if _eval:
            # switch to eval mode
            self.eval()
        else:
            self.train()

        x_o = self.conv1(x_i)
        x_o = torch.relu(x_o)
        x_o = self.pool1(x_o)

        x_o = self.conv2(x_o)
        x_o = torch.relu(x_o)
        x_o = self.pool2(x_o)

        x_o = self.flatten(x_o)

        x_o = torch.relu(self.fc1(x_o))

        self.train()

        return self.fc2(x_o)


class RestNetBasicBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride):
        super(RestNetBasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=stride, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        output = self.conv1(x)
        output = F.relu(self.bn1(output))
        output = self.conv2(output)
        output = self.bn2(output)
        return F.relu(x + output)


class RestNetDownBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride):
        super(RestNetDownBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride[0], padding=1)
        self.bn1 = nn.BatchNorm2d(out_channels)

        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=stride[1], padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)

        self.extra = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride[0], padding=0),
            nn.BatchNorm2d(out_channels)
        )

    def forward(self, x):
        extra_x = self.extra(x)
        output = self.conv1(x)
        out = F.relu(self.bn1(output))

        out = self.conv2(out)
        out = self.bn2(out)
        return F.relu(extra_x + out)


class RestNet18(nn.Module):
    def __init__(self):
        super(RestNet18, self).__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3)
        self.bn1 = nn.BatchNorm2d(64)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        self.layer1 = nn.Sequential(RestNetBasicBlock(64, 64, 1),
                                    RestNetBasicBlock(64, 64, 1))

        self.layer2 = nn.Sequential(RestNetDownBlock(64, 128, [2, 1]),
                                    RestNetBasicBlock(128, 128, 1))

        self.layer3 = nn.Sequential(RestNetDownBlock(128, 256, [2, 1]),
                                    RestNetBasicBlock(256, 256, 1))

        self.layer4 = nn.Sequential(RestNetDownBlock(256, 512, [2, 1]),
                                    RestNetBasicBlock(512, 512, 1))

        self.avgpool = nn.AdaptiveAvgPool2d(output_size=(1, 1))

        self.fc = nn.Linear(512, 10)

    def forward(self, x):
        out = self.conv1(x)
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = self.avgpool(out)
        out = out.reshape(x.shape[0], -1)
        out = self.fc(out)
        return out


class CNN_1_cifar10(nn.Module):
    def __init__(self):
        super(CNN_1_cifar10, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class LeNet_3_32_32(nn.Module):
    def __init__(self):
        super(LeNet_3_32_32, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

        self.modules_to_hook = (nn.Conv2d, nn.Linear)

    def forward(self, x):
        x = F.max_pool2d(F.relu(self.conv1(x)), (2, 2))
        x = F.max_pool2d(F.relu(self.conv2(x)), 2)
        x = x.view(x.size()[0], -1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class net_cifar10(nn.Module):
    def __init__(self):
        # the input size = Batch *3*32*32
        super(net_cifar10, self).__init__()
        self.seq = torch.nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=64, kernel_size=(3, 3)),
            nn.ReLU(),
            nn.Conv2d(64, 64, (3, 3)),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=(2, 2)),
            nn.Conv2d(64, 128, (3, 3)),
            nn.ReLU(),
            nn.Conv2d(128, 128, (3, 3)),
            nn.ReLU(),
            nn.MaxPool2d((2, 2)),
        )
        self.seq2 = nn.Sequential(
            nn.Linear(in_features=128 * 5 * 5, out_features=128),
            nn.ReLU(),
            # nn.Linear(128, 128),
            # nn.ReLU(),
            nn.Linear(128, 10)
        )

        self.modules_to_hook = (torch.nn.ReLU,)

    def forward(self, x):
        r1 = self.seq(x)
        r1 = r1.view(r1.size(0), -1)
        r2 = self.seq2(r1)
        return r2


class VGG_s(nn.Module):
    # implement a simple version of vgg11 (https://arxiv.org/pdf/1409.1556.pdf)
    # the shape of image in CIFAR10 is 32x32x3, much smaller than 224x224x3,
    # the number of channels and hidden units are decreased compared to the architecture in paper
    def __init__(self):
        super(VGG_s, self).__init__()
        self.features = nn.Sequential(
            # Stage 1
            #  convolutional layer, input channels 3, output channels 8, filter size 3
            #  max-pooling layer, size 2
            nn.Conv2d(in_channels=3, out_channels=8, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),

            # Stage 2
            #  convolutional layer, input channels 8, output channels 16, filter size 3
            #  max-pooling layer, size 2
            nn.Conv2d(in_channels=8, out_channels=16, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),

            # Stage 3
            #  convolutional layer, input channels 16, output channels 32, filter size 3
            #  convolutional layer, input channels 32, output channels 32, filter size 3
            #  max-pooling layer, size 2
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, padding=1),
            # nn.Conv2d(in_channels=32, out_channels=32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),

            # Stage 4
            #  convolutional layer, input channels 32, output channels 64, filter size 3
            #  convolutional layer, input channels 64, output channels 64, filter size 3
            #  max-pooling layer, size 2
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
            # nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),

            # Stage 5
            #  convolutional layer, input channels 64, output channels 64, filter size 3
            #  convolutional layer, input channels 64, output channels 64, filter size 3
            #  max-pooling layer, size 2
            nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
            # nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),

        )

        self.classifier = nn.Sequential(
            #  fully-connected layer (64->64)
            #  fully-connected layer (64->10)
            nn.Linear(in_features=64, out_features=64),
            nn.ReLU(),
            nn.Dropout(0.5),

            nn.Linear(in_features=64, out_features=64),
            nn.ReLU(),
            nn.Dropout(0.5),

            nn.Linear(in_features=64, out_features=10),
        )

        # self._initialize_weights()

        # self.modules_to_hook = ('features.1',
        #                         'features.3',
        #                         'features.6',
        #                         'features.9',
        #                         'features.12',
        #                         'classifier.3')
        self.modules_to_hook = (torch.nn.MaxPool2d, torch.nn.Linear)

    def _initialize_weights(self):
        print('Initialize weights')
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


'''VGG11/13/16/19 in Pytorch.'''

cfg = {
    'VGG11': [64, 'M', 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
    'VGG13': [64, 64, 'M', 128, 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
    'VGG16': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M'],
    'VGG19': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 256, 'M', 512, 512, 512, 512, 'M', 512, 512, 512, 512, 'M'],
}


class VGG(nn.Module):
    def __init__(self, vgg_name):
        super(VGG, self).__init__()
        self.features = self._make_layers(cfg[vgg_name])
        self.classifier = nn.Linear(512, 10)

    def forward(self, x):
        out = self.features(x)
        out = out.view(out.size(0), -1)
        out = self.classifier(out)
        return out

    def _make_layers(self, cfg):
        layers = []
        in_channels = 3
        for x in cfg:
            if x == 'M':
                layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
            else:
                layers += [nn.Conv2d(in_channels, x, kernel_size=3, padding=1),
                           nn.BatchNorm2d(x),
                           nn.ReLU(inplace=True)]
                in_channels = x
        layers += [nn.AvgPool2d(kernel_size=1, stride=1)]
        return nn.Sequential(*layers)

# net = VGG_s('VGG11')
# x = torch.randn(2, 3, 32, 32)
# print(net)


# x1 = torch.rand(1, 3, 32, 32)
# x2 = torch.rand(1, 1, 28, 28)
#
# net1 = net_cifar10()
# net2 = Net_mnist()
# print(net1(x1).size())
# print(net2(x2).size())
