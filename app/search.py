from whoosh.qparser import MultifieldParser, FuzzyTermPlugin
from whoosh.index import open_dir

import util.functions as FN

parser = MultifieldParser(['section_name', 'text', 'section_number'], schema=FN.schema())
parser.add_plugin(FuzzyTermPlugin())
index = open_dir(FN.INDEX_PATH, FN.index_name(None))

query_text = input("Query: ")
code_list = input("Codes (*=All): ")
while query_text != '':
    if code_list != '*' and code_list != '':
        codes = code_list.upper().split(',')
        code_clauses = [f'code:{c} ' for c in codes]
        code_clause = ' OR '.join(code_clauses)
        query_text = query_text + ' ' + code_clause
    query = parser.parse(query_text)
    print(query)
    with index.searcher() as searcher:
        result = searcher.search(query)
        for doc in result:
            code_name = doc.get('code_name', "NO CODE NAME")
            section_number = doc.get('section_number', "NO SECTION NUMBER")
            section_name = doc.get('section_name', "NO SECTION NAME")
            text = doc.get('text', "NO TEXT")
            default_code = "NO CODE"
            code = doc.get('code', default_code)
            if code != default_code:
                print(f"{code}: {code_name} Section {section_number} - {section_name}\n")
                print(doc.get('title', "NO TITLE"))
                print(doc.highlights('text'))
                print('-' * 120)

    query_text = input("Query: ")
