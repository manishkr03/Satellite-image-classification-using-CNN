# -*- coding: utf-8 -*-
"""Attentive_AI_satellite_image_classification_v3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KXPeAuccMf-DdKm0ezDH05u2A8iB2fAA
"""

from google.colab import drive
drive.mount("/content/drive/")

#!ls "/content/drive/MyDrive/Colab Notebooks/code_challenge/D-attentive-AI-satellite-image-classification/dataset"

#!wget -O "attentive_ai_internship_hiring_challenge-dataset.zip" "https://dockship-job-models.s3.ap-south-1.amazonaws.com/c452513e7cb7c4db308401f0f0079e51?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIDOPTEUZ2LEOQEGQ%2F20210129%2Fap-south-1%2Fs3%2Faws4_request&X-Amz-Date=20210129T154939Z&X-Amz-Expires=1800&X-Amz-Signature=0b83ff3033648b2b40ec46ef75268ce913ae00fb9d3bd9bdc243608f9f6ae698&X-Amz-SignedHeaders=host&response-content-disposition=attachment%3B%20filename%3D%22attentive_ai_internship_hiring_challenge-dataset.zip%22"

#!wget -O "/content/drive/MyDrive/Colab Notebooks/code_challenge/D-attentive-AI-satellite-image-classification/dataset/attentive_ai_internship_hiring_challenge-dataset.zip" "https://dockship-job-models.s3.ap-south-1.amazonaws.com/c452513e7cb7c4db308401f0f0079e51?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIDOPTEUZ2LEOQEGQ%2F20210128%2Fap-south-1%2Fs3%2Faws4_request&X-Amz-Date=20210128T063924Z&X-Amz-Expires=1800&X-Amz-Signature=8a137e91b30abb1034cdead844fd74ea7cc16b217b1f363c2a8f4fd0aff9d8d0&X-Amz-SignedHeaders=host&response-content-disposition=attachment%3B%20filename%3D%22attentive_ai_internship_hiring_challenge-dataset.zip%22"

#!unzip "/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/attentive_ai_internship_hiring_challenge-dataset.zip"

#!cp "/content/merged_data" -r "/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification"
#!rm -rf "/content/merged_data"

!ls "/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/merged_data"

import pandas as pd
import numpy as np

train_df =pd.read_csv("/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/merged_data/train_challenge.csv")

train_df =train_df.rename(columns={"0":"Filename", "1":"Labels"})
print(train_df.shape)
train_df.head()

import os
test_files = os.listdir("/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/merged_data/test/")
test_df = pd.DataFrame(test_files,columns=["Filename"])
print(test_df.shape)
test_df.head()

submission_df =pd.read_csv("/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/merged_data/test_challenge.csv")
print(submission_df.shape)
submission_df.head()

print(train_df["Labels"].value_counts())

# How manu images are there of each satellite?
train_df.Labels.value_counts().plot.bar(figsize=(20, 10))

!ls "/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/merged_data/train"

# Let's view an image
from IPython.display import Image
Image("/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/merged_data/train/4887.jpg")

# Check whether number of filenames matches number of actual image files
#train_image_dir_pth ="/content/drive/MyDrive/Colab Notebooks/code_challenge/D-attentive-AI-satellite-image-classification/dataset/merged_data/train"
#filenames = train_df.shape[0]
import os
print(len(os.listdir("/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/merged_data/train")))
print(train_df.shape[0])

filenames =[fname for fname in train_df['Filename']]
print(filenames[:10])
print(len(filenames))

print(train_df.Filename[4887])
print(train_df.Labels[4887])

Image("/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/merged_data/train/4887.jpg")

import cv2
import matplotlib.pyplot as plt

def display_car_image(index, scale=True, WIDTH=224, HEIGHT=224):
    images_dir = '/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/merged_data/train/'
    
    img = cv2.imread(images_dir + train_df['Filename'].iloc[index])
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, dsize=(WIDTH, HEIGHT))

    plt.figure(figsize=(20, 10))
    plt.imshow(img)
    plt.show()
    print("Filename : ", train_df['Filename'].iloc[index])
    print("labels : ", train_df['Labels'].iloc[index])


display_car_image(12)

