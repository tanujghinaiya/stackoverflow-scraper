import os
import requests

from soscrape.utils.session import get_session
from soscrape.utils.tor_session import TorSession


class RequestsHandler:
    def __init__(self, tor_session_renew_list=(403, 408, 429), max_renews=5):
        self.max_renews = max_renews
        self.renew_list = tor_session_renew_list
        self.tor_session = TorSession()
        self.session = get_session(tor_session=self.tor_session)

    def get(self, url, attempt=0, **kwargs):
        try:
            res = self.session.get(url, **kwargs)

            if res.status_code in self.renew_list and attempt < self.max_renews:
                self.tor_session.renew_identity()
                return self.get(url, attempt=attempt + 1, **kwargs)

            return res
        except requests.ConnectTimeout as e:
            print(e)
        except requests.ConnectionError as e:
            print(e)
        except requests.HTTPError as e:
            print(e)

    def get_file(self, url, file_path):
        if os.path.isfile(file_path):
            # print('Already Exists : %s' % self.file_path.split('/')[-1])
            return

        req = self.get(url=url, stream=True)

        if req.status_code is 200:
            with open(file_path, 'wb') as f:
                for chunk in req.iter_content(1024):
                    f.write(chunk)

            return True
        else:
            print(req.status_code)
            # print(req.content)
            return False

    def __del__(self):
        self.tor_session.terminate()
        self.session.close()
