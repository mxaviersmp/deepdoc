# Projeto deepdoc-petrobras

## backend

Access the backend folder

Create a new python virtual environment if it doesnt exists: `virtualenv .venv`

Activate the virtual environment: `source .venv/bin/activate`

Install the backend requirements if a new one was created: `pip install -r requirements.txt`

To run the backend server run the script: `./run_backend.sh`

To index the files: `localhost:5000/create`

To convert and index new files: `localhost:5000/add/folder?path=<folder-path>&ocr=<boolean>`

To perform a search for terms: `localhost:5000/search/terms?query=<term>,<term>,...`

To perform a search for tags: `localhost:5000/search/tags?query=<tag>`

To perform an advanced search: `localhost:5000/search/advanced?and=<term>,...&or=<term>,...&not=<term>,...`

To get the pdf file: `localhost:5000/pdf?file=<file-path>&ocr=<boolean>`

## frontend

To run the frontend, access the frontend folder and run: `npm install`

Then run: `npm start`