#FUNCTION FOR PLOTTING
def plot_loss_acc(acc,val_acc,loss,val_loss):

    epochs=range(len(acc)) # Get number of epochs

    #------------------------------------------------
    # Plot training and validation accuracy per epoch
    #------------------------------------------------
    plt.plot(epochs, acc, 'r')
    plt.plot(epochs, val_acc, 'b')
    plt.title('Training and validation accuracy')
    plt.legend(['Train', 'Validation'], loc='upper left')
    plt.grid()
    plt.figure()

    #------------------------------------------------
    # Plot training and validation loss per epoch
    #------------------------------------------------
    plt.plot(epochs, loss, 'r')
    plt.plot(epochs, val_loss, 'b')
    plt.title('Training and validation loss')
    plt.legend(['Train', 'Validation'], loc='lower left')
    plt.grid()

#basicparams 
img_sz = (380,380)
train_btz = 16
val_btz = 16
test_btz = 16

from tensorflow import *
from tensorflow.keras.layers import *
import tensorflow as tf
from tensorflow.keras.preprocessing.image import *
import numpy as np, os, cv2, pandas as pd

train_datagen = ImageDataGenerator(
    rescale=1./255.,
    validation_split=0.1,
    horizontal_flip=True,
    rotation_range=10,
    brightness_range=(0.1,0.5),
    zoom_range=0.2,
   
    )

train_ds = train_datagen.flow_from_dataframe(
    dataframe=train_df,
    directory="/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/merged_data/train/",
    x_col = "Filename",
    y_col = "Labels",
    subset = "training",
    batch_size = train_btz,
    shuffle = True,
    class_mode = "categorical",
    target_size = img_sz
)

val_ds = train_datagen.flow_from_dataframe(
    dataframe=train_df,
    directory="/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/merged_data/train/",
    x_col = "Filename",
    y_col = "Labels",
    subset = "validation",
    batch_size = val_btz,
    shuffle = False,
    class_mode = "categorical",
    target_size = img_sz
)

test_datagen = ImageDataGenerator(rescale=1./255.)

test_ds = test_datagen.flow_from_dataframe(
    dataframe=test_df,
    directory="/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/merged_data/test/",
    x_col="Filename",
    y_col = None,
    batch_size = test_btz,
    seed = 42,
    shuffle = False,
    class_mode = None,
    target_size = img_sz
)

#Estimating Step size for train and validation set
STEP_SIZE_TRAIN = int(np.ceil(train_ds.n / train_ds.batch_size))
STEP_SIZE_VAL = int(np.ceil(val_ds.n / val_ds.batch_size))

print("Train step size:", STEP_SIZE_TRAIN)
print("Validation step size:", STEP_SIZE_VAL)

import tensorflow as tf
from tensorflow.keras.layers import Flatten, Dense, Conv2D, MaxPooling2D, Input, Dropout, AveragePooling2D, Concatenate
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import categorical_crossentropy
from tensorflow.keras.preprocessing.image import ImageDataGenerator

###--1st method-----------------
train_ds.reset()
val_ds.reset()

WIDTH = 380
HEIGHT = 380

#Creating CNN
cnnmodel = Sequential()

cnnmodel.add(Conv2D(64, (3,3), activation='relu', input_shape=(WIDTH,HEIGHT,3)))
cnnmodel.add(MaxPooling2D(2,2))
cnnmodel.add(Conv2D(32, (3,3), activation='relu'))
cnnmodel.add(MaxPooling2D(2,2))
cnnmodel.add(Conv2D(16, (3,3), activation='relu'))
cnnmodel.add(MaxPooling2D(2,2))
cnnmodel.add(Flatten())
cnnmodel.add(Dense(128, activation="relu"))
cnnmodel.add(Dense(64, activation="relu"))
cnnmodel.add(Dense(64, activation="relu"))
cnnmodel.add(Dense(6, activation="softmax"))

cnnmodel.summary()

cnnmodel.compile(optimizer=Adam(lr=0.0005), loss="mse", metrics=['acc'])
history = cnnmodel.fit_generator(train_ds,
    steps_per_epoch=STEP_SIZE_TRAIN,
    validation_data=val_ds,
    validation_steps=STEP_SIZE_VAL,
    epochs=1)

"""
cnnmodel.compile(optimizer=Adam(lr=0.0005), loss="mse", metrics=['acc'])
cnnmodel.fit(train_ds,epochs=1,validation_data=val_ds)
"""

