import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn import metrics
from shot_data import get_shots

pd.options.mode.chained_assignment = None  # default='warn'

def clean_df(df):
    df = df[df['EmptyNetFlag'] == 0]
    
    one_hot_encoded_shot = pd.get_dummies(df['ShotType'])
    one_hot_encoded_hand = pd.get_dummies(df['Shot'])
    
    df = df[['GoalFlag',
             'AdjDistance', 
             'TimeBetween', 
             'Angle', 
             'ScoreDifference',
             'ForwardFlag',
             'IsRebound',
             ]]
    
    df = df.join(one_hot_encoded_shot)
    df = df.join(one_hot_encoded_hand)
    df = df.dropna()
    
    return df

def clean_df_upload(df):
    df = df[df['EmptyNetFlag'] == 0]
    df = df.dropna(subset = ['AdjDistance', 
             'TimeBetween', #omitting speed since prev event, not sure if overfits 
             'Angle', 
             'ScoreDifference',
             'ForwardFlag',
             'IsRebound',
             'GoalFlag'])
    return df

def forest_classifier(df): 
    X, y = df.iloc[:, 1:].values, df.iloc[:, 0].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    sc = StandardScaler()
    
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    
    classifier = RandomForestClassifier(n_estimators=300,
                                        random_state=42,
                                        criterion='gini')
    classifier.fit(X_train, y_train)
    
    y_pred = classifier.predict(X_test)
    y_pred_prob = classifier.predict_proba(X_test)

    return(y_pred, y_pred_prob, y_test, classifier)

def goal_probability(df1, df2, classifier):
    X = df1.iloc[:, 1:].values
    predictions = classifier.predict_proba(X)
    df2['ExpectedGoals'] = predictions[:][:,1]
    df2 = df2.reset_index(drop=True)
    return df2

def flurry_adjustment(df):
    flurry_array =[]
    for i, row in df.iterrows():
        if i == 0:
            flurry_array.append(df.loc[i, 'ExpectedGoals'])
            continue
        time_between = df.loc[i, 'TimeBetween']
        exp_goal = int(df.loc[i, 'ExpectedGoals'])
        exp_goal_next = int(df.loc[i - 1, 'ExpectedGoals'])
        exp_goal_ceiling = 1 - exp_goal_next
        if abs(time_between) <= 3:
            flurry_array.append(exp_goal * exp_goal_ceiling)
        else:
            flurry_array.append(exp_goal)
    df['ExpectedGoalsFlurryAdj'] = flurry_array
    return df

if __name__ == '__main__':
    shots_raw = get_shots()
    shots_semi_clean = clean_df_upload(shots_raw)
    shots = clean_df(shots_raw)
    score = forest_classifier(shots)

    classifier = score[3]
    ex = goal_probability(shots, shots_semi_clean, classifier)

    
