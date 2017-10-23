#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# author: Lifeng Wang(ofandywang@gmail.com)
# 常用工具函数

import logging
import os
import subprocess
import sys

FLOAT_MAX = sys.float_info.max

def run_cmd(cmd):
    logging.info('run cmd: %s' % cmd)
    p = subprocess.Popen(cmd, shell=True, env=os.environ)
    p.cmd = cmd
    return p

def run_wait_cmd(cmd):
    logging.info('run cmd: %s' % cmd)
    p = subprocess.Popen(cmd, shell=True,
            #stdout=subprocess.PIPE,
            #stderr=subprocess.PIPE,
            close_fds=True, env=os.environ)
    ret = p.wait()
    return ret

def wait_cmd(p, timeout=FLOAT_MAX, refresh_interval=1.0):
    while True:
        p.poll()
        if p.returncode is None:
            if timeout > 0:
                timeout -= refresh_interval
                time.sleep(refresh_interval)
            else:
                p.terminate()
        else:
            break
    if p.returncode != 0:
        return p.returncode
    return p.returncode

def run_cmds_and_wait(cmds, timeout=FLOAT_MAX, refresh_interval=1.0):
    ps = []
    for c in cmds:
        ps.append(run_cmd(c))

    ret = 0
    for p in ps:
        if wait_cmd(p, timeout, refresh_interval) != 0:
            ret = -1
    return ret

