import logging
from typing import Dict, List
import requests
from .data_classes import Hotel
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type

class BaseSupplier:
    @staticmethod
    def endpoint():
        """URL to fetch supplier data"""

    @staticmethod
    def parse(obj: Dict) -> Hotel:
        """Parse supplier-provided data into Hotel object"""

    @retry(retry=retry_if_exception_type(requests.exceptions.RequestException),
           wait=wait_fixed(2),
           stop=stop_after_attempt(3))
    def fetch(self) -> List[Hotel]:
        url = self.endpoint()
        try:
            logging.info(f"Fetching data from {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses
            data = response.json()
            logging.info(f"Received {len(data)} records from {url}")
            return [self.parse(dto) for dto in data]
        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP error from {url}: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error from {url}: {str(e)}")
            return []