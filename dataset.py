from keras.layers import Input,Dense,Embedding,LSTM,Dropout,TimeDistributed,Bidirectional
from keras.models import Model,load_model
from keras.utils import np_utils
import numpy as np
import re

maxlen=500
#将数据集切分开
def cut_small(vocab):
    sentences=[]
    for v in vocab:
        v=v.replace('$$_','')
        v=v.replace('$$','')
        v=re.split('[，。]',v)
        if len(v)==1:
            sentences.append(v[0])
        elif len(v)>1:
            v.pop(-1)
            for i in range(len(v)):
                if i==0 and v[i]!='':
                    s=v[i]+' ，/w'
                    sentences.append(s)
                elif i%2==0 and v[i]!='':
                    s=v[i]+' 。/w'
                    s=s[3:]
                    sentences.append(s)
                elif i%2==1 and v[i]!='':
                    s=v[i]+' ，/w'
                    s=s[3:]
                    sentences.append(s)
    return sentences

#将训练集中的词与标签分隔开，创建pos_dict字典，并统计标签总数
def word_label(vocab):
    pos_dict = {}
    label = []
    for sen in vocab:
        for word in sen.split():
            if len(word) > 2 and word[-2] == '/':
                char = word[:-2]
                pos = word[-1:]
                pos_dict[char] = pos
                label.append(pos)
            elif len(word) > 3 and word[-3] == '/':
                char = word[:-3]
                pos = word[-2:]
                pos_dict[char] = pos
                label.append(pos)
    label=set(label)
    print("标签总数：%d"%(len(label)))
    return pos_dict,label

#创建词和标签与id的一一映射
def make_dict(pos_dict,label):
    words = [s for s in pos_dict.keys()]
    char2id = {c: i + 1 for i, c in enumerate(words)}
    id2char = {i + 1: c for i, c in enumerate(words)}
    label2id = {c: i + 1 for i, c in enumerate(label)}
    id2label = {i + 1: c for i, c in enumerate(label)}

    fw = open("char2id.txt", 'w', encoding='utf-8')
    fw.write(str(char2id))  # 把字典转化为str
    fw.close()
    # 将字典id2char写入文件
    f = open("id2char.txt", 'w', encoding='utf-8')
    f.write(str(id2char))
    f.close()
    # 将字典char2id写入文件
    fw = open("label2id.txt", 'w', encoding='utf-8')
    fw.write(str(label2id))  # 把字典转化为str
    fw.close()
    # 将字典id2char写入文件
    f = open("id2label.txt", 'w', encoding='utf-8')
    f.write(str(id2label))
    f.close()
    return char2id,id2char,label2id,id2label

#读取数据集
def data_cut(inputfile):
  sentences=[]
  with open(inputfile,'r',encoding='utf-8') as f:
      lines=f.readlines()
      for line in lines:
          line=line.replace('$$_','')
          line=line.replace('$$','')
          sentences.append(line)
  return sentences

#载入数据集
def load_data(sentences,char2id,label2id):
    X_data=[]
    y_data=[]
    for sen in sentences:
        sen=sen.split()
        X=[]
        y=[]
        for word in sen:
            if len(word)>2 and word[-2]=='/':
                char=word[:-2]
                pos=word[-1:]
                if char in char2id:
                    X.append(char2id[char])
                    y.append(label2id[pos])
            elif len(word)>3 and word[-3]=='/':
                char=word[:-3]
                pos=word[-2:]
                if char in char2id:
                    X.append(char2id[char])
                    y.append(label2id[pos])
         # 统一长度    一个小句子的长度不能超过32,否则将其切断。只保留32个
        if len(X) > maxlen:
            X = X[:maxlen]
            y = y[:maxlen]
        else:
            for i in range(maxlen - len(X)):  # 如果长度不够的，我们进行填充，记得标记为x
                X.append(0)
                y.append(0)
        X_data.append(X)
        y_data.append(y)
        #print(y_data)
    X=np.array(X_data)
    y=np_utils.to_categorical(y_data,41)
    return X,y

if __name__=='__main__':
    trainfile = 'data/train_pos.txt'
    vocab = open(trainfile, encoding='utf-8').read().rstrip('\n').split('\n')
    pos_dict,label=word_label(vocab)
    make_dict(pos_dict,label)
