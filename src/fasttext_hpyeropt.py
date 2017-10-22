#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# author: Lifeng Wang(ofandywang@gmail.com)
# 基于 hyperopt 和 n-fold 交叉验证自动为 fasttext 模型选取最优的超参数

import os.path
import random
import sys
import time

from hyperopt import fmin, tpe, hp, STATUS_OK, Trials

input_file = ''
nfold = 5

def f1(p, r):
    return 2.0 * p * r / (p + r + 0.000001)

def exp(params):
    print 'Trying ', params
    start = time.clock() 
    fscore = 0.0 
    try:
        # 创建临时文件夹
        # 文件划分成 nfold 份
        for n in xrange(1, 5):
            # 生成训练文件和测试文件
            train_file = ''
            test_file = ''
            # train
            # test
            # 解析 test 评估结果
    except:
        pass
        # 删除临时文件夹
            
    return {'loss': - fscore / nfold,
            'status': STATUS_OK,
            'time': time.clock() - start}

def hyperopt():
    space = {
        'dim' : hp.choice('dim', [10, 30, 50, 100, 150, 200, 300]),
        'minCount' : hp.choice('minCount', [0, 1, 2, 3, 4, 5]),
        'wordNgrams' : hp.choice('wordNgrams', [1, 2, 3]),
        'bucket' : hp.choice('bucket', [5000000, 10000000]),
        'loss' : hp.choice('loss', ['hs', 'ns', 'softmax']),
        'lr' : hp.choice('lr', [0.01, 0.05, 0.1, 0.5, 1.0]),
        'epoch': hp.choice('epoch', [5, 10, 20, 25, 50])
        'thread': hp.choice('thread', [4, 8, 16])
        # 'pretrainedVectors' : hp.choice('pretrainedVectors', [])
    }
    trials = Trials()
    best = fmin(exp, space, algo=tpe.suggest, max_evals=100, trials=trials)
    print 'best'
    print best


if __name__ == '__main__':
    global input_file 
    input_file = sys.argv[1]
    hyperopt()

