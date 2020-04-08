"""
app.py - Retrieve text of codified statutes and convert to JSON

Copyright (c) 2020 by Thomas J. Daley, J.D.
"""
import argparse
import glob
import json
import os
from whoosh.index import create_in, exists_in, open_dir
from util.classifier import Classifier
from util.htmltotext import HtmlToText
from util.retriever import Retriever
import util.functions as FN

INDEX_PATH = FN.INDEX_PATH


def progress_bar(total, current):
    bar = 'Progress: ['
    percent = int(current/total*100)
    bar += '*' * percent
    bar += ' ' * (100-percent)
    bar += ']'
    print(bar, end='\r')


def main(args):
    classifier = Classifier()
    htmltotexter = HtmlToText()
    config = FN.code_config(args.code)
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


def edit_code_files(args):
    """
    Modify this method as needed to do whatever file editing needs to be done.
    """
    config = FN.code_config(args.code)
    files = glob.glob(f"{config['code_name']}-Chapter-*.json")
    prog_total = len(files)
    prog_current = 0
    for file in files:
        prog_current += 1
        if args.progress:
            progress_bar(prog_total, prog_current)
        try:
            with open(file, 'r') as fp:
                sections = json.load(fp)
        except Exception as e:
            print(f'\n Error reading {file}: {str(e)}')
            break
        for section in sections:
            section['code'] = config['code_name']
        try:
            with open(file, 'w') as fp:
                json.dump(sections, fp, indent=4)
        except Exception as e:
            print(f'\nError writing {file}: {str(e)}')
            break

    print('\n')


def create_index(args):
    schema = FN.schema()

    if not os.path.exists(INDEX_PATH):
        os.mkdir(INDEX_PATH)
    ix_name = FN.index_name(args)
    create_in(INDEX_PATH, schema, indexname=ix_name)
    print(f"Index '{ix_name}' created at this path: {INDEX_PATH}")


def index_content(args):
    config = FN.code_config(args.code)
    ix_name = FN.index_name(None)

    # Create index if it does not already exist.
    if not FN.index_exists(args):
        create_index(args)

    # Open our index
    index = FN.open_index(args)

    # Process every section in this codified law
    if not args.chapter:
        files = glob.glob(f"{config['code_name']}-Chapter-*.json")
    else:
        files = [f"{config['code_name']}-Chapter-{args.chapter}.json"]

    prog_total = len(files)
    prog_current = 0
    for file in files:
        # Open next chapter in the codified law
        with open(file, 'r') as chapter_file:
            chapter = json.load(chapter_file)

        # If we don't have any sections in that chapter, there was probably a
        # snafu upstream, but there's nothing we can do about it now. skip it.
        if not chapter:
            continue

        # We have a chapter with sections . . . process them
        if not args.quiet and not args.progress:
            print('-' * 80)
            print(chapter[0]['chapter'], "- indexing")
        with index.writer(limitmb=256, procs=3, multisegment=True) as writer:
            for section in chapter:
                section_number = section.get('section_number')
                section_name = section.get('section_name')
                chapter_name = section.get('chapter')
                if not args.quiet and not args.progress:
                    print(f"Indexing {section_number} - {section_name}", end='')
                writer.add_document(
                    code_name=section.get('code_name'),
                    title=section.get('title'),
                    subtitle=section.get('subtitle'),
                    chapter=chapter_name,
                    subchapter=section.get('subchapter'),
                    section_number=section_number,
                    section_name=section_name,
                    text=section.get('text'),
                    code=section.get('code')
                )
                if not args.quiet and not args.progress:
                    print(" - added")
        if not args.quiet and not args.progress:
            print(f"{chapter_name} - committed to index {ix_name}")
        if args.progress:
            prog_current += 1
            progress_bar(prog_total, prog_current)
    print('')


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
        "--get",
        required=False,
        help="Indicates whether to go get the statutory text",
        action='store_const',
        const=True,
        default=False
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
        '--edit',
        required=False,
        help="Indicates whether edit_code_files() is to be called.",
        action='store_const',
        const=True,
        default=False
    )
    parser.add_argument(
        '--quiet',
        required=False,
        help="Indicates whether we run as silently as we know how.",
        action='store_const',
        const=True,
        default=False
    )
    parser.add_argument(
        '--progress',
        required=False,
        help="Indicates whether to display a progress bar instead of progress messages.",
        action='store_const',
        const=True,
        default=False
    )

    args = parser.parse_args()

    if args.get:
        main(args)

    if args.edit:
        edit_code_files(args)

    if args.index:
        index_content(args)