acc=history.history['acc']
val_acc=history.history['val_acc']
loss=history.history['loss']
val_loss=history.history['val_loss']

plot_loss_acc(acc,val_acc,loss,val_loss)

test_ds.reset()
pred = cnnmodel.predict_generator(test_ds,
                               verbose=1)

predicted_class_indices = np.argmax(pred,axis=1)
labels = (train_ds.class_indices)
labels = dict((v,k) for k,v in labels.items())

predictions = [labels[k] for k in predicted_class_indices]
filenames = test_ds.filenames

results = pd.DataFrame({"filename":filenames,
                        "label":predictions})

results.to_csv("results.csv",index=False)

df =pd.read_csv("results.csv")
df.head()

#xception

model_x = tf.keras.applications.Xception(
    include_top=False,
    weights="imagenet",
    input_tensor=None,
    input_shape=(380, 380, 3),
    pooling='avg',
    #classes=1000,
    classifier_activation="softmax",
)

for layer in model_x.layers:
    layer.trainable = False
output = Dense(6, activation='softmax')(model_x.output)
model_xception = tf.keras.Model(model_x.input, output)

model_xception.compile(loss='categorical_crossentropy', 
              optimizer='adam', 
              metrics=['accuracy'])

model_xception.summary()

model_xception.fit_generator( 
    train_ds, 
    epochs=1, 
    validation_data=val_ds)

predict = model.predict_generator(test_ds)

prediction_cls_idx = predict.argmax(axis=-1)

idx_to_cls = {v: k for k, v in train_ds.class_indices.items()}
prediction_cls= np.vectorize(idx_to_cls.get)(prediction_cls_idx)
filenames_to_cls = list(zip(test_ds.filenames, prediction_cls))

data = pd.DataFrame(filenames_to_cls)
data.columns = ['Filename', 'Labels']
data.to_csv('output1.csv', index = False)

#---vgg16---2nd method-------------

model_vgg16 = tf.keras.applications.VGG16(
    include_top=False,
    weights="imagenet",
    input_tensor=None,
    input_shape=(224, 224, 3),
    pooling='avg',
    #classes=1000,
    classifier_activation="softmax",
)

for layer in model_vgg16.layers:
    layer.trainable = False
output = Dense(6, activation='softmax')(model_vgg16.output)
vgg16_model = tf.keras.Model(model_vgg16.input, output)

vgg16_model.compile(loss='categorical_crossentropy', 
              optimizer='adam', 
              metrics=['accuracy'])

vgg16_model.summary()

#fit model
history_vgg16 =vgg16_model.fit_generator( 
    train_ds, 
    epochs=3, 
    validation_data=val_ds)

#custom CNN MODEL------3rd method------------

model = Sequential()
model.add(Conv2D(input_shape=(380,380,3),filters=64,kernel_size=(3,3),padding="same", activation="relu"))
model.add(Conv2D(filters=64,kernel_size=(3,3),padding="same", activation="relu"))
model.add(MaxPool2D(pool_size=(2,2),strides=(2,2)))
model.add(Conv2D(filters=128, kernel_size=(3,3), padding="same", activation="relu"))
model.add(Conv2D(filters=128, kernel_size=(3,3), padding="same", activation="relu"))
model.add(MaxPool2D(pool_size=(2,2),strides=(2,2)))
model.add(Conv2D(filters=256, kernel_size=(3,3), padding="same", activation="relu"))
model.add(Conv2D(filters=256, kernel_size=(3,3), padding="same", activation="relu"))
model.add(Conv2D(filters=256, kernel_size=(3,3), padding="same", activation="relu"))
model.add(MaxPool2D(pool_size=(2,2),strides=(2,2)))
model.add(Conv2D(filters=512, kernel_size=(3,3), padding="same", activation="relu"))
model.add(Conv2D(filters=512, kernel_size=(3,3), padding="same", activation="relu"))
model.add(Conv2D(filters=512, kernel_size=(3,3), padding="same", activation="relu"))
model.add(MaxPool2D(pool_size=(2,2),strides=(2,2)))
model.add(Conv2D(filters=512, kernel_size=(3,3), padding="same", activation="relu"))
model.add(Conv2D(filters=512, kernel_size=(3,3), padding="same", activation="relu"))
model.add(Conv2D(filters=512, kernel_size=(3,3), padding="same", activation="relu"))
model.add(MaxPool2D(pool_size=(2,2),strides=(2,2)))

