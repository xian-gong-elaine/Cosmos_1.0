#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 12:21:22 2024

@author: gx
"""

import pandas as pd
import numpy as np
import time
from datetime import datetime
import pickle

import xgboost as xgb
from xgboost import XGBClassifier
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import accuracy_score, f1_score, fbeta_score, log_loss, roc_auc_score, confusion_matrix

summary_output_title = 'Tech_Detection_XGBoost_Classifier_Result.csv'
prediction_output_title = 'Original_ET50k_Prediction.csv'
model_output_title = 'Tech_Classifier_Model.sav'

# Dataset for prediction
df_50k_vec = pd.read_csv('Original_ET50k_entity_vectors.csv')
df_50k_vec.rename(columns = {'Unnamed: 0':'Wiki_Entity'}, inplace = True)
df_50k_vec = df_50k_vec.set_index('Wiki_Entity')
df_50k_vec_output = df_50k_vec.copy()

# 30 different seeds
seed_list = [42, 123, 5581, 3501, 1911, 867, 88169, 445, 2594, 1278, 
             9579, 34262, 73159, 17074, 52689, 878269, 758, 43255, 471012, 805211, 
             409, 513235, 68393, 993313, 830895, 17036, 629905, 881, 5458219, 2639]

# Define parameter grid
param_grid = {
    'n_estimators': [50, 100, 150],
    'learning_rate': [0.01, 0.03, 0.05, 0.1],
    'max_depth': [3, 5, 7, 10],
    'subsample': [0.6, 0.8, 1.0],
    'colsample_bytree': [0.5, 0.8, 1.0],
    'lambda':[1.5, 2],
    'alpha':[1.5, 2]
}

seed_index = 0
row_list = []
model_dict = {}
while seed_index < len(seed_list):
    t_start = datetime.now()
    seed = seed_list[seed_index]
    print (seed)

    data = pd.read_csv('Tech_Classifier_Input_Data.csv')
    data = data.sample(frac = 1, random_state = seed)
    feature_list = data.columns.tolist()[2:]
    target = 'Target'
    X, y = data[feature_list], data[target]

    row_dict = {}
    row_dict['seed'] = seed

    # Input Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed)

    # Model Training
    xgb_clf = XGBClassifier(objective='binary:logistic', use_label_encoder=False, eval_metric='mlogloss')
    
    clf = RandomizedSearchCV(estimator=xgb_clf, 
                             param_distributions=param_grid,
                             scoring='accuracy', 
                             cv = 5,
                             n_iter=1000, 
                             n_jobs = -1,
                             verbose=1)
    clf.fit(X_train, y_train)

    best_model = clf.best_estimator_
    model_dict[seed] = best_model

    y_pred = best_model.predict(X_test)
    y_pred_log_proba = np.log(best_model.predict_proba(X_test))
    y_pred_proba = best_model.predict_proba(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    fbeta = fbeta_score(y_test, y_pred, average='weighted', beta=0.5)
    auc = roc_auc_score(y_test, y_pred_proba[:, 1])    

    row_dict['Accuracy'] = accuracy
    row_dict['F1_Score'] = f1
    row_dict['FBeta_Score'] = fbeta
    row_dict['AUC_Score'] = auc
    
    row_list.append(row_dict)

    seed_index = seed_index + 1
    t_end = datetime.now()
    print (t_end - t_start)


df_result = pd.DataFrame(row_list)
optimal_seed = df_result.loc[df_result['F1_Score'] == df_result['F1_Score'].max(), 'seed'].values.tolist()[0]
optimal_model = model_dict[optimal_seed]

pred_col_name = 'Predicted_Label'
pred_prob_col_name = 'Predicted_Prob'
df_50k_vec_output[pred_col_name] = optimal_model.predict(df_50k_vec)
df_50k_vec_output[pred_prob_col_name] = optimal_model.predict_proba(df_50k_vec)[:, 1]

df_result.to_csv(summary_output_title, index = False)
df_50k_vec_output.reset_index().to_csv(prediction_output_title, index = False)
pickle.dump(optimal_model, open(model_output_title, 'wb'))


