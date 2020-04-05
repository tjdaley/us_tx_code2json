from whoosh.qparser import MultifieldParser, FuzzyTermPlugin
from whoosh.index import open_dir

index = open_dir('index')

parser = MultifieldParser(['section_name', 'text', 'section_number'], schema=index.schema)
parser.add_plugin(FuzzyTermPlugin())

query = parser.parse('insurance reasonable cost')
with index.searcher() as searcher:
    results = searcher.search(query)
    for result in results:
        code_name = result['code_name']
        section_number = result['section_number']
        section_name = result['section_name']
        text = result['text']
        print(f"{code_name} Section {section_number} - {section_name}\n\n{text}")
        print('-' * 120)
