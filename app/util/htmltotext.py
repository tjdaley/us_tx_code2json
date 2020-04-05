"""
htmltotext.py - Convert HTML to Markdown text.

Copyright (c) 2020 by Thomas J. Daley, J.D.
"""
import html2text


class HtmlToText(object):
    def __init__(self):
        self.converter = html2text.HTML2Text()

    def get_text(self, html_content: str) -> str:
        text_content = self.converter.handle(html_content)
        return text_content
