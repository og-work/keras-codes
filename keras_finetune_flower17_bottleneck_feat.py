'''This script goes along the blog post
"Building powerful image classification models using very little data"
from blog.keras.io.
It uses data that can be downloaded at:
https://www.kaggle.com/c/dogs-vs-cats/data
In our setup, we:
- created a data/ folder
- created train/ and validation/ subfolders inside data/
- created cats/ and dogs/ subfolders inside train/ and validation/
- put the cat pictures index 0-999 in data/train/cats
- put the cat pictures index 1000-1400 in data/validation/cats
- put the dogs pictures index 12500-13499 in data/train/dogs
- put the dog pictures index 13500-13900 in data/validation/dogs
So that we have 1000 training examples for each class, and 400 validation examples for each class.
In summary, this is our directory structure:
```
data/
    train/
        dogs/
            dog001.jpg
            dog002.jpg
            ...
        cats/
            cat001.jpg
            cat002.jpg
            ...
    validation/
        dogs/
            dog001.jpg
            dog002.jpg
            ...
        cats/
            cat001.jpg
            cat002.jpg
            ...
```
'''
import numpy as np
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dropout, Flatten, Dense
from keras import applications
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

# dimensions of our images.
img_width, img_height = 150, 150

top_model_weights_path = '../../data/flower17/finetune-keras/bottleneck_fc_model.h5'
train_data_dir = '../../data/flower17/finetune-keras/train/'
validation_data_dir = '../../data/flower17/finetune-keras/valid/'
FILE_BOTTLENECK_FEATURES_TRAIN = '../../data/flower17/finetune-keras/bottleneck_features_train.npy'
FILE_BOTTLENECK_FEATURES_VALID = '../../data/flower17/finetune-keras/bottleneck_features_valid.npy'
nb_train_samples = 180
nb_validation_samples = 60
epochs = 3
batch_size = 2
NUM_CLASSES = 2


def save_bottlebeck_features():
    datagen = ImageDataGenerator(rescale=1. / 255)

    # build the VGG16 network
    model = applications.VGG16(include_top=False, weights='imagenet')

    generator = datagen.flow_from_directory(
        train_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)
    bottleneck_features_train = model.predict_generator(
        generator, nb_train_samples // batch_size)
    np.save(open(FILE_BOTTLENECK_FEATURES_TRAIN, 'w'),
            bottleneck_features_train)

    generator = datagen.flow_from_directory(
        validation_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)
    bottleneck_features_validation = model.predict_generator(
        generator, nb_validation_samples // batch_size)
    np.save(open(FILE_BOTTLENECK_FEATURES_VALID, 'w'),
            bottleneck_features_validation)


def train_top_model():
    train_data = np.load(open(FILE_BOTTLENECK_FEATURES_TRAIN))
    train_labels = np.array(
        [0] * (nb_train_samples / 2) + [1] * (nb_train_samples / 2))

    print train_labels	
    validation_data = np.load(open(FILE_BOTTLENECK_FEATURES_VALID))
    validation_labels = np.array(
        [0] * (nb_validation_samples / 2) + [1] * (nb_validation_samples / 2))

    model = Sequential()
    model.add(Flatten(input_shape=train_data.shape[1:]))
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy', metrics=['accuracy'])

    model.fit(train_data, train_labels,
              epochs=epochs,
              batch_size=batch_size,
              validation_data=(validation_data, validation_labels))
    model.save_weights(top_model_weights_path)
	

save_bottlebeck_features()
train_top_model()

