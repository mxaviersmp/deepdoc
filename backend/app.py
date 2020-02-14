from flask import Flask, request, send_file
from flask_cors import CORS
from indexer_whoosh import Indexer
import json

app = Flask(__name__)
CORS(app)
indexer = Indexer('docs', 'index-directory')


@app.route('/search/term')
def search_term():
    """
    API endpoint for searching indexed files by terms
    :return: result of search
    """
    query = request.args.get('query')
    query = query.split(',')
    query = {"AND": query}
    query = json.dumps(query)
    return indexer.search_documents(query)


@app.route('/search/tag')
def search_tag():
    """
    API endpoint for searching files with given tag
    :return: result of search
    """
    query = request.args.get('query')
    query = {"TAG": [query]}
    query = json.dumps(query)
    return indexer.search_documents(query, False)


@app.route('/search/advanced')
def advanced_search():
    """
    API endpoint for performing advanced search on indexed files
    :return: result of search
    """
    and_query = request.args.get('and')
    or_query = request.args.get('or')
    not_query = request.args.get('not')
    query = {"AND": and_query.split(','), "OR": or_query.split(','), "NOT": not_query.split(',')}
    query = json.dumps(query)
    return indexer.search_documents(query, True, True)


@app.route('/create')
def create():
    """
    API endpoint for indexing existing documents
    :return: result of indexing
    """
    if indexer.create_searchable_data():
        return 'Indexing successful'
    return 'Error indexing data'


@app.route('/add/folder')
def add_folder():
    """
    API endpoint for extracting text and indexing new files
    :return: result of indexing
    """
    folder_path = request.args.get('path')
    allow_ocr = bool(request.args.get('ocr'))
    if indexer.add_documents_to_index(folder_path, allow_ocr):
        return 'Files indexed successfully'
    return 'Error indexing files'


@app.route('/pdf')
def pdf():
    """
    API endpoint for retrieving pdf file
    :return: pdf file
    """
    file_path = request.args.get('file')
    try:
        return send_file(file_path, mimetype='application/pdf')
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run()
