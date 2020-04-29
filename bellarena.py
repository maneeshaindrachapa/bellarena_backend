import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from sentiment_analyser import SentimentAnalyser
import logging
logging.getLogger('tensorflow').disabled = True
from mf import RecommenderSystem
from util import get_sentiment_data, get_reviews_for_id, get_user_id, get_final_score, get_recommendation_data

'''
python -W ignore bellarena.py

1187 users
147 cloths

'''

if __name__ == "__main__":

    user_id = get_user_id()

    # recommender system
    recommendations = RecommenderSystem()
    recommendations.run()
    rec_cloth_ids, recommender_scores  = recommendations.predict(user_id)

    # sentiment analysis
    analyser = SentimentAnalyser()
    analyser.run()
    sentiment_scores = analyser.predict_sentiments(rec_cloth_ids)

    # Final score
    data_tuple = get_final_score(recommender_scores, sentiment_scores, rec_cloth_ids)