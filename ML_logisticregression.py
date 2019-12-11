# Part 1 - Data Preprocessing
# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

# Importing the dataset
dataset = pd.read_csv('matches_ready_for_ML_1.csv')
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
#dump(preprocess, 'randomforest_preprocess.bin', compress=True)

# Splitting the dataset into the Training set and Test set
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y1, test_size = 0.2, random_state = 0)


# Feature Scaling
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# Save the standardscaler:
#dump(sc, 'randomforest_std_scaler.bin', compress=True)

# Fitting Logistic Regression to the Training set
from sklearn.linear_model import LogisticRegression
classifier = LogisticRegression(random_state = 0)
classifier.fit(X_train, y_train)

# Predicting the Test set results
y_pred = pd.DataFrame(classifier.predict(X_test))

# Making the Confusion Matrix
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)

# Accuracy
acc = sum([cm[i,i] for i in range(0,len(cm))]) / len(y_test)

# Saving the classifier
pickle.dump(classifier, open("classifier_logisticregression.sav", "wb"))


# Applying k-Fold Cross Validation
# from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_validate
"""It will actually return the 10 accuracies for each one of the 10 combinations that will be created
through k-fold cross validation. 10 accuracy values are actually enough to get a relevant idea of the model performance."""
score = cross_validate(estimator = classifier, X = X_train, y = y_train, cv = 10)
score['test_score'].mean()
score['test_score'].std()


# Applying Grid Search to find the best model and the best parameters
# from sklearn.model_selection import GridSearchCV
pipe = Pipeline([('classifier' , RandomForestClassifier())])

from sklearn.model_selection import GridSearchCV
param_grid = [
    {'classifier' : [LogisticRegression()],
     'classifier__penalty' : ['l1', 'l2'],
    'classifier__C' : np.logspace(-4, 4, 20),
    'classifier__solver' : ['liblinear']},
    {'classifier' : [RandomForestClassifier()],
    'classifier__n_estimators' : list(range(10,101,10)),
    'classifier__max_features' : list(range(6,32,5))}
    ]

grid_search = GridSearchCV(pipe,
                           param_grid = param_grid,
                           scoring = 'accuracy',
                           cv = 5, # 5-fold cross validation
                           verbose=True,
                           n_jobs = 1) # all the power from my machine for a large dataset n_jobs = -1
"""
Sklearn will start parallel threads in all available CPU's if you give n_jobs = -1,
"""
grid_search = grid_search.fit(X_train, y_train)
best_accuracy = grid_search.best_score_
best_parameters = grid_search.best_params_








