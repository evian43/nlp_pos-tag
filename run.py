# -*- coding: utf-8 -*-
from keras.layers import Input,Dense,Embedding,LSTM,Dropout,TimeDistributed,Bidirectional
from keras.models import Model,load_model
from keras.utils import np_utils
from keras_contrib.layers import CRF
from keras.models import Sequential
from dataset import *
from model import *
import os
from keras.callbacks import ModelCheckpoint
import numpy as np
import re
import warnings
warnings.filterwarnings("ignore")

#定义模型所需的参数
embedding_size=200  #字嵌入的长度
maxlen=500   #长于则截断，短于则填充0
hidden_size=128
batch_size=64
epochs=20

trainfile = 'data/train_pos.txt'
valfile='data/val_pos.txt'
testfile='data/test_pos.txt'

#读取数据
vocab = open(trainfile, encoding='utf-8').read().rstrip('\n').split('\n')
#创建词典标签字典
pos_dict,label=word_label(vocab)

#载入词典
with open("dictionary/char2id.txt","r",encoding='utf-8') as f:
    char2id=eval(f.read())
    #print(len(char2id))
#载入字典
with open("dictionary/label2id.txt","r",encoding='utf-8') as f:
    label2id=eval(f.read())
    #print(len(label2id))
#载入字典
with open("dictionary/id2char.txt","r",encoding='utf-8') as f:
    id2char=eval(f.read())

#载入字典
with open("dictionary/id2label.txt","r",encoding='utf-8') as f:
    id2label=eval(f.read())

#切分数据集
sen_train = data_cut(trainfile)
sen_val = data_cut(valfile)
sen_test = data_cut(testfile)
#划分数据集，训练集，验证集
X_train, y_train = load_data(sen_train, char2id, label2id)
X_val, y_val = load_data(sen_val, char2id, label2id)
X_test, y_test = load_data(sen_val, char2id, label2id)

# 返回预测的标签序列
def pos_pre(data):
    data = re.split('[\n]', data)  # 来一句话，我们先进行切分，因为我们的输入限制在32
    sens = []
    Xs = []
    for sentence in data:
        sen = []
        X = []
        sentence = list(sentence.split())
        for s in sentence:
            s = s.strip()
            # if not s == '' and s in char2id:
            if s in char2id:
                sen.append(s)
                X.append(char2id[s])
            else:
                sen.append(0)
                X.append(0)
        if len(X) > maxlen:
            sen = sen[:maxlen]
            X = X[:maxlen]
        else:
            for i in range(maxlen - len(X)):
                X.append(0)

        if len(sen) > 0:
            Xs.append(X)
            sens.append(sen)

    Xs = np.array(Xs)
    ys = model.predict(Xs)
    return ys

#将one_hot编码解码
def one_hot_decode(encoded_seq):
    return [np.argmax(vector) for vector in encoded_seq]

def pos_sentences(strs):
    y_pre=pos_pre(strs)
    print(y_pre.shape)
    sentences = strs.split('\n')
    for i in range(y_pre.shape[0]):
        y = one_hot_decode(y_pre[i])
        #print(y)
        l = [id2label[i] for i in y]
        s = sentences[i].split()
        length = len(s)
        string = ''
        for j in range(length):
            ll = s[j] + '/' + id2label[y[j]] + ' '
            string += ll
        print(string)
        return string

def pos_file(filename,outputpath):
    with open(filename,'r',encoding='utf-8') as fr:
        sentences=fr.readlines()
        with open(outputpath, 'w', encoding='utf-8') as fw:
            for sentence in sentences:
                sen=pos_sentences(sentence)
                fw.write(sen)
                fw.write('\n')

if __name__=='__main__':
    import warnings
    warnings.filterwarnings("ignore")
    print('*'*10+"功能选择："+'*'*10)
    print("重新训练词性标注模型，请输入1")
    print("使用BILSTM模型进行词性标注，请输入2")
    print("使用BILSTM+CRF模型进行词性标注，请输入3")
    num=int(input('请输入：'))
    if num==1:
        model = model_BILSTM()
        model.fit(X_train, y_train, batch_size=batch_size, validation_data=(X_val, y_val), epochs=epochs)
        model.save('model/model_pos.h5')
    elif num==2:
        model_name='model/model_pos_bilstm_200_128.hdf5'
        model = load_model(model_name)
        print("已经加载模型："+model_name)
    elif num==3:
        model_name='model/model_pos_crf_200_128.hdf5'
        crf_layer = CRF(len(label2id))
        model = load_model(model_name,custom_objects={'CRF': CRF, 'crf_loss': crf_layer.loss_function,
                                           'crf_viterbi_accuracy': crf_layer.accuracy})
        print("已经加载模型：" + model_name)
    else:
        print("无对应选择功能")

    print('*' * 10 + "功能选择：" + '*' * 10)
    print('选择词性标注句子或段落，请输入1')
    print('选择词性标注文件，请输入2')
    n=int(input('请输入：'))
    if n==1:
        strs=input('输入需要词性标注的句子(已分完词）：')
        pos_sentences(strs)
    elif n==2:
        inputfile=input('请输入需要词性标注的文件路径（已分完词）：')
        outputfile=input('请输出词性标注结果需要写入的文件路径：')
        pos_file(inputfile,outputfile)
    else:
        print("无对应选择功能")







