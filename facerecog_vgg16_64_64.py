# -*- coding: utf-8 -*-
"""FaceRecog_VGG16_64_64.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UqBlOghmnu7BVmPjrXy27TkpKDJeA061

# Making FC Barcelona Face Recognition Model with VGG16

#### Loading the VGG16 Model
"""

from keras.applications import VGG16

# Setting the input size now to 64 x 64 pixel 
img_rows = 64
img_cols = 64 

# loads the VGG16 model without the top or FC layers
vgg16 = VGG16(weights = 'imagenet', 
                 include_top = False, 
                 input_shape = (img_rows, img_cols, 3))

# Here we freeze the last 4 layers, i.e. include_top = False

"""#### Freezing all the layers except the Top 4"""

# Layers are set to trainable as True by default
for layer in vgg16.layers:
    layer.trainable = False
    
# Let's print our layers 
for (i,layer) in enumerate(vgg16.layers):
    print(str(i) + " "+ layer.__class__.__name__, layer.trainable)

"""#### Let's make a function that returns our FC Head"""

def barcaface(bottom_model, num_classes):
  """creates the top or head of the model that will be 
    placed on top of the bottom layers"""
  top_model = bottom_model.output
  top_model = Flatten(name = "flatten")(top_model)
  top_model = Dense(512, activation='relu')(top_model)
  top_model = Dense(256, activation='relu')(top_model)
  top_model = Dense(128, activation='relu')(top_model)
  top_model = Dense(num_classes, activation='softmax')(top_model)
  return top_model

"""#### Let's add our FC head back onto VGG16"""

from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D, ZeroPadding2D
from keras.layers.normalization import BatchNormalization
from keras.models import Model
    
# Number of classes in the Flowers-17 dataset
num_classes = 3

FC_Head = barcaface(vgg16, num_classes)

model = Model(inputs=vgg16.input, outputs=FC_Head)

print(model.summary())

"""#### Loading our Barca Dataset"""

from keras.preprocessing.image import ImageDataGenerator

train_data_dir = 'root/mlops1/Train/'
validation_data_dir = 'root/mlops1/Test/'

# Augmenting the data!
train_datagen = ImageDataGenerator(
      rescale=1./255,
      rotation_range=20,
      width_shift_range=0.2,
      height_shift_range=0.2,
      horizontal_flip=True,
      fill_mode='nearest')
 
validation_datagen = ImageDataGenerator(rescale=1./255)
 
# Change the batchsize according to your system RAM
train_batchsize = 16
val_batchsize = 10
 
train_generator = train_datagen.flow_from_directory(
        train_data_dir,
        target_size=(img_rows, img_cols),
        batch_size=train_batchsize,
        class_mode='categorical')
 
validation_generator = validation_datagen.flow_from_directory(
        validation_data_dir,
        target_size=(img_rows, img_cols),
        batch_size=val_batchsize,
        class_mode='categorical',
        shuffle=False)

"""#### Training out our Model

* We are using the concept of checkpoint and early stopping here!
"""

from keras.optimizers import RMSprop
from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
                   
checkpoint = ModelCheckpoint("FCBarcelona_vgg16_64.h5",
                             monitor="val_loss",
                             mode="min",
                             save_best_only = True,
                             verbose=1)

earlystop = EarlyStopping(monitor = 'val_loss', 
                          min_delta = 0, 
                          patience = 5,
                          verbose = 1,
                          restore_best_weights = True)

reduce_lr = ReduceLROnPlateau(monitor = 'val_loss',
                              factor = 0.2,
                              patience = 3,
                              verbose = 1,
                              min_delta = 0.00001)

# we put our call backs into a callback list
callbacks = [earlystop, checkpoint, reduce_lr]

# Note we use a very small learning rate 
model.compile(loss = 'categorical_crossentropy',
              optimizer = RMSprop(lr = 0.0001),
              metrics = ['accuracy'])

# Enter the number of training and validation samples here
nb_train_samples = 324
nb_validation_samples = 100

# We are only training 1 EPOCH
epochs = 1
batch_size = 64

history = model.fit_generator(
    train_generator,
    steps_per_epoch = nb_train_samples // batch_size,
    epochs = epochs,
    callbacks = callbacks,
    validation_data = validation_generator,
    validation_steps = nb_validation_samples // batch_size)

# loss, accuracy = model.evaluate(train_generator, validation_generator)

accuracy = history.history['accuracy']
final = str(accuracy[len(accuracy)-1])
print(final)

output_file = open('root/mlops1/Accuracy.txt','w')
output_file.write(final)
output_file.close()