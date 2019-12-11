# Part 1 - Data Preprocessing
# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer

for i in range(1,8):
    for csv_file in ['matches_ready_for_ML_{}_handicap.csv'.format(i),
                     'matches_ready_for_ML_{}_traditional.csv'.format(i)]:
        # Importing the dataset
        dataset = pd.read_csv(csv_file)
        X1 = pd.DataFrame(dataset.iloc[:, 0].values)       # league_id --> categorical data
        X2 = pd.DataFrame(dataset.iloc[:, 7:-2].values)    # exclude [match_time, match_url, home_team, away_team, full_time_score, half_time_score]
                                                           # as well as [match_outcome_full_time, match_outcome_half_time]
        X = pd.concat([X1, X2], axis=1)                    # Matrix of features - independent variables
        
        y1 = dataset.iloc[:, -2].values                    # Outcomes: Full time score
        y2 = dataset.iloc[:, -1].values                    #           Half time score
        
        # Encoding categorical data (and handling dummy variable trap)
        preprocess = ColumnTransformer(transformers=[('onehot', OneHotEncoder(categories='auto'), [0])], remainder="passthrough")
        X = np.array(preprocess.fit_transform(X).toarray(), dtype=np.int)
        X = X[:, 1:]
        
        from sklearn.externals.joblib import dump
        #dump(preprocess, 'randomforest_preprocess.bin', compress=True)
        
        # Splitting the dataset into the Training set and Test set
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y1, test_size = 0.2, random_state = 2)
        
        
        # Feature Scaling
        from sklearn.preprocessing import StandardScaler
        sc = StandardScaler()
        X_train = sc.fit_transform(X_train)
        X_test = sc.transform(X_test)
        
        # Save the standardscaler:
        #dump(sc, 'randomforest_std_scaler.bin', compress=True)
        
        # Fitting Random Forest Classification to the Training set
        from sklearn.ensemble import RandomForestClassifier
        classifier = RandomForestClassifier(n_estimators = 100,
                                            criterion = 'entropy',
                                            random_state = 2)
        classifier.fit(X_train, y_train)
        
        # Predicting the Test set results
        y_pred = pd.DataFrame(classifier.predict(X_test))
        
        # Making the Confusion Matrix
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Accuracy
        acc = sum([cm[i,i] for i in range(0,len(cm))]) / len(y_test)
        
        # Saving the classifier
        #pickle.dump(classifier, open("classifier_randomforest.sav", "wb"))
    
        with open('strategy_accuracies.txt', 'a') as f:
            f.write(csv_file.split(".")[0] + " accuracy: " + str(acc)[:5] + "\n")