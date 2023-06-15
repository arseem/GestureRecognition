import json
import os
import datetime
import numpy as np
from alive_progress import alive_bar
import random

from sklearn.model_selection import train_test_split
from sklearn.metrics import multilabel_confusion_matrix, accuracy_score

import tensorflow as tf

from keras.utils import to_categorical
from keras.models import load_model, Model
from keras.layers import Dense
from keras.callbacks import TensorBoard, ModelCheckpoint


class TrainingHandler:

    def __init__(self, config_instance, state_instance, model_loader_instance):
        self._state = state_instance
        self._model_loader = model_loader_instance
        self._config = config_instance

        self._num_frames = config_instance.num_frames

        self._path_base = config_instance.models_path
        self._path_data = config_instance.datasets_path

        self._labels = np.array([])
        self._label_map = {}

        self.training = False


    def _get_gesture_data(self, gesture):
        data = np.load(os.path.join(self._path_data, 'raw', gesture + '.npy'))
        data = data.reshape(data.shape[0],
                     data.shape[1],
                     data.shape[2] * data.shape[3])
        
        for t in data:
            x_coords = t[..., 0::3]
            y_coords = t[..., 1::3]
            
            normalized_x = (x_coords - np.min(x_coords)) / abs(np.max(x_coords) - np.min(x_coords))
            normalized_y = (y_coords - np.min(y_coords)) / abs(np.max(y_coords) - np.min(y_coords))
            
            t[..., 0::3] = normalized_x
            t[..., 1::3] = normalized_y
        
        print(data.shape)

        self._labels = np.append(self._labels, np.full(data.shape[0], self._label_map[gesture]))
        return data


    def _get_training_data(self):
        trained = self._model_loader.get_model_info()['gestures']
        to_train = [gesture for gesture in self._state.gestures if gesture not in trained]

        data_needed = trained + to_train
        self._label_map = {g:i for i, g in enumerate(data_needed)}


        self._gestures_data = {gesture: self._get_gesture_data(gesture) for gesture in data_needed}

        # Flatten data
        X = np.concatenate([self._gestures_data[g] for g in self._gestures_data], axis=0)
        print('----------------------------------------')
        print(f'Final input data shape: {X.shape}')

        # One-hot encode labels
        y = to_categorical(self._labels).astype(int)

        # Split data
        TEST_SIZE = 0.20
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, random_state=42, shuffle=True)
        print('----------------------------------------')
        print(f'Training/Testing data size: {int(100-TEST_SIZE*100)}%/{int(TEST_SIZE*100)}%')
        print(f'Training data shape: {X_train.shape}')
        print(f'Training labels shape: {y_train.shape}')
        print(f'Testing data shape: {X_test.shape}')
        print(f'Testing labels shape: {y_test.shape}')

        return X_train, X_test, y_train, y_test


    def _get_model(self):
        path = self._state.model_path[:-6]+'h5'
        old_model = load_model(path)
        new_output_layer = Dense(len(self._state.gestures), activation='softmax', name=f"dense{random.randint(0, 10000)}")
        new_model = Model(inputs=old_model.input, outputs=new_output_layer(old_model.layers[-2].output))
        if self._config.freeze_weights:
            for layer in new_model.layers[:-1]:
                layer.trainable = False

        new_model.summary()
        new_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        
        return new_model
    

    def train(self):
        self.training = True

        model_name = f"model_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

        os.makedirs(f'{self._path_base}/{model_name}/logs')
        os.mkdir(f'{self._path_base}/{model_name}/models')
        info = {'gestures': list(self._state.gestures.keys()), 'num_frames': self._num_frames}
        with open(f'{self._path_base}/{model_name}/info.json', 'w+') as f:
            json.dump(info, f) 

        checkpoint_loss = ModelCheckpoint(f'{self._path_base}/{model_name}/models/{model_name}_checkpoint.h5', monitor='val_loss', verbose=1, save_best_only=True, mode='min')
    
        X_train, X_test, y_train, y_test = self._get_training_data()
        model = self._get_model()

        model.fit(X_train, y_train, epochs=self._config.epochs, validation_data=(X_test, y_test), callbacks=[checkpoint_loss, TensorBoard(log_dir=f'./hand_pose_estimation/models/{model_name}/logs/')])
        
        # Evaluate model
        print('----------------------------------------')
        print(model.evaluate(X_test, y_test, return_dict=True))

        yhat = model.predict(X_test)
        ytrue = np.argmax(y_test, axis=1).tolist()
        yhat = np.argmax(yhat, axis=1).tolist()

        print('Confusion matrix:')
        print(multilabel_confusion_matrix(ytrue, yhat))

        print('Accuracy score:')
        print(accuracy_score(ytrue, yhat))

        # Save model
        print('----------------------------------------')
        print('Saving model...')
        model.save(os.path.join(self._path_base, model_name, 'models', model_name + '.h5'))

        print('Done.')

        model_path = os.path.join(self._path_base, model_name, 'models', model_name + '_checkpoint.h5')
        save_path = model_path.replace('.h5', '.tflite')

        with alive_bar(unknown='dots_waves2', spinner=False, stats=False, monitor=False) as bar:
            model = tf.keras.models.load_model(model_path)
            converter = tf.lite.TFLiteConverter.from_keras_model(model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.experimental_new_converter=True
            converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS, tf.lite.OpsSet.SELECT_TF_OPS]
            tflite_model = converter.convert()

        with open(save_path, 'wb') as f:
            f.write(tflite_model)

        self._state.model_path = save_path

        print('----------------------------------------')
        print('Model saved to:')
        print(save_path)
        
        self.training = False


