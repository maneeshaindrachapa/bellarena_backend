import os
import numpy as np
import pandas as pd
from util import get_recommendation_data
from variables import max_neighbor, preprocessed_recommender_data

class RecommenderSystem:
    def __init__(self):
        similarity_df, pivot_norm, pivot = get_recommendation_data()
        data = pd.read_csv(preprocessed_recommender_data)
        self.similarity_df = similarity_df
        self.pivot_norm = pivot_norm
        self.pivot = pivot
        self.data = data

    def get_similar_cloths(self,cloth_id):
        if cloth_id not in self.pivot_norm.index:
            return None, None

        else:
            sim_cloths = self.similarity_df.sort_values(by=cloth_id, ascending=False).index[1:]
            sim_score = self.similarity_df.sort_values(by=cloth_id, ascending=False).loc[:, cloth_id].tolist()[1:]
            return sim_cloths, sim_score

    # predict the rating of cloth x by user y
    def predict_rating(self,user_id, cloth_id, max_neighbor=max_neighbor):
        cloth_ids, scores = self.get_similar_cloths(cloth_id)
        cloth_arr = np.array([x for x in cloth_ids])
        sim_arr = np.array([x for x in scores])

        # select only the cloth that has already rated by user x
        filtering = self.pivot_norm[user_id].loc[cloth_arr] != 0

        # calculate the predicted score
        try:
            score = np.dot(sim_arr[filtering][:max_neighbor], self.pivot[user_id].loc[cloth_arr[filtering][:max_neighbor]]) \
                    / np.sum(sim_arr[filtering][:max_neighbor])
        except:
            pass

        return score

    def get_recommendation(self,user_id, n_cloths=max_neighbor):
        predicted_rating = np.array([])

        for _cloth in self.pivot_norm.index:
            predicted_rating = np.append(predicted_rating, self.predict_rating(user_id, _cloth))

        # Never recommend something that user has already rated
        temp = pd.DataFrame({'predicted':predicted_rating, 'ids':self.pivot_norm.index})
        filtering = (self.pivot_norm[user_id] == 0.0)
        temp = temp.loc[filtering.values].sort_values(by='predicted', ascending=False)

        #Get to n recommendations
        ids = temp['ids'][:max_neighbor]
        predicted_scores = temp['predicted'][:max_neighbor].values
        rec_cloth_ids = self.data.loc[ids]['New Clothing ID'].values
        return predicted_scores, rec_cloth_ids

