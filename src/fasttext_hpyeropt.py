#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# author: Lifeng Wang(ofandywang@gmail.com)
# 基于 hyperopt 和 n-fold 交叉验证自动为 fasttext 模型选取最优的超参数

import os
import random
import shutil
import sys
import time
import traceback
import utils

from hyperopt import fmin, tpe, hp, STATUS_OK, Trials

# 当前脚本文件所在目录
WORKER_ROOT_DIR = os.path.split(os.path.realpath(__file__))[0]
input_file = ''
NFOLD = 3


def f1(p, r):
    return 2.0 * p * r / (p + r + 0.000001)

def exp(params):
    print 'Input file ', input_file
    print 'Trying ', params
    start = time.clock()
    fscore = 0.0
    try:
        # 创建临时文件夹
        local_dir = os.path.join(WORKER_ROOT_DIR, 'ft_exp')
        if not os.path.exists(local_dir):
            os.mkdir(local_dir)
        os.chdir(local_dir)

        total = 0
        for line in open(input_file, 'r'):
            total += 1
        print 'num instances %d.' % total
        # 文件划分成 NFOLD 份, 分别训练模型评估
        for n in range(NFOLD):
            # 生成训练文件和测试文件
            lower = int(1.0 * (total + NFOLD - 1) / NFOLD * n)
            upper = int(1.0 * (total + NFOLD - 1) / NFOLD * (n + 1))
            print 'lower %d, upper %d' % (lower, upper)
            train_file = 'cur_train.csv'
            model_file = 'cur_model'
            test_file = 'cur_test.csv'
            eval_file = 'cur_eval_result'
            ftrain = open(train_file, 'w')
            ftest = open(test_file, 'w')
            cnt = 0
            for line in open(input_file, 'r'):
                if random.random() < params['data_sampling_ratio']:
                    if cnt >= lower and cnt < upper:
                        ftest.write(line)
                    else:
                        ftrain.write(line)
                cnt += 1
            ftrain.close()
            ftest.close()

            # train
            train_cmd = '%s/bin/fasttext supervised -input %s -output %s -dim %d -wordNgrams %d -minCount %d -bucket %d -lr %f -loss %s -epoch %d -thread %d' \
                    % (WORKER_ROOT_DIR, train_file, model_file, params['dim'], params['wordNgrams'], params['minCount'], params['bucket'], params['lr'], params['loss'], params['epoch'], params['thread'])
            print train_cmd
            if utils.run_wait_cmd(train_cmd) != 0:
                print 'train model error, cmd: %s.' % train_cmd
                return {'loss': 0, 'status': STATUS_OK}
            # test
            test_cmd = '%s/bin/fasttext test %s.bin %s > %s' % (WORKER_ROOT_DIR, model_file, test_file, eval_file)
            print test_cmd
            if utils.run_wait_cmd(test_cmd) != 0:
                print 'test model error, cmd: %s.' % test_cmd
                return {'loss': 0, 'status': STATUS_OK}
            # 解析 test 评估结果
            p, r = 0, 0
            for line in open(eval_file, 'r'):
                if line.startswith('P@1'):
                    p = float(line.split('\t')[-1])
                elif line.startswith('R@1'):
                    r = float(line.split('\t')[-1])
            F1 = f1(p, r)
            print 'P %.2f R %.2f F1 %.2f' % (p, r, F1)
            fscore += F1
        print '%d-fold F1 %.2f' % (NFOLD, fscore / NFOLD)
    except Exception:
        estr = traceback.format_exc()
        print estr
    finally:
        # 删除临时文件夹
        shutil.rmtree(local_dir)

    return {'loss': - fscore / NFOLD,
            'status': STATUS_OK,
            'time': time.clock() - start}

def hyperopt():
    """best
       dim = 200
       loss hs
       bucket = 10000000
       epoch 5
       lr 0.1
       minCount 3
       wordNgrams 3
    """
    space = {
            'data_sampling_ratio': hp.choice('data_sampling_ratio', [1.0]),
            'dim' : hp.choice('dim', [50, 100, 200]),
            'minCount' : hp.choice('minCount', [1, 2, 5]),
            'wordNgrams' : hp.choice('wordNgrams', [2, 3]),
            'bucket' : hp.choice('bucket', [5000000, 10000000]),
            'loss' : hp.choice('loss', ['hs', 'ns']),   #, 'softmax']),
            'lr' : hp.choice('lr', [0.1, 0.5, 1.0]),
            'epoch': hp.choice('epoch', [5, 20]),
            'thread': hp.choice('thread', [8])
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

