from http.server import BaseHTTPRequestHandler, HTTPServer
import numpy as np
from scipy.sparse import csr_matrix
from data_reader import (
    csr_vstack, read_ratings_data,
    get_anime_name_from_rebased_index, get_rebased_anime_from_title)
from recommenders import DistanceRecommender
import logging
from timeit import default_timer as timer


class AnimeHandler(BaseHTTPRequestHandler):
    def _ok_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._ok_response()

    def do_POST(self):
        global ratings_data, positive_ratings_data, positive_ratings_csr
        post_data = self.rfile.read(int(self.headers['Content-Length']))

        t0 = timer()
        anime_titles = post_data.decode('utf-8').split(';')
        anime_indices = []
        for title in anime_titles:
            if title == '':
                continue
            try:
                anime_indices.append(get_rebased_anime_from_title(title))
            except Exception as e:
                logging.info(f'Got exception while handling titles: {e}')
        logging.info(f'User provided {len(anime_indices)} animes:')
        for anime_index in anime_indices:
            anime_name = get_anime_name_from_rebased_index(anime_index)
            logging.info(anime_name)
        user_csr_row = csr_matrix((
            np.ones((len(anime_indices), )),
            (
                [0 for i in range(len(anime_indices))],
                anime_indices
            )
        ), shape=(1, positive_ratings_csr.shape[1]))
        positive_ratings_plus_user_csr = csr_vstack(positive_ratings_csr, user_csr_row)
        t1 = timer()
        logging.info(f'User request handling time: {t1 - t0} seconds')

        recommender = DistanceRecommender()
        recommender.fit(positive_ratings_plus_user_csr)
        top_anime_indices = recommender.get_best_items_for_user(
            positive_ratings_plus_user_csr.shape[0] - 1, n=10, exclude_items=anime_indices)

        recommendation = ''
        logging.info('Recommended animes:')
        for top_anime_index in top_anime_indices:
            anime_name = get_anime_name_from_rebased_index(top_anime_index, show_id=False)
            logging.info(anime_name)
            recommendation += anime_name + '\n'
        t2 = timer()
        logging.info(f'Recommendation calculation time: {t2 - t1} seconds')

        self._ok_response()
        self.wfile.write(f"{recommendation}".encode('utf-8'))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)

    server_address = (input('Enter server IP:\n'), int(input('Enter server port:\n')))
    logging.info(f'Running server on {server_address}')

    t0 = timer()
    ratings_data, positive_ratings_data, positive_ratings_csr = read_ratings_data()
    t1 = timer()
    logging.info(f'Data loading time: {t1 - t0} seconds')

    http_server = HTTPServer(server_address, AnimeHandler)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        logging.info('Server was interrupted')
    http_server.server_close()
