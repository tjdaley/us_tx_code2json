"""
functions.py - Various utility functions.

Copyright (c) 2020 by Thomas J. Daley, J.D.
"""
import glob
import json
import os

from whoosh.index import exists_in, open_dir
from whoosh.fields import DATETIME, Schema, TEXT


INDEX_PATH = 'index'


def schema():
    return Schema(
        code=TEXT(stored=True),
        code_name=TEXT(stored=True),
        title=TEXT(stored=True),
        subtitle=TEXT(stored=True),
        chapter=TEXT(stored=True),
        subchapter=TEXT(stored=True),
        section_number=TEXT(stored=True),
        section_name=TEXT(stored=True),
        text=TEXT(stored=True),
        future_effective_date=DATETIME(stored=True)
    )


def code_config(code_name: str) -> dict:
    """
    Open and load the configuration file for this code.

    Args:
        code_name (str): The two-letter abbreviation for the code, e.g. fa = Family Law
    Returns:
        (dict): Configuration file.
    """
    with open(f'codes/{code_name.lower()}.json', 'r') as config_file:
        config = json.load(config_file)
    return config


def enumerate_indices() -> list:
    """
    Examine the INDEX_PATH and gather a list of indices.

    Args:
        None
    Returns:
        (list): List of code abbreviations that have been indexed
    """
    files = glob.glob(f'{INDEX_PATH}/_??_*.toc')
    indices = []
    for toc in files:
        begin_position = toc.find('_', 0) + 1
        end_position = toc.find('_', begin_position+1)
        code_name = toc[begin_position:end_position]
        config = code_config(code_name)
        full_name = config.get('code_full_name', f"Texas {code_name.upper()} Code")
        indices.append({'code_name': code_name, 'full_code_name': full_name})
    return indices


def index_name(args) -> str:
    """
    This is *THE* way we create index names.
    I tried an experiment with putting each codified book into its own
    index, thus the commented code below.

    But I could not merge the search results properly, so now I'm back
    to indexing everying into one common index called 'main'.
    /tjd/ 2020-04-06

    Args:
        args (argpase): Argparse arguments. (somtimes passed as a str)

    Returns:
        (str): Index name we use for this code section
    """
    return 'main'
    # if isinstance(args, str):
    #     return args.lower().strip()
    # return args.code.lower().strip()


def index_exists(args) -> bool:
    """
    See if an index exists.

    Args:
        args (argparse): Argparse arguments
    Returns:
        (bool): True if the index exists, otherwise False.
    """
    if not os.path.exists(INDEX_PATH):
        return False
    return exists_in(INDEX_PATH, index_name(args))


def open_index(args):
    """
    Open an index for searching.

    Args:
        args (argparse): Argparse arguments.
    Returns:
        (whoosh.index): Instance of index
    """
    index = open_dir(INDEX_PATH, index_name(args))
    return index
