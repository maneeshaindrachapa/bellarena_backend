import re
import os
import pandas as pd
import numpy as np
import pickle as pkl
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.utils import resample
from sklearn.utils import shuffle
from variables import train_data_path, test_data_path, cloth_count_threshold, preprocessed_sentiment_data, preprocessed_recommender_data, eclothing_data
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from collections import Counter
from variables import alpha
import math

def get_sentiment_data():
    global train_data_path, test_data_path
    if not os.path.exists(train_data_path) or not os.path.exists(test_data_path) or not os.path.exists(preprocessed_sentiment_data):
        print("Upsampling data !!!")
        df = pd.read_csv(preprocessed_recommender_data)
        data = df.copy()[['ID','USER ID','Clothing ID','New Clothing ID','Review Text','Recommended IND']]
        data['PreProcessed Text'] = data.apply(preprocessed_text_column, axis=1)
        data.to_csv(preprocessed_sentiment_data, encoding='utf-8', index=False)
        upsample_data(data)
    train_data = pd.read_csv(train_data_path)
    test_data  = pd.read_csv(test_data_path)

    train_labels  = np.array(train_data['Recommended IND'],dtype=np.int32)
    test_labels   = np.array(test_data['Recommended IND'],dtype=np.int32)

    train_reviews = np.array(train_data['PreProcessed Text'],dtype='str')
    test_reviews  = np.array(test_data['PreProcessed Text'],dtype='str')
    print("Data is Ready!!!")
    return train_labels,test_labels,train_reviews,test_reviews

def lemmatization(lemmatizer,sentence):
    lem = [lemmatizer.lemmatize(k) for k in sentence]
    lem = set(lem)
    return [k for k in lem]

def remove_stop_words(stopwords_list,sentence):
    return [k for k in sentence if k not in stopwords_list]

def preprocess_one(review):
    lemmatizer = WordNetLemmatizer()
    tokenizer = RegexpTokenizer(r'\w+')
    stopwords_list = stopwords.words('english')
    review = review.lower()
    remove_punc = tokenizer.tokenize(review) # Remove puntuations
    remove_num = [re.sub('[0-9]', '', i) for i in remove_punc] # Remove Numbers
    remove_num = [i for i in remove_num if len(i)>0] # Remove empty strings
    lemmatized = lemmatization(lemmatizer,remove_num) # Word Lemmatization
    remove_stop = remove_stop_words(stopwords_list,lemmatized) # remove stop words
    updated_review = ' '.join(remove_stop)
    return updated_review

def preprocessed_text_column(row):
    review = str(row['Review Text'])
    lemmatizer = WordNetLemmatizer()
    tokenizer = RegexpTokenizer(r'\w+')
    stopwords_list = stopwords.words('english')
    review = review.lower()
    remove_punc = tokenizer.tokenize(review) # Remove puntuations
    remove_num = [re.sub('[0-9]', '', i) for i in remove_punc] # Remove Numbers
    remove_num = [i for i in remove_num if len(i)>0] # Remove empty strings
    lemmatized = lemmatization(lemmatizer,remove_num) # Word Lemmatization
    remove_stop = remove_stop_words(stopwords_list,lemmatized) # remove stop words
    updated_review = ' '.join(remove_stop)
    return updated_review

def upsample_data(data):
    data_majority = data[data['Recommended IND'] == 1]
    data_minority = data[data['Recommended IND'] == 0]

    # bias = data_minority.shape[0]/data_majority.shape[0]

    # lets split train/test data first then
    train = pd.concat([data_majority.sample(frac=0.8,random_state=200),
            data_minority.sample(frac=0.8,random_state=200)])
    test = pd.concat([data_majority.drop(data_majority.sample(frac=0.8,random_state=200).index),
            data_minority.drop(data_minority.sample(frac=0.8,random_state=200).index)])

    train = shuffle(train)
    test = shuffle(test)

    print('positive data in training:',(train['Recommended IND'] == 1).sum())
    print('negative data in training:',(train['Recommended IND'] == 0).sum())
    print('positive data in test:',(test['Recommended IND'] == 1).sum())
    print('negative data in test:',(test['Recommended IND'] == 0).sum())

    # Separate majority and minority classes in training data for up sampling
    data_majority = train[train['Recommended IND'] == 1]
    data_minority = train[train['Recommended IND'] == 0]

    print("majority class before upsample:",data_majority.shape)
    print("minority class before upsample:",data_minority.shape)

    # Upsample minority class
    data_minority_upsampled = resample(data_minority,
                                      replace=True,     # sample with replacement
                                      n_samples= data_majority.shape[0],    # to match majority class
                                      random_state=42) # reproducible results

    # Combine majority class with upsampled minority class
    train_data_upsampled = pd.concat([data_majority, data_minority_upsampled])

    # Display new class counts
    print("After upsampling\n",train_data_upsampled['Recommended IND'].value_counts(),sep = "")
    train_data_upsampled = shuffle(train_data_upsampled)

    train_data_upsampled = train_data_upsampled.dropna(axis = 0, how ='any')
    test = test.dropna(axis = 0, how ='any')
    train_data_upsampled.to_csv(train_data_path, encoding='utf-8', index=False)
    test.to_csv(test_data_path, encoding='utf-8', index=False)

def preprocessed_data(reviews):
    updated_reviews = []
    if isinstance(reviews, np.ndarray) or isinstance(reviews, list):
        for review in reviews:
            updated_review = preprocess_one(review)
            updated_reviews.append(updated_review)
    elif isinstance(reviews, np.str_)  or isinstance(reviews, str):
        updated_reviews = [preprocess_one(reviews)]

    return np.array(updated_reviews)