model.add(Flatten())
model.add(Dense(units=4096,activation="relu"))
model.add(Dense(units=4096,activation="relu"))
model.add(Dense(units=6, activation="softmax"))

from keras.optimizers import Adam
opt = Adam(lr=0.001)
model.compile(loss='categorical_crossentropy', 
              optimizer=opt, 
              metrics=['accuracy'])

model.summary()

#from keras.callbacks import ModelCheckpoint, EarlyStopping
#checkpoint = ModelCheckpoint("vgg16_1.h5", monitor='val_acc', verbose=1, save_best_only=True, save_weights_only=False, mode='auto', period=1)
#early = EarlyStopping(monitor='val_acc', min_delta=0, patience=20, verbose=1, mode='auto')
#hist = model.fit_generator(steps_per_epoch=100,generator=traindata, validation_data= testdata, validation_steps=10,epochs=100,callbacks=[checkpoint,early])

hist = model.fit_generator(train_ds,
    steps_per_epoch=STEP_SIZE_TRAIN,
    validation_data=val_ds,
    validation_steps=STEP_SIZE_VAL,
    epochs=1)

# All the training/validation accuracy and loss are stored in hist and I will visualise it from there

import matplotlib.pyplot as plt
plt.plot(hist.history["acc"])
plt.plot(hist.history['val_acc'])
plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])
plt.title("model accuracy")
plt.ylabel("Accuracy")
plt.xlabel("Epoch")
plt.legend(["Accuracy","Validation Accuracy","loss","Validation Loss"])
plt.show()

###---vgg16---final----4th method-----------

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Flatten, Dense, Dropout
from tensorflow.keras.applications import VGG16

IMAGE_SIZE = [380, 380]  # we will keep the image size as (380,380). You can increase the size for better results. 
num_classes=6
# loading the weights of VGG16 without the top layer. These weights are trained on Imagenet dataset.
vgg = VGG16(input_shape = IMAGE_SIZE + [3], weights = 'imagenet', include_top = False)  # input_shape = (64,64,3) as required by VGG

# this will exclude the initial layers from training phase as there are already been trained.
for layer in vgg.layers:
    layer.trainable = False

x = Flatten()(vgg.output)
x = Dense(512, activation = 'relu')(x)   # we can add a new fully connected layer but it will increase the execution time.
x = Dropout(0.5)(x)
x = Dense(num_classes, activation = 'softmax')(x)  # adding the output layer with softmax function as this is a multi label classification problem.

model_vgg = Model(inputs = vgg.input, outputs = x)

model_vgg.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

model_vgg.summary()

hist_vgg = model_vgg.fit_generator(train_ds,
    steps_per_epoch=STEP_SIZE_TRAIN,
    validation_data=val_ds,
    validation_steps=STEP_SIZE_VAL,
    epochs=30)

# All the training/validation accuracy and loss are stored in hist and I will visualise it from there

import matplotlib.pyplot as plt
plt.plot(hist_vgg.history["accuracy"])
plt.plot(hist_vgg.history['val_accuracy'])
plt.plot(hist_vgg.history['loss'])
plt.plot(hist_vgg.history['val_loss'])

plt.title("model accuracy")
plt.ylabel("Accuracy")
plt.xlabel("Epoch")
plt.legend(["Accuracy","Validation Accuracy","loss","Validation Loss"])
plt.show()

predict = model_vgg.predict_generator(test_ds)

prediction_cls_idx = predict.argmax(axis=-1)
prediction_cls_idx

idx_to_cls = {v: k for k, v in train_ds.class_indices.items()}
prediction_cls= np.vectorize(idx_to_cls.get)(prediction_cls_idx)
filenames_to_cls = list(zip(test_ds.filenames, prediction_cls))

data = pd.DataFrame(filenames_to_cls)
data.columns = ['Filename', 'Labels']
data.to_csv('/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/output.csv', index = False)

data_output2 =pd.read_csv("/content/drive/MyDrive/Dataset/D-attentive-AI-satellite-image-classification/output.csv")
data_output2

data_output2['Labels'].value_counts()

