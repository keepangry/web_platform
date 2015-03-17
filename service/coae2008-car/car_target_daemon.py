#-*- coding: utf-8 -*-
from socket import *
import jieba
import jieba.posseg as pseg
import json
import os
from func0317 import *
import subprocess
from configure import *


BASE_PATH = os.getcwd()+'/'
TEMP_PATH = BASE_PATH+'tmp/'
MODEL_PATH = BASE_PATH+'output/model'
CRF_TEST = '/usr/local/bin/crf_test'

car_word_jieba_path = BASE_PATH+'output/car_word_jieba'
#加载领域词库，TODO，应该标注词库的词性，默认名词可以
#jieba.load_userdict(car_word_jieba_path)

def jieba_cut(text):
        words = pseg.cut(text)
        seg_list = []
        for w in words:
            seg_list.append([w.word, w.flag])
        return seg_list


#文章内容生成crf格式数据
def generate_crf_data(text):
    #对text进行替换

    tempfile = TEMP_PATH+get_temp_filename()
    seg_list = jieba_cut(text)
    predict_list = []
    for item in seg_list:
        predict_list.append('\t'.join([item[0],item[1],'O']))
    list_to_file(predict_list,tempfile)
    return tempfile


def get_crf_result(test_file):
    #crf_test  -m model test.data
    cmd = [CRF_TEST,'-m '+MODEL_PATH,test_file]
    retcode = os.popen(' '.join(cmd))
    result = retcode.read()
    result = result.split('\n')

    #二维列表，带标注结果 0为词，1为O表示不知道，B为评价对象
    ret_data = []
    for line in result:
        line = line.split('\t')
        if len(line)==4:
            ret_data.append([line[0],line[2]])
    return ret_data


#test_data = generate_crf_data('我爱北京天安门，特别是开着骐达特别省油。')
#get_crf_result(test_data)


def main():
    HOST='localhost'
    PORT=20318
    BUFSIZ=102400
    ADDR=(HOST, PORT)
    sock=socket(AF_INET, SOCK_STREAM)
    sock.bind(ADDR)

    sock.listen(5)
    while True:
        tcpClientSock, addr=sock.accept()
        try:
            data=tcpClientSock.recv(BUFSIZ)
            #jieba_res = " ".join(jieba.cut(data,cut_all=False))

            test_data = generate_crf_data(data)
            result = get_crf_result(test_data)
            result = {"data":result}
            #result = {"data":data}
            tcpClientSock.send(json.dumps(result).encode("utf-8"))
        except:
            tcpClientSock.close()
    tcpClientSock.close()
    sock.close()

main()
