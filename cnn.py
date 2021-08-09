
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


# Importing the Keras libraries and packages
from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.layers import Dropout
from keras.optimizers import Adam

# Initialising the CNN
# Creates an object for this class
classifier = Sequential()


# Step 1 - Convolution

p = 0.5
input_shape = (64 ,64)
classifier.add(Conv2D(32 ,(3 ,3), input_shape = (*input_shape ,3) , activation = 'relu'))

# Step 2 - Pooling

classifier.add(MaxPooling2D(pool_size = (2 ,2)))

classifier.add(Conv2D(32, (3, 3), activation = 'relu'))
classifier.add(MaxPooling2D(pool_size = (2, 2))) 

classifier.add(Conv2D(64, (3, 3), activation = 'relu'))
classifier.add(MaxPooling2D(pool_size = (2, 2))) 

classifier.add(Conv2D(64, (3, 3), activation = 'relu'))
classifier.add(MaxPooling2D(pool_size = (2, 2))) 


# Step 3 - Flattening layer that will flatten the feautre map into one single vector
classifier.add(Flatten())

# Step 4 - Full connection
classifier.add(Dense(units = 64 , activation = 'relu'))
classifier.add(Dropout(p))

classifier.add(Dense(units = 10 , activation = 'sigmoid'))

optimizers = Adam(lr=1e-3)


# Compiling the CNN
classifier.compile(optimizer = optimizers, loss = 'binary_crossentropy', metrics = ['accuracy'])


# Part 2 - Fitting the CNN to the images
# Prevent overfitting

from keras.preprocessing.image import ImageDataGenerator


image_generator = ImageDataGenerator(rescale= 1 /255, validation_split=0.2)

train_dataset = image_generator.flow_from_directory(batch_size=32,
                                                 directory='dataset/raw-img',
                                                 shuffle=True,
                                                 target_size=(input_shape), 
                                                 subset="training",
                                                 class_mode='categorical')

validation_dataset = image_generator.flow_from_directory(batch_size=32,
                                                 directory='dataset/raw-img',
                                                 shuffle=True,
                                                 target_size=(input_shape), 
                                                 subset="validation",
                                                 class_mode='categorical')

# Generate by training set

classifier.fit(train_dataset,
                         steps_per_epoch = (8000/32),
                         epochs = 100,
                         validation_data = validation_dataset,
                         workers = 32,
                         max_queue_size = 150,
                         validation_steps = (2000/32))

# # save model
#
# classifier.save("model_cnn.h5")
#
# classifier.summary()
#
# indices2 = validation_dataset.class_indices
# classifier.evaluate(train_dataset)


