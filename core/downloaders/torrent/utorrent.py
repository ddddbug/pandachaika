import re
from tempfile import NamedTemporaryFile
from typing import Union

import requests
from requests.exceptions import RequestException
from requests.auth import HTTPBasicAuth

from core.base.types import TorrentClient


class uTorrent(TorrentClient):

    name = 'utorrent'
    convert_to_base64 = False
    send_url = False

    def __str__(self) -> str:
        return self.name

    def add_torrent(self, torrent_data: Union[str, bytes], download_dir: str=None) -> bool:

        self.total_size = 0
        self.expected_torrent_name = ''
        lf = NamedTemporaryFile()
        lf.write(torrent_data)

        params = {'action': 'add-file', 'token': self.token}
        files = {'torrent_file': open(lf.name, 'rb')}
        try:
            response = requests.post(
                self.UTORRENT_URL,
                auth=self.auth,
                params=params,
                files=files,
                timeout=25).json()
            lf.close()
            if 'error' in response:
                return False
            else:
                return True
        except RequestException:
            lf.close()
            return False

    def add_url(self, url: str, download_dir: str=None) -> bool:

        self.total_size = 0
        self.expected_torrent_name = ''

        params = {'action': 'add-url', 'token': self.token, 's': url}
        try:
            response = requests.get(
                self.UTORRENT_URL,
                auth=self.auth,
                # cookies=self.cookies,
                params=params,
                timeout=25).json()
            if 'error' in response:
                return False
            else:
                return True
        except RequestException:
            return False

    def connect(self) -> bool:
        self.UTORRENT_URL = '%s:%s/gui/' % (self.address, self.port)
        UTORRENT_URL_TOKEN = '%stoken.html' % self.UTORRENT_URL
        REGEX_UTORRENT_TOKEN = r'<div[^>]*id=[\"\']token[\"\'][^>]*>([^<]*)</div>'
        self.auth = HTTPBasicAuth(self.user, self.password)
        try:
            r = requests.get(UTORRENT_URL_TOKEN, auth=self.auth, timeout=25)
            self.token = re.search(REGEX_UTORRENT_TOKEN, r.text).group(1)
            return True
        except requests.exceptions.RequestException:
            return False
        # guid = r.cookies['GUID']
        # self.cookies = dict(GUID=guid)

    def __init__(self, address: str='localhost', port: int=8080, user: str='', password: str='', secure: bool=True) -> None:
        super().__init__(address=address, port=port, user=user, password=password, secure=secure)
        self.auth = None
        self.token = None
        self.UTORRENT_URL = ''
