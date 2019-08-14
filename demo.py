"""
A simple program to demo the API.
"""

from donnees.rcan_coll import *


def main():
    coll = RCollection('/data/rali6/Tmp/gottif/radiocan/data/articles_ici.radiocanada.ca-extracted/')
    # A directory on your local machine will improve performance tenfold!

    for doc in coll.find():
        # access the JSON file keys directly...
        is_dispatch = doc['IsDispatch']

        # ... or use the RDocument fields and functions for ease of use.
        title = doc.title
        paragraph_list = doc.extract_body_paragraphs()
        summary = doc.summary
        theme = doc.theme
        subthemes = doc.subthemes

        # We can print most of the content here for a demo.
        print(f"Document {doc.id} ============= {doc.url}")
        print(f"{title}\n")
        print('Summary ' + '-' * 10)
        print(summary)
        print('Body ' + '-' * 10)
        print('\n'.join(paragraph_list))
        print('-' * 10)
        print(f"Theme is {theme['id']} ({theme['name']})")
        print(f"Subthemes are: {', '.join([str(x['id']) + ' (' + x['name'] + ')' for x in subthemes])}\n")


if __name__ == '__main__':
    main()
