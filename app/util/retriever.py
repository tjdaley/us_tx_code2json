"""
retriever.py - Retrieve text of statutes

Copyright (c) 2020 by Thomas J. Daley, J.D.
"""
import requests
from time import sleep


class Retriever(object):
    def __init__(self, base_url: str, code_abbreviation: str):
        self.base_url = base_url
        self.code_abbreviation = code_abbreviation

    def retrieve(self, chapter: int) -> str:
        url = self.make_url(chapter)
        print(url, end=" - ")
        retry = True
        retry_remaining = 5
        while retry:
            try:
                retry_remaining -= 1
                response = requests.get(url)
                retry = False
                print(response.status_code, end=" - ")
                if response.status_code != 404:
                    return response.text
            except ConnectionResetError as e:
                print(str(e))
                sleep(5)
            except ConnectionError as e:
                print(str(e))
                sleep(5)
            except Exception as e:
                print(str(e))
                retry = False

        return None

    def make_url(self, chapter: int) -> str:
        return f'{self.base_url}/Docs/{self.code_abbreviation}/htm/{self.code_abbreviation}.{chapter}.htm'
