"""
app.py - Retrieve text of codified statutes and convert to JSON

Copyright (c) 2020 by Thomas J. Daley, J.D.
"""
import argparse
import json
from util.classifier import Classifier
from util.htmltotext import HtmlToText
from util.retriever import Retriever


def main(args):
    classifier = Classifier()
    htmltotexter = HtmlToText()
    with open(f'codes/{args.code.lower()}.json', 'r') as config_file:
        config = json.load(config_file)
    code_name = config['code_name']
    retriever = Retriever('https://statutes.capitol.texas.gov', code_name)

    if args.chapter:
        chapters = [args.chapter]
        skip_chapters = []
    else:
        chapters = [str(i) for i in range(config['chapter_range_low'], config['chapter_range_high'])]
        for chapter in config['add_chapters']:
            chapters.append(chapter)
        skip_chapters = config['skip_chapters']

    for chapter in chapters:
        if chapter in skip_chapters:
            continue
        html_content = retriever.retrieve(chapter)
        if not html_content:
            print("(end)")
            continue
        text_content = htmltotexter.get_text(html_content)
        print("txt extracted", end=" - ")
        code = classifier.classify_doc(text_content)
        print("classified", end=" - ")
        chap_num = str(chapter).rjust(3, '0')
        with open(f'{code_name}-Chapter-{chap_num}.json', 'w') as json_file:
            json.dump(code, json_file)
        print("json saved")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Encode Texas Codified Laws')
    parser.add_argument('--code', required=True, help="Two-letter abbreviation for code to process")
    parser.add_argument('--chapter', required=False, help="Chapter number to process instead of entire codified law")
    args = parser.parse_args()
    main(args)
