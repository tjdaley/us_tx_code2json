"""
app.py - Retrieve text of codified statutes and convert to JSON

Copyright (c) 2020 by Thomas J. Daley, J.D.
"""
import argparse
import glob
import json
import os
from whoosh.index import create_in, open_dir
from whoosh.fields import DATETIME, Schema, TEXT
from util.classifier import Classifier
from util.htmltotext import HtmlToText
from util.retriever import Retriever

INDEX_PATH = 'index'


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
        chap_num = str(chapter).rjust(5, '0')
        with open(f'{code_name}-Chapter-{chap_num}.json', 'w') as json_file:
            json.dump(code, json_file)
        print("json saved")


def create_index(args):
    schema = Schema(
        code_name=TEXT(),
        title=TEXT,
        subtitle=TEXT,
        chapter=TEXT,
        subchapter=TEXT,
        section_number=TEXT(stored=True),
        section_name=TEXT(stored=True),
        text=TEXT(stored=True),
        future_effective_date=DATETIME
    )

    if not os.path.exists(INDEX_PATH):
        os.mkdir(INDEX_PATH)
    ix = create_in(INDEX_PATH, schema)
    print(f"Index created at this path: {INDEX_PATH}")


def index_content(args):
    with open(f'codes/{args.code.lower()}.json', 'r') as config_file:
        config = json.load(config_file)

    index = open_dir(INDEX_PATH)

    files = glob.glob(f"{config['code_name']}-Chapter-*.json")
    for file in files:
        with open(file, 'r') as chapter_file:
            chapter = json.load(chapter_file)
        with index.writer(limitmb=256, procs=3, multisegment=True) as writer:
            for section in chapter:
                section_number = section.get('section_number')
                section_name = section.get('section_name')
                chapter_name = section.get('chapter')
                print(f"Indexing {section_number} - {section_name}", end='')
                writer.add_document(
                    code_name=section.get('code_name'),
                    title=section.get('title'),
                    subtitle=section.get('subtitle'),
                    chapter=chapter_name,
                    subchapter=section.get('subchapter'),
                    section_number=section_number,
                    section_name=section_name,
                    text=section.get('text')
                )
                print(" - added")
        print(f"{chapter_name} - committed")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Encode Texas Codified Laws')
    parser.add_argument(
        '--code',
        required=True,
        help="Two-letter abbreviation for code to process"
    )
    parser.add_argument(
        '--chapter',
        required=False,
        help="Chapter number to process instead of entire codified law"
    )
    parser.add_argument(
        '--index',
        required=False,
        help="Indicates whether to run the indexing process. If omitted, will just download and text-prep the codified statutes",
        action='store_const',
        const=True,
        default=False
    )
    parser.add_argument(
        '--create_index',
        required=False,
        help="Indicates whether to create the initial index schema",
        action='store_const',
        const=True,
        default=False
    )
    args = parser.parse_args()

    if not args.index and not args.create_index:
        main(args)
        exit()

    if args.create_index:
        create_index(args)
        exit()

    if args.index:
        index_content(args)
        exit()
