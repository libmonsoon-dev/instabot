import pickle
import json
import random
from time import sleep

from requests import Session, Response
from requests.exceptions import HTTPError
from fake_useragent import FakeUserAgent

from .logger import logging, debug_wrapper, stringify_object
from .types import Any, Dict, Mode, HttpMethod


class InstagramAPI(object):
    BASE_URL = 'https://www.instagram.com'

    @debug_wrapper
    def __init__(self, *, username: str, password: str, query_hash: str, limit: int, mode: Mode, ajax_header: str,
                 requests_interval: float, random_intervals: bool, session_file_path: str = 'session.pickle'):
        self.username: str = username
        self.password: str = password
        self.query_hash: str = query_hash
        self.limit: int = limit
        self.mode: str = mode
        self.requests_interval: float = requests_interval
        self.random_intervals: bool = random_intervals
        self.session_file_path: str = session_file_path

        self.send_requests_qty = 0
        self.user_id: int = None
        self.session: Session = None
        self.user_agent: str = FakeUserAgent().random
        self.defaultHeaders: Dict[str, str] = {
            "User-Agent": self.user_agent,
            "Accept": "*/*",
            "Accept-Language": "en,en-US;q=0.7,ru;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.instagram.com/accounts/login/?source=auth_switcher",
            "X-Instagram-AJAX": ajax_header,  # TODO: find this variable source
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "DNT": "1",
            "Connection": "keep-alive",
            "TE": "Trailers",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }

    @debug_wrapper
    def request(self, method: HttpMethod, url: str, **kwargs) -> Response:
        url = f'{self.BASE_URL}{url}'
        logging.debug(url)

        r = self.session.request(
            method,
            url,
            **kwargs,
        )

        r.raise_for_status()
        self.update(cookies=r.cookies)
        return r

    @debug_wrapper
    def update(self, cookies=None):
        if cookies:
            self.session.cookies.update(cookies)

        self.defaultHeaders.update({
           "X-CSRFToken": self.session.cookies['csrftoken'],
        })
        self._backup_session_()

    @debug_wrapper
    def _init_session_(self) -> None:
        self.session = Session()

        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en,en-US;q=0.7,ru;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        r = self.session.get(
            self.BASE_URL,
            headers=headers,
        )

        r.raise_for_status()
        self.session.cookies.update(r.cookies)
        assert self.session.cookies['csrftoken']
        self.update()

    @debug_wrapper
    def login(self) -> None:
        self._restore_session_()
        if not self.session or not self.user_id:
            self._init_session_()
            self._login_()

        # self._get_user_page()
        logging.info(f'User {self.username} successfully logged in')

    @debug_wrapper
    def _login_(self) -> None:
        headers = {
            **self.defaultHeaders,
            'Referer': 'https://www.instagram.com/accounts/login/?source=auth_switcher',
        }

        data = dict(
            username=self.username,
            password=self.password,
            queryParams='{"source": "auth_switcher"}',
        )

        r = self.request(
            'POST',
            '/accounts/login/ajax/',
            data=data,
            headers=headers,
            cookies=self.session.cookies
        )

        r.raise_for_status()

        self.update(cookies=r.cookies)

        login_response = r.json()

        assert login_response['status'] == 'ok'
        assert login_response['authenticated']

        self.user_id = login_response['userId']

    # @debug_wrapper
    # def _get_user_page(self) -> None:
    #     self.request(
    #         'GET',
    #         f'/{self.username}/',
    #         headers={
    #             **self.defaultHeaders,
    #             'Referer': f'{self.BASE_URL}/{self.username}/'
    #         }
    #     )

    @debug_wrapper
    def get_following_data(self, after: str = None):
        logging.info('loading new page...')
        url = f'{self.BASE_URL}/graphql/query/'

        assert self.username
        assert self.user_id

        params_variables = {
            "id": self.user_id,
            "include_reel": True,
            "fetch_mutual": False,
            "first": 24
        }

        if after:
            params_variables["first"] = 12
            params_variables["after"] = after

        params = {
            'query_hash': self.query_hash,  # TODO: find this variables source
            'variables': json.dumps(params_variables)
        }

        headers = {
            **self.defaultHeaders,
            'Referer': f'https://www.instagram.com/{self.username}/following/'
        }

        r = self.session.get(
            url=url,
            params=params,
            headers=headers,
        )

        r.raise_for_status()
        self.update(cookies=r.cookies)
        return r.json()

    @debug_wrapper
    def unfollow(self, target_user_id: int) -> Dict[str, Any]:
        assert self.user_id
        assert self.username

        url = f'{self.BASE_URL}/web/friendships/{target_user_id}/unfollow/'
        headers = {
            **self.defaultHeaders,
            'Referer': f'{self.BASE_URL}/{self.username}/following/'
        }

        r = self.session.post(
            url=url,
            headers=headers
        )

        r.raise_for_status()
        self.update(cookies=r.cookies)
        return r.json()

    @debug_wrapper
    def main_loop(self):
        if self.mode == 'unfollow':
            self.unfollow_loop()
        else:
            raise ValueError(f'Invalid mode {self.mode}')

    @debug_wrapper
    def unfollow_loop(self):
        has_next_page, end_cursor = self.unfollow_on_page()

        while self.send_requests_qty < self.limit and has_next_page:
            has_next_page, end_cursor = self.unfollow_on_page(after=end_cursor)

    @debug_wrapper
    def unfollow_on_page(self, after: str = None):
        data = self.get_following_data(after=after)

        edge_follow = data['data']['user']['edge_follow']
        page_info = edge_follow['page_info']
        end_cursor: str = page_info['end_cursor']
        has_next_page: bool = page_info['has_next_page']
        nodes: list = edge_follow['edges']
        logging.debug(f'end_cursor={end_cursor}, has_next_page={has_next_page}')

        for node in nodes:
            user = node['node']
            logging.debug(stringify_object(node))
            if not user['followed_by_viewer']:
                continue
            logging.info(f'[{self.send_requests_qty + 1}/{self.limit}] Unfollow user {user["username"]}')
            try:
                self.unfollow(user['id'])
                self.send_requests_qty += 1
            except HTTPError as error:
                logging.warning(error)
            self.wait()

        return has_next_page, end_cursor

    @debug_wrapper
    def _backup_session_(self) -> None:
        with open(self.session_file_path, 'wb') as file:
            pickle.dump((self.session, self.user_id), file)

    @debug_wrapper
    def _restore_session_(self) -> None:
        try:
            with open(self.session_file_path, 'rb') as file:
                self.session, self.user_id = pickle.load(file)
                self.update()
        except FileNotFoundError as e:
            logging.debug(e)

    @debug_wrapper
    def wait(self):
        if self.random_intervals:
            interval = (self.requests_interval / 2) + random.uniform(0, self.requests_interval)
        else:
            interval = self.requests_interval

        sleep(interval)

    @debug_wrapper
    def close(self):
        self.session.close()
