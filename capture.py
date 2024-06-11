from abc import ABC, abstractmethod
import requests
import os

class Capture(ABC):
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.session = self.create_session_with_retries(max_retries)

    def create_session_with_retries(self, max_retries):
        session = requests.Session()
        retry_strategy = requests.packages.urllib3.util.retry.Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def download_file(self, link):
        filename = os.path.join(self.download_dir, link.split("/")[-1])
        with self.session.get(link) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                f.write(r.content)

    @abstractmethod
    def run(self):
        ...