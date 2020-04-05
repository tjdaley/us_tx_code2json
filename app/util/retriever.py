"""
retriever.py - Retrieve text of statutes

Copyright (c) 2020 by Thomas J. Daley, J.D.
"""
import requests


class Retriever(object):
    def __init__(self, base_url: str, code_abbreviation: str):
        self.base_url = base_url
        self.code_abbreviation = code_abbreviation

    def retrieve(self, chapter: int) -> str:
        url = self.make_url(chapter)
        print(url, end=" - ")
        response = requests.get(url)
        print(response.status_code, end=" - ")
        if response.status_code == 404:
            return None
        html_content = response.text
        return html_content

    def make_url(self, chapter: int) -> str:
        return f'{self.base_url}/Docs/{self.code_abbreviation}/htm/{self.code_abbreviation}.{chapter}.htm'
