#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# author: Lifeng Wang(ofandywang@gmail.com)
# 文本分类数据集预处理

import os.path
import random
import sys


def multi_label_stat(input_file):
    """
    统计多标签分布情况
    """
    multi_label_dist = {}
    for line in open(input_file, 'r'):
        items = line.strip().split("\t")
        if len(items) != 3:
            print 'format error, line: %s' % items
            continue
        if items[0] in multi_label_dist:
            multi_label_dist[items[0]].add(items[-1])
        else:
            multi_label_dist[items[0]] = set([items[-1]])
    
    num_dist = {}
    for key, value in multi_label_dist.items():
        label_num = len(value)
        if label_num in num_dist:
            num_dist[label_num] += 1
        else:
            num_dist[label_num] = 1

    prefix = os.path.basename(input_file)
    fmulti_label = open(prefix + '.label_dist', 'w')
    for key, value in num_dist.items():
        fmulti_label.write('%d\t%d\n' % (key, value))
    fmulti_label.close()
 
def split(input_file, train_ratio = 0.8):
    """
    行格式化为 FastText 文件格式，并随机划分训练集和测试集
    注意：保证同一个 item 存在 multi-label 情况时，分到同一文件
    """
    prefix = os.path.basename(input_file)
    train_file = prefix + '.train.ft'
    ftrain = open(train_file, 'w')
    test_file = prefix + '.test.ft'
    ftest = open(test_file, 'w')
    class_set = set()
    total, ctrain, ctest = 0, 0, 0
    for line in open(input_file, 'r'):
        items = line.strip().split("\t")
        if len(items) != 3:
            print 'format error, line: %s' % items
            continue
        new_line = '__label__%s %s' % (items[-1], items[1])
        class_set.add(items[-1]) 
        total += 1
        random.seed(items[0])
        if random.random() < train_ratio:
            ftrain.write(new_line + '\n')
            ctrain += 1
        else:
            ftest.write(new_line + '\n')
            ctest += 1
    ftrain.close()
    ftest.close()
    print 'num_class %d\nnum_instance total %d, train %d(%.2f), test %d(%.2f)' \
       % (len(class_set), total, ctrain, 1.0 * ctrain / total, ctest, 1.0 * ctest / total)
    return train_file, test_file

def shuffle(input_file):
    """
    按行对文件随机打散，避免输出存在一定的规律
    """
    items = []
    for line in open(input_file, 'r'):
        items.append(line)
    random.shuffle(items)
    
    fout = open(input_file, 'w')
    for item in items:
        fout.write(item.strip() + '\n')
    fout.close()

def dist_stat(input_file):
    """
    统计数据集分布情况，包括样本长度，行业分布等
    """
    len_dist = {}  # 样本长度统计，即 tokens 数目
    class_dist = {}  # 行业样本分布
    
    for line in open(input_file, 'r'):
        items = line.strip().split(' ')
        tokens = len(items) - 1
        if tokens in len_dist:
             len_dist[tokens] += 1
        else:
             len_dist[tokens] = 1
        if items[0] in class_dist:
            class_dist[items[0]] += 1
        else:
            class_dist[items[0]] = 1
    
    prefix = os.path.basename(input_file)
    flen_dist = open(prefix + '.len_dist', 'w')
    for key, value in len_dist.items():
        flen_dist.write('%s\t%d\n' % (key, value))
    flen_dist.close()
    fclass_dist = open(prefix + '.class_dist', 'w')
    for key, value in class_dist.items():
        fclass_dist.write('%s\t%d\n' % (key, value))
    fclass_dist.close()
    

if __name__ == '__main__':
    input_file = sys.argv[1]
    
    multi_label_stat(input_file)
    train_file, test_file = split(input_file)
    shuffle(train_file)
    shuffle(test_file)
    dist_stat(train_file)
    dist_stat(test_file)

    # TODO: 格式化成其他模型需要的文件格式

