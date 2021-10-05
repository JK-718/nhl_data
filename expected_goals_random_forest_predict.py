from expected_goals_random_forest_train import forest_classifier, clean_df
from shot_data import get_shots





if __name__ == '__main__':
    classifier = forest_classifier[3]
    shots_raw = get_shots()
    shots = clean_df(shots_raw)
    score = forest_classifier(shots)
    classifier = score[3]