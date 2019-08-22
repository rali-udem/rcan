"""
Atelier de résolution de problèmes industriels 2019.

(c) RALI, Université de Montréal.
Fabrizio Gotti - gottif.
"""
import sys

from bs4 import BeautifulSoup
import lxml
import orjson
import os

_theme_dict = {}
_subtheme_dict = {}
_res_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + 'resources'


class RCollection:
    def __init__(self, col_spec: str):
        """
        :param col_spec: A path containing the JSon files of the collection.
        """
        if not os.path.exists(col_spec):
            raise ValueError(f"Invalid directory {col_spec}")

        self.col_spec = col_spec

    def find(self):
        """
        :return: An iterator over the whole collection. Returns an RDocument object for every document in the
        collection.
        """
        class RCollectionIt:
            def __init__(self, directory):
                self.dir = directory
                self.scan_it = os.scandir(self.dir)

            def __iter__(self):
                return self

            def __next__(self):
                next_file_entry = next(self.scan_it)
                next_file = os.path.join(self.dir, next_file_entry.name)

                doc = None
                try:
                    result = orjson.loads(open(next_file, 'r', encoding='utf-8').read())
                    result['source_file'] = next_file
                    doc = RDocument(result)
                except:
                    print("Problem reading file " + next_file)

                return doc

        return RCollectionIt(self.col_spec)


class RDocument:
    """
    A few utilities to manipulate documents.
    """
    id: str
    summary: str
    title: str
    url: str

    def __init__(self, dictionary: dict):
        self._d = dictionary
        self.id = self._d['_id']
        self.title = self._d['SearchableTitle']
        self.summary = self._d['SearchableSummary']
        self.url = self._d['FirstPublishedCanonicalWebLink']

    def __getitem__(self, item):
        return self._d[item]

    def __contains__(self, item):
        return item in self._d

    def extract_body_paragraphs(self) -> list:
        """
        Returns the concatenation of the lead and the body of the article, after parsing html to get text. Some
        extraneous content may be found in the result since the body contains numerous heterogeneous elements,
        including 'related content' for instance. This list *does not* contain the title of the whole article
        but does include section headers.

        When the field BodyParagraphs is present in the underlying JSON, will simply return this value, otherwise
        will perform the extraction per se, which is much slower.

        :return: A list of text paragraphs (strings).
        """

        if 'BodyParagraphs' in self._d:
            result = self._d['BodyParagraphs']
        else:
            result = self._extract_body_paragraphs()

            # cache result
            self._d['BodyParagraphs'] = result

        return result

    def _extract_body_paragraphs(self):
        # guess the document type
        ledevoirdoc = 'ledevoir' in self.url

        # create an html of the full document, then parse
        full_html = '<div>' + self._d.get('Lead', '') + '</div> \n<div>' + self._d.get('Body', '') + '</div>'
        soup = BeautifulSoup(full_html, "lxml")

        if ledevoirdoc:
            # remove
            for n in soup.select('script, noscript, style'):
                n.decompose()
            # create text version
            result = [x.strip() for x in soup.get_text().split('\n') if len(x.strip()) > 1]
        else:  # radio-canada
            # remove copyright holders in figures, scripts, styles
            for n in soup.select('span.creator, span.copyrightHolder, script, noscript, style'):
                n.decompose()
            # create text version
            result = [x for x in soup.get_text().split('\n') if len(x.strip()) > 1]

        return result

    @property
    def theme(self) -> dict:
        """
        :return: A single theme, possibly none. A theme is a dict with keys 'id', 'name', 'codename', 'active'
        and 'subthemes', a list of subtheme ids loosely followed by Radio-Canada.
        """
        return _theme_dict[int(self._d['ThemeId'])]

    @property
    def subthemes(self) -> list:
        """
        :return: A possibly empty list of subthemes. A subtheme is a dict with keys 'id', 'name', 'codename', 'active'
        and 'theme', a possibly empty list of parent theme ids.
        """
        return [_subtheme_dict[int(x)] for x in self._d['SubThemeIds']]

    def write_to(self, output_file):
        """
        Writes the json to output_file
        :param output_file: Output file.
        :return: void
        """
        with open(output_file, 'wb') as fout:
            fout.write(orjson.dumps(self._d))


def get_theme(theme_id):
    return _theme_dict[int(theme_id)]


def get_subtheme(stheme_id):
    return _subtheme_dict[int(stheme_id)]


def load_resources():
    theme_file_name = os.path.join(_res_path, 'themes.tsv')
    if not os.path.exists(theme_file_name):
        print(f"Install the resource files in the dir {_res_path} before using this API.\n"
              f"See {os.path.join(_res_path, 'README.md')} for details.", file=sys.stderr)
        sys.exit(1)

    with open(theme_file_name, encoding='utf-8') as fin:
        for line in fin:
            parts = line.strip().split('\t')
            _theme_dict[int(parts[0])] = {'id': int(parts[0]), 'name': parts[1],
                                          'codename': parts[2], 'active': parts[3] == '1', 'subthemes': []}

    with open(os.path.join(_res_path, 'subthemes.tsv'), encoding='utf-8') as fin:
        for line in fin:
            clean_line = line.strip()
            if clean_line:
                parts = clean_line.split('\t')
                _subtheme_dict[int(parts[0])] = {'id': int(parts[0]), 'name': parts[1], 'codename': parts[2],
                                                 'active': parts[3] == '1',
                                                 'comment': parts[4] if len(parts) >= 5 else '', 'theme': []}

    rels = orjson.loads(open(os.path.join(_res_path, 'theme_soustheme_relationship.json'), 'r', encoding='utf-8').read())
    for theme in rels:
        theme_id = int(theme['ThemeId'])
        subthemes = [int(x) for x in theme['SubThemeIds']]
        _theme_dict[theme_id]['subthemes'] = subthemes

        for sub in subthemes:
            assert len(_subtheme_dict[sub]['theme']) == 0, 'A single parent please.'
            _subtheme_dict[sub]['theme'] = theme_id


load_resources()
