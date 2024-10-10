from pathlib import Path

import joblib
import matplotlib
import pandas as pd

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA


# Calculate the probability that the token belongs to category 0(real secret token)
def calculate_probability(x):
    probabilities = lda.predict_proba(x)
    prob_class_0 = probabilities[0][0]
    return prob_class_0


if __name__ == '__main__':

    key_names = ["alibabacloud", "google_api_key", "google_oauth_client_id", "slack_incoming_web_hook_url", "stripe_test", "tencent_cloud_secret_id"]
    current_dir = Path(__file__).resolve().parent
    # Location for LDA models
    model_folder = f"{current_dir.parent}/LDA_Models"

    for key_name in key_names:
        # Token features file
        csv_file = f"{current_dir.parent}/data/{key_name}.csv"
        df = pd.read_csv(csv_file)
        X_scaled = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values
        lda = LDA(n_components=1)
        lda.fit(X_scaled, y)

        joblib.dump(lda, f'{model_folder}/LDA_{key_name}.pkl')


