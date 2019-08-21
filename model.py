from keras.layers import Input,Dense,Embedding,LSTM,Dropout,TimeDistributed,Bidirectional
from keras.models import Model,load_model
from keras.utils import np_utils
from keras_contrib.layers import CRF
from keras.models import Sequential
from dataset import *
import os
from keras.callbacks import ModelCheckpoint
import numpy as np
import re

#定义模型所需的参数
embedding_size=300  #字嵌入的长度
maxlen=500   #长于则截断，短于则填充0
hidden_size=128
batch_size=64
epochs=20

#载入字典
with open("char2id.txt","r",encoding='utf-8') as f:
    char2id=eval(f.read())
    #print(len(char2id))
#载入字典
with open("label2id.txt","r",encoding='utf-8') as f:
    label2id=eval(f.read())
    #print(len(label2id))

#定义BILSTM+CRF模型
def model_BILSTM_CRF():
    model = Sequential()
    model.add(Embedding(len(char2id) + 1, output_dim=embedding_size, input_length=maxlen))
    model.add(Bidirectional(LSTM(hidden_size, return_sequences=True)))
    model.add(Dropout(0.6))
    model.add(Bidirectional(LSTM(hidden_size, return_sequences=True)))
    model.add(Dropout(0.6))
    model.add(TimeDistributed(Dense(len(label2id)+1)))
    crf_layer = CRF(len(label2id)+1)
    model.add(crf_layer)
    model.compile('rmsprop', loss=crf_layer.loss_function, metrics=[crf_layer.accuracy])
    print(model.summary())
    return model

#定义BILSTM模型
def model_BILSTM():
    model = Sequential()
    model.add(Embedding(input_dim=len(char2id) + 1, output_dim=embedding_size, input_length=maxlen, mask_zero=True))
    model.add(Bidirectional(LSTM(hidden_size, return_sequences=True), merge_mode='concat'))
    model.add(Dropout(0.6))
    model.add(Bidirectional(LSTM(hidden_size, return_sequences=True), merge_mode='concat'))
    model.add(Dropout(0.6))
    model.add(TimeDistributed(Dense(41, activation='softmax')))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())
    return model


if __name__=='__main__':
    trainfile='data/train_pos.txt'
    valfile='data/val_pos.txt'
    testfile='data/test_pos.txt'
    sen_train = data_cut(trainfile)
    sen_val = data_cut(valfile)
    sen_test = data_cut(testfile)
    #print(sen_val)
    X_train, y_train = load_data(sen_train, char2id, label2id)
    X_val, y_val = load_data(sen_val, char2id, label2id)
    X_test, y_test = load_data(sen_val, char2id, label2id)

    # 断点续存，保存模型
    model=model_BILSTM()
    savePath = "Checkpoint_model.hdf5"  # 尽量将模型名字和前面的标题统一，这样便于查找
    checkpoint = ModelCheckpoint(savePath, save_weights_only=False, verbose=1, save_best_only=False,period=1)  # 回调函数，实现断点续训功能
    if os.path.exists(savePath):
        model.load_weights(savePath)
        # 若成功加载前面保存的参数，输出下列信息
        print("checkpoint_loaded")
    else:
        pass

    # 训练模型
    model.fit(X_train, y_train, batch_size=batch_size, validation_data=(X_val, y_val), epochs=epochs,callbacks=[checkpoint])

    #模型评价
    model.evalute(X_test,y_test)