def balance_test_data(reviews,labels):
    positive_labels = labels[labels == 1]
    positive_reviews = reviews[labels == 1]

    negative_labels = labels[labels == 0]
    negative_reviews = reviews[labels == 0]

    minority_count = len(negative_reviews)
    majority_count = len(positive_reviews)

    idxs = np.random.randint(0, majority_count, minority_count)

    reviews1 = positive_reviews[idxs]
    labels1 = positive_labels[idxs]

    reviews , labels = shuffle(np.concatenate((reviews1,negative_reviews)),np.concatenate((labels1,negative_labels)))
    return reviews , labels

def get_reviews_for_id(cloth_id):
    data = pd.read_csv(preprocessed_sentiment_data)
    cloth_ids = data['New Clothing ID']
    while True:
        if cloth_id < max(cloth_ids) + 1:
            # get_newId_on_oldId(data,cloth_id)
            cloth_id_data = data[data['New Clothing ID'] == cloth_id]
            reviews = cloth_id_data['PreProcessed Text']
            labels = cloth_id_data['Recommended IND']
            break

    return reviews.to_numpy(), labels.to_numpy()

def get_user_id():
    get_recommendation_data()
    data = pd.read_csv(preprocessed_recommender_data)
    user_ids = set(data['USER ID'])
    while True:
        user_id = int(input("Enter user Id :"))
        if user_id in user_ids:
            return user_id
        print("Please enter Valid User ID below !")

def get_newId_on_oldId(data,cloth_id):
    idx = data['Clothing ID'].values.tolist().index(cloth_id)
    return data['New Clothing ID'][idx]

def fill_nan_data(data):
    data_copy = data.copy()
    size = len(data_copy)
    idxs = data_copy.index[data_copy.isnull().any(axis=1)].tolist()

    if len(idxs) > 0:
        print("filling missing values")
        for idx in idxs:
            while True:
                row = np.random.choice(size)
                data_row = data_copy.iloc[row,:]
                if len(data_row[data_row.isnull()]) != 0:
                   data_copy.iloc[idx,:] = data_row
                   break
    return data_copy

def create_new_user_ids(filter_data):
    devision_name = filter_data['Division Name'].values
    department_name = filter_data['Department Name'].values
    class_name = filter_data['Class Name'].values
    age = filter_data['Age'].values

    new_ids = {}
    id_idx = 0
    user_data = [(devision_name[i], department_name[i], class_name[i], age[i]) for i in range(len(filter_data))]
    for ud in user_data:
        if not ud in new_ids:
           new_ids[ud] = id_idx
           id_idx += 1

    def user_id_row(row, new_ids=new_ids):
        devision_name = row['Division Name']
        department_name = row['Department Name']
        class_name = row['Class Name']
        age = row['Age']

        user_tuple = (devision_name, department_name, class_name, age)
        return int(new_ids[user_tuple])

    filter_data['USER ID'] = filter_data.apply(user_id_row, axis=1)
    filter_data.to_csv(preprocessed_recommender_data, encoding='utf-8', index=False)
    return filter_data

def get_recommendation_data():
    if not os.path.exists(preprocessed_recommender_data):
        df = pd.read_csv(eclothing_data)
        df.drop(['Positive Feedback Count', 'Title'], axis=1, inplace=True)
        data = fill_nan_data(df)
        data  = data.dropna(axis = 0, how ='any')
        data = data.copy()
        filter_data = cloth_rating_distrubution(data,False)
        filter_data = create_new_user_ids(filter_data)
    filter_data = pd.read_csv(preprocessed_recommender_data)
    filter_data = shuffle(filter_data)
    user_ids = filter_data['USER ID'].to_numpy()
    cloth_ids = filter_data['New Clothing ID'].to_numpy()
    ratings = filter_data['Rating'].to_numpy(dtype=np.float64)
    return user_ids, cloth_ids,ratings

def cloth_rating_distrubution(data,show_fig=True):
    cloth_ids = data['Clothing ID']
    cloth_rating_counts = Counter(cloth_ids)
    if show_fig:
        all_counts = list(cloth_rating_counts.values())
        all_counts.sort(reverse = True)
        plt.plot(np.array(all_counts))
        plt.show()
    filter_cloths  = np.array([k for k,v in cloth_rating_counts.items() if int(v) >= cloth_count_threshold])
    filter_data = data.copy().loc[data['Clothing ID'].isin(filter_cloths)]
    rename_cloth_ids(filter_data)
    return filter_data

def rename_cloth_ids(filter_data):
    cloth_ids = filter_data['Clothing ID']
    unique_ids = set(cloth_ids)
    id_map = {cloth_id:i for i,cloth_id in enumerate(unique_ids)}
    def update_cloth_ids(row, id_map=id_map):
        x = row['Clothing ID']
        return id_map[x]
    filter_data['New Clothing ID'] = filter_data.apply(update_cloth_ids, axis=1)

def get_final_score(recommender_scores, sentiment_scores, rec_cloth_ids):
    data_tuple = []
    for r, s, ids in zip(recommender_scores, sentiment_scores, rec_cloth_ids):
        if math.isnan(r):
            final_score = round(s, 3)
        else:
            final_score = round(alpha * s + (1 - alpha) * r, 3)
        data_tuple.append((ids, final_score))
    data_tuple = sorted(data_tuple,key=lambda x: x[1],reverse=True)
    recommended_ids = [int(v[0]) for v in data_tuple]
    recommended_score = [float(v[1]) for v in data_tuple]
    # visualize_scores(data_tuple)
    return recommended_ids, recommended_score


def visualize_scores(data_tuple):
    for ids, final_score in data_tuple:
        print("cloth id : {} , prediction score : {}".format(ids, final_score))
