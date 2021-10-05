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
             'TimeBetween', #omitting speed since prev event, not sure if overfits 
             'Angle', 
             #'AngleChange',
             'ScoreDifference',
             'ForwardFlag',
             'IsRebound',
             ]]
    df = df.join(one_hot_encoded_shot)
    df = df.join(one_hot_encoded_hand)
    #df['AngleChange'] = df['AngleChange'].fillna(value=0)
    df = df.dropna()
    return df

def clean_df_upload(df):
    df = df[df['EmptyNetFlag'] == 0]
    #one_hot_encoded_shot = pd.get_dummies(df['ShotType'])
    #df = df.join(one_hot_encoded_shot)
    #df['AngleChange'] = df['AngleChange'].fillna(value=0)
    df = df.dropna(subset = ['AdjDistance', 
             'TimeBetween', #omitting speed since prev event, not sure if overfits 
             'Angle', 
             #'AngleChange',
             'ScoreDifference',
             'ForwardFlag',
             'IsRebound',
             'GoalFlag'])
    return df

def forest_classifier(df):  #consider training on all data and returing the results of that
    #df = df.drop(['TimeBetween', 'ScoreDifference'], axis=1)
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
    #return(classifier.fit(X_train, y_train))
    return(y_pred, y_pred_prob, y_test, classifier)
    #return(y_pred, y_pred_prob, y_test, classifier.fit(X_train, y_train))
    #return(metrics.accuracy_score(y_test, y_pred), y_pred)

def forest_classifier_all(df):  #consider training on all data and returing the results of that
    X, y = df.iloc[:, 1:].values, df.iloc[:, 0].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    #X = sc.transform(X)
    classifier = RandomForestClassifier(n_estimators=300,
                                        random_state=42,
                                        criterion='gini')
    classifier.fit(X_train, y_train)
    #y_pred = classifier.predict(X)
    y_pred_prob = classifier.predict_proba(X)
    #return(classifier.fit(X_train, y_train))
    df['ExpectedGoals'] = y_pred_prob[:][:,1]
    df = df.reset_index(drop=True)
    return df

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
    #predictions_proba = score[1]
    classifier = score[3]
    ex = goal_probability(shots, shots_semi_clean, classifier)
    #expected_goals_flurry = flurry_adjustment(expected_goals)
    #ex_all = forest_classifier_all(shots)
    #ex_all_flurry = flurry_adjustment(ex_all)
    
    #ex_all_flurry.to_sql('ExpectedGoals', schema='nhl', if_exists='replace', con=engine)
    