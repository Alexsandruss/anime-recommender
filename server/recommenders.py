import pandas as pd
import numpy as np
import daal4py as d4p
from sklearn.metrics.pairwise import cosine_distances


class BaseRecommender:
    def filter_items(self, items: list, exclude_items: list=None, n: int = None):
        if exclude_items is not None:
            for exclude_item in exclude_items:
                items.remove(exclude_item)
        if n is None:
            return items
        else:
            return items[:n]


# warning: this recommender works only on x86 systems
class ImplicitALSRecommender(BaseRecommender):
    def __init__(self, n_factors: int = 32, max_iterations: int = 10,
                 alpha_confidence: float = 40, lambda_regularization: float = 0.01):
        self.n_factors = n_factors
        self.max_iterations = max_iterations
        self.alpha_confidence = alpha_confidence
        self.lambda_regularization = lambda_regularization

    def fit(self, x):
        init_algorithm = d4p.implicit_als_training_init(
            nFactors=self.n_factors, method='fastCSR')
        init_result = init_algorithm.compute(x)

        training_algorithm = d4p.implicit_als_training(
            nFactors=self.n_factors, maxIterations=self.max_iterations,
            alpha=self.alpha_confidence, lambda_=self.lambda_regularization,
            method='fastCSR')
        training_result = training_algorithm.compute(x, init_result.model)

        self.users_factors = training_result.model.UsersFactors
        self.items_factors = training_result.model.ItemsFactors

    def predict_(self, user_id: int, item_id: int):
        return np.matmul(self.users_factors[user_id, :], self.items_factors[item_id, :])

    def get_best_items_for_user(self, user_id: int, n: int = None, exclude_items: set = None):
        item_rates = np.matmul(self.users_factors[[user_id], :], self.items_factors.T)
        item_rates = pd.Series(item_rates.reshape((-1,))).sort_values(ascending=False)
        result = list(item_rates.index.values)
        return self.filter_items(result, exclude_items, n)


class DistanceRecommender(BaseRecommender):
    def __init__(self, n_similar: int = 256, distance_func=cosine_distances):
        self.n_similar = n_similar
        self.distance_func = distance_func

    def fit(self, x):
        self.x = x

    def get_best_items_for_user(self, user_id: int, n: int = None, exclude_items: list = None):
        user_distances = self.distance_func(self.x[user_id, :], self.x)
        user_distances = pd.Series(user_distances.reshape((-1,))).sort_values(ascending=True)[:self.n_similar]
        item_rates = pd.Series(np.array(self.x[user_distances.index, :].todense()).sum(axis=0)).sort_values(ascending=False)
        result = list(item_rates.index.values)
        return self.filter_items(result, exclude_items, n)
