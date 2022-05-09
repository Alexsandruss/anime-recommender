import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
import os


def csr_vstack(a, b):
    if a.shape[1] != b.shape[1]:
        raise ValueError('"a" and "b" have different number of columns')
    c = a.copy()
    c.data = np.hstack((c.data, b.data))
    c.indices = np.hstack((c.indices, b.indices))
    c.indptr = np.hstack((c.indptr, (b.indptr + c.nnz)[1:]))
    c._shape = (c.shape[0] + b.shape[0], b.shape[1])
    return c


anime_data, unique_users, unique_animes = None, None, None


def read_ratings_data(rating_threshold: int = 7):
    global anime_data, unique_users, unique_animes

    # reading of animes
    anime_data = pd.read_csv('anime.csv', index_col='MAL_ID')

    # create anime titles txt list for Android application suggestions
    anime_titles_file = 'anime_titles.txt'
    if not os.path.isfile(anime_titles_file):
        anime_data['Name'].to_csv(anime_titles_file, index=False, header=None)

    # reading of ratings
    ratings_data = pd.read_csv('rating_complete.csv')

    # treat ratings > `threshold` as positive
    positive_ratings_data = ratings_data[ratings_data['rating'] > rating_threshold].drop(columns=['rating'])

    # rebase user and anime ids to (0, max_unique)
    user_codes, unique_users = pd.factorize(positive_ratings_data['user_id'])
    anime_codes, unique_animes = pd.factorize(
        positive_ratings_data['anime_id'])

    positive_ratings_data['user_id'] = user_codes
    positive_ratings_data['anime_id'] = anime_codes

    # create sparse matrix of ratings
    positive_ratings_csr = csr_matrix(
        (np.ones((positive_ratings_data.shape[0], )),
         (positive_ratings_data['user_id'], positive_ratings_data['anime_id'])))

    return ratings_data, positive_ratings_data, positive_ratings_csr


# mapping of indices and titles
def get_original_user_from_rebased(idx: int): return unique_users[idx]
def get_original_anime_from_rebased(idx: int): return unique_animes[idx]
def get_rebased_user_from_original(idx: int): return unique_users.get_loc(idx)
def get_rebased_anime_from_original(idx: int): return unique_animes.get_loc(idx)

def get_rebased_anime_from_title(title: str):
    global anime_data
    original_idx = anime_data['Name'][anime_data['Name'] == title].index[0]
    return get_rebased_anime_from_original(original_idx)

# align anime name and index
def get_anime_name_from_rebased_index(idx, show_id=True, show_genres=True):
    global anime_data

    anime_info = anime_data.loc[get_original_anime_from_rebased(idx)]
    result = ""
    if show_id:
        result += f'[id={idx}] '
    result += anime_info['Name']
    if show_genres:
        result += f' [{anime_info["Genres"]}]'
    return result
