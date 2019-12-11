# Part 1 - Data Preprocessing
# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer

# Importing the dataset
dataset = pd.read_csv('matches_ready_for_ML.csv')
X1 = pd.DataFrame(dataset.iloc[:, 0].values)       # league_id --> categorical data
X2 = pd.DataFrame(dataset.iloc[:, 7:-2].values)    # exclude [match_time, match_url, home_team, away_team, full_time_score, half_time_score]
                                                   # as well as [match_outcome_full_time, match_outcome_half_time]
X = pd.concat([X1, X2], axis=1)                    # Matrix of features - independent variables

y1 = dataset.iloc[:, -2].values                     # Outcomes: Full time score
y2 = dataset.iloc[:, -1].values

# --> Need to translate all values by +2 because of error:
# Received a label value of -2 which is outside the valid range of [0, 6)
y1 = y1 + 2
y2 = y2 + 2

# Encoding categorical data (and handling dummy variable trap)
preprocess = ColumnTransformer(transformers=[('onehot', OneHotEncoder(categories='auto'), [0])], remainder="passthrough")
X = np.array(preprocess.fit_transform(X).toarray(), dtype=np.int)
X = X[:, 1:]

from sklearn.externals.joblib import dump
dump(preprocess, 'ML_preprocess.bin', compress=True)

# Splitting the dataset into the Training set and Test set
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y1, test_size = 0.2, random_state = 0)


# Feature Scaling
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# Save the standardscaler:
dump(sc, 'ML_std_scaler.bin', compress=True)

# Part 2 - Now let's make the ANN!
# Importing the Keras libraries and packages
import keras
from keras.models import Sequential
from keras.layers import Dense

# Setting up the layers
classifier = Sequential([
        keras.layers.Dense(46, activation='relu'),
        keras.layers.Dense(100, activation='relu'),
        keras.layers.Dense(100, activation='relu'),
        keras.layers.Dense(100, activation='relu'),
        keras.layers.Dense(6, activation='softmax')])

# Compiling the ANN - Applying Stochastic Gradient Descent
classifier.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Fitting the ANN to the Training set
classifier.fit(x=X_train, y=y_train, batch_size=10, epochs=100)

# Part 3 - Making the predictions and evaluating the model

# Predicting the Test set results
y_pred = pd.DataFrame(classifier.predict(X_test))
y_pred = (y_pred > 0.5)  # Convert probabilities into true/false values



y_pred_simplified = [0] * len(y_pred)
for i,_ in enumerate(y_pred[0]):    # 0...3359
    if y_pred[0][i] == True:
        y_pred_simplified[i] = 0
for i,_ in enumerate(y_pred[1]):    # 0...3359
    if y_pred[1][i] == True:
        y_pred_simplified[i] = 1
for i,_ in enumerate(y_pred[2]):    # 0...3359
    if y_pred[2][i] == True:
        y_pred_simplified[i] = 2
for i,_ in enumerate(y_pred[3]):    # 0...3359
    if y_pred[3][i] == True:
        y_pred_simplified[i] = 3
for i,_ in enumerate(y_pred[4]):    # 0...3359
    if y_pred[4][i] == True:
        y_pred_simplified[i] = 4
for i,_ in enumerate(y_pred[5]):    # 
    if y_pred[5][i] == True:
        y_pred_simplified[i] = 5        
y_pred_simplified = pd.DataFrame(y_pred_simplified)

# Making the Confusion Matrix
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred_simplified)

# Accuracy
acc = sum([cm[i,i] for i in range(0,len(cm))]) / len(y_test)

# Saving the classifier
# Serialize classifier to JSON
classifier_json = classifier.to_json()
with open("classifier_binance_v3.json", "w") as f:
    f.write(classifier_json)

# Serialize weights to HDF5
classifier.save_weights("classifier_binance_v3.h5")
print("Saved classifier to disk")


# Later...

# Load JSON and create model
json_file = open('classifier_binance_20191001_v2.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = keras.models.model_from_json(loaded_model_json)
# Load weights into new model
loaded_model.load_weights('classifier_binance_20191001_v2.h5')
print('Loaded model from disk')

# Evaluate Loaded model on test data
loaded_model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
score = loaded_model.evaluate(X_test, y_test, verbose=0)
print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1]*100))










