from whoosh.fields import Schema, TEXT, ID, KEYWORD, STORED
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
from whoosh.scoring import Frequency
from whoosh.analysis import RegexTokenizer, StopFilter
from text_from_pdf import TextFromPDF
from collections import defaultdict
import os
from glob import glob
import json
import numpy as np
import pandas as pd
import re
from termcolor import colored


class Indexer:
    def __init__(self, documents_folder, index_folder):
        """
        Class responsible for handling indexation, tagging and search of documents
        :param documents_folder: path where files containing text from pdfs will be saved
        :param index_folder: path where the index will be created
        """
        self._keywords = {}
        for cat in glob('keywords/*.json'):
            with open(cat, 'r') as f:
                keywords = json.load(f)
                self._keywords.update(keywords)
        with open('tags.json', 'r') as f:
            self._tags = json.load(f)
        self._keywords_array = self._get_keywords_array()
        self._writer = None
        self._index_folder = index_folder
        self._text_extractor = TextFromPDF(documents_folder, self._index_folder)

    def create_searchable_data(self):
        """
        Creates index schema and indexes existing documents
        """
        # breaks text into tokens and remove portuguese stopwords
        analyzer = RegexTokenizer() | StopFilter(lang='por')
        # schema for file indexing
        # title: title of the document, # path: path to the document
        # content: text from the document, # tags: tags of the document
        # categories: tags from document grouped in corresponding categories
        schema = Schema(
            title=TEXT(stored=True),
            path=ID(stored=True, unique=True),
            content=TEXT(analyzer=analyzer, stored=True, phrase=True),
            tags=KEYWORD(lowercase=True, commas=True),
            categories=STORED()
        )
        # creates index following schema on directory
        create_in(f'{self._index_folder}', schema).close()
        data = pd.read_csv(f'{self._index_folder}/indexed_files.csv', index_col='name')
        data['indexed'] = 0
        data.to_csv(f'{self._index_folder}/indexed_files.csv')
        return self.add_documents_to_index()
 
    def add_documents_to_index(self, folder_path=None, allow_ocr=False):
        """
        Indexes new documents
        :param folder_path: path where to index documents from
        :param allow_ocr: if allowed to run OCR on documents
        :return: if indexing process was successful
        """
        if folder_path:
            self._text_extractor.extract_text_from_pdfs(folder_path, allow_ocr)
        paths = self._get_all_file_paths()
        ix = open_dir(f'{self._index_folder}')
        try:
            # opens index writer that will parallelize job
            self._writer = ix.writer(procs=os.cpu_count(), limitmb=256)
            self._add_to_writer(paths)
            print('Committing indexes')
            # commits new documents
            self._writer.commit()
            ix.close()
            # register new indexed documents
            file_names = [p.split('/')[-1][:-4] for p in paths]
            data = pd.read_csv(f'{self._index_folder}/indexed_files.csv', index_col='name')
            data.loc[file_names, ['indexed']] = 1
            data.to_csv(f'{self._index_folder}/indexed_files.csv')
            return True
        except Exception as e:
            print(colored(e, 'red'))
            # cancel documents indexation
            self._writer.cancel()
            ix.close()
            return False   

    def search_documents(self, query_str, terms=True, advanced=False):
        """
        Search for documents respecting query restrictions
        :param query_str: query arguments in format {'AND': [...], 'OR': [...], 'NOT': [...], 'TAG': [...] }
        :param terms: whether to perform a search by terms within the documents
        :param advanced: whether to perform an advanced search in the documents
        :return: documents found respecting query restrictions
        """
        query_json = json.loads(query_str)
        query_str_list = self._get_query_list(query_json, terms, advanced)
        query_str = self._get_query_str(query_str_list, terms, advanced)
        # opens register of indexed documents
        ix = open_dir(f'{self._index_folder}')
        # choose score function depending on type of search
        scorer = Frequency()
        with ix.searcher(weighting=scorer) as searcher:
            # choose where to search depending on type of search
            query = QueryParser('content' if terms else 'tags', ix.schema).parse(query_str)
            data = {'results': []}
            results = searcher.search(query, limit=None)
            for hit in results:
                content = hit['content']
                if not self._get_hit_validity(query_json, terms, advanced, content):
                    continue
                occurrences = {}
                score = 0
                # calculates number of matches for each term
                for q in query_str_list:
                    positions = [(t.start(), t.end()) for t in re.finditer(self._normalize_text(q), content)]
                    occurrences[q] = len(positions)
                    score += len(positions)
                occurrences = json.dumps(occurrences, ensure_ascii=False)
                data['results'].append({
                    'title': hit['title'],
                    'path': hit['path'],
                    'occurrences': occurrences,
                    'categories': hit['categories'],
                    'score': score
                })
        ix.close()
        if terms:
            data['results'].sort(key=lambda x: x['score'], reverse=True)
        return json.dumps(data, ensure_ascii=False)

    def _add_to_writer(self, paths):
        """
        Adds documents to be indexed to the writer
        :param paths: paths of documents to be indexed
        """
        data = pd.read_csv(f'{self._index_folder}/indexed_files.csv', index_col='name')
        for path in paths:
            with open(path, 'r') as fp:
                print(f'Indexing {path}')
                content = fp.read()
                content = self._process_content(content)
                # gets document name from path
                file_name = path.split('/')[-1][:-4]
                # gets document original pdf file path
                file_path = data.loc[file_name, 'pdf_path']
                tags, categories = self._get_file_tags_categories(content)
                self._writer.add_document(
                    title=file_name,
                    path=file_path,
                    content=content,
                    tags=tags,
                    categories=categories
                )

    def _normalize_text(self, text):
        """
        Transform text to lowercase and remove all accentuation
        :param text: string to be normalized
        :return: normalized string
        """
        txt = text.lower()
        txt = txt.strip()
        txt = re.sub('[áàâãä]', 'a', txt)
        txt = re.sub('[éèêë]', 'e', txt)
        txt = re.sub('[íìîï]', 'i', txt)
        txt = re.sub('[óòôõö]', 'o', txt)
        txt = re.sub('[úùûü]', 'u', txt)
        txt = re.sub('[ç]', 'c', txt)
        return txt

    def _process_content(self, content):
        """
        Processes content of document for indexation
        :param content: raw document content
        :return: document content processed
        """
        # turn line breaks into spaces, turning string into one line
        content = content.replace('\n', ' ')
        content = ' ' + self._normalize_text(content) + ' '
        return content

    def _get_file_tags_categories(self, content):
        """
        Infers document tags and categories using specific vocabulary
        :param content: document text
        :return: document tags and categories
        """
        # escape characters to help identifying keywords more precisely
        esc = "[](){}.,;:/~'\" "
        keywords_frequency = {}
        # for each keyword finds positions of occurrences in the content and check if it's valid using escape characters
        for kw in self._keywords_array:
            positions = [(t.start() - 1, t.end()) for t in re.finditer(kw, content)]
            valid = 0
            for s, e in positions:
                if content[s] in esc and content[e] in esc:
                    valid += 1
            if valid:
                keywords_frequency[kw] = valid
        # now for each valid keywords discover it's tag
        tag_occurrences = defaultdict(int)
        tags_frequency = []
        for kw, f in keywords_frequency.items():
            for t in self._get_keyword_tags(kw):
                tag_occurrences[t] += f
                [tags_frequency.append(t) for _ in range(f)]
        # then associate each category with the found tags
        categories_tags = defaultdict(list)
        for t, f in tag_occurrences.items():
            categories_tags[self._get_tag_category(t)].append((t, f))
        # now filters categories
        for cat in categories_tags:
            total = 0
            for _, f in categories_tags[cat]:
                total += f
            # to count as valid, a tag must amount for at least thresh of that category occurrence
            thresh = 0.15 if cat in ['assunto', 'escala'] else 0.00
            categories_tags[cat] = list(filter(lambda x: x[1]/total >= thresh, categories_tags[cat]))
            # categories_tags[cat] = [max(categories_tags[cat], key=lambda x: x[1])]
        return ','.join(tags_frequency), json.dumps(categories_tags, ensure_ascii=False)

    def _get_keyword_tags(self, keyword):
        """
        Gets the tags associated with the keyword
        :param keyword: keyword
        :return: tags of keyword
        """
        tags = []
        for tag, kws in self._keywords.items():
            if keyword in kws:
                tags.append(tag)
        return tags

    def _get_tag_category(self, tag):
        """
        Gets the category of the keyword
        :param tag: tag
        :return: category of the tag
        """
        return self._tags[tag]

    def _get_keywords_array(self):
        """
        Gets an array of all possible keywords
        :return: array of keywords
        """
        keywords_list = []
        for v in self._keywords.values():
            for kw in v:
                keywords_list.append(kw)
        return np.array(keywords_list)

    def _get_query_list(self, query_json, terms, advanced):
        """
        Constructs a list of terms to search depending on the type of search
        :param query_json: dictionary with query parameters
        :param terms: whether is a search for terms
        :param advanced: whether is an advanced search
        :return: list of terms to search
        """
        query_str_list = []
        # if a search for terms builds list of terms
        if terms:
            # if an advanced search gets terms from 'AND', 'OR' and 'NOT'
            if advanced:
                for query in query_json.values():
                    for term in query:
                        query_str_list.append(term)
            # else gets only terms from 'AND'
            else:
                query_str_list = query_json['AND']
        # else gets only the tag to be searched
        else:
            query_str_list = query_json['TAG']
        return query_str_list

    def _get_query_str(self, query_str_list, terms, advanced):
        """
        Constructs a query string depending on the type of search
        :param query_str_list: list of terms to construct string
        :param advanced: whether is an advanced search
        :return: query string
        """
        if not terms:
            return query_str_list[0]
        query_str = [f'"{self._normalize_text(query)}"' for query in query_str_list]
        if advanced:
            query_str = ' OR '.join(query_str)
        else:
            query_str = ' AND '.join(query_str)
        return query_str

    def _get_hit_validity(self, query_json, terms, advanced, content):
        """
        Checks if the found document is valid depending on search conditions
        :param query_json: dictionary with query parameters
        :param terms: whether is a search for terms
        :param advanced: whether is an advanced search
        :param content: document text
        :return: whether the result if valid
        """
        if terms:
            # checks if every 'AND' term is in the document
            for term in query_json['AND']:
                if self._normalize_text(term) not in content:
                    return False
            if advanced:
                # checks if no 'NOT' term is in the document
                for term in query_json['NOT']:
                    if self._normalize_text(term) in content:
                        return False
        return True

    def _get_all_file_paths(self):
        """
        Gets the paths of all non indexed documents
        :return: paths of documents
        """
        data = pd.read_csv(f'{self._index_folder}/indexed_files.csv', index_col='name')
        indexed = list(data[data['indexed'] == 0]['txt_path'].values)
        return indexed
