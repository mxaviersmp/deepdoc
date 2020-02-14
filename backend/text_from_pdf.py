import textract
import os
from multiprocessing import Pool
from termcolor import colored
import pandas as pd


class TextFromPDF:
    def __init__(self, documents_folder, index_folder):
        """
        Class responsible for extracting text from pdf files
        :param documents_folder: path where files containing text from pdfs will be saved
        :param index_folder: path where the index will be created
        """
        self._allow_ocr = False
        self._existing = []
        self._paths = []
        self._documents_folder = documents_folder
        self._index_folder = index_folder
        if not os.path.exists(f'{self._index_folder}'):
            os.mkdir(f'{self._index_folder}')
            with open(f'{self._index_folder}/indexed_files.csv', 'w') as f:
                print('name,pdf_path,txt_path,indexed', file=f)

    def extract_text_from_pdfs(self, root, allow_ocr=False):
        """
        Processes a batch of pdf files in a folder
        :param root: path to the pdf files to be processed
        :param allow_ocr: whether to allow performing OCR on pdf files
        """
        self._prepare_for_extraction(root, allow_ocr)
        os.environ['OMP_THREAD_LIMIT'] = '1'
        Pool(os.cpu_count()).map(self._text_from_pdf, self._paths)
        self._reset_state()

    def _text_from_pdf(self, pdf_file):
        """
        Performs text extraction on a pdf file
        :param pdf_file: path to the pdf file to be processed
        """
        print(f'Extracting from {pdf_file}')
        try:
            # uses simple text extraction on file
            texts = textract.process(pdf_file)
            # infers if it was able to extract text from file
            valid_text = len(texts.split()) > 1000
            if not valid_text:
                # if text extraction was not successful and OCR is allowed
                if self._allow_ocr:
                    txt = colored(f'Running OCR on {pdf_file}', 'yellow')
                    print(txt)
                    texts = textract.process(pdf_file, method='tesseract', lang='por')
                    valid_text = True
            # decodes text to a readable format
            texts = texts.decode('utf-8')
            # tries to mitigate word breaks due to line breaks
            texts = texts.replace('-\n', '')
            name = pdf_file.split('/')[-1]
            output_file = f'{self._documents_folder}/{name}.txt'
            if valid_text:
                # if the text was extracted from the file, saves and register it
                with open(f'{self._index_folder}/indexed_files.csv', 'a') as f:
                    print(f'{name},{pdf_file},{output_file},0', file=f)
                with open(output_file, 'w') as f:
                    print(texts, file=f)
        except Exception as e:
            print(colored(e, 'red'))

    def _prepare_for_extraction(self, root, allow_ocr):
        """
        Updates class parameters for the text extraction process
        :param root: path to the pdf files to be processed
        :param allow_ocr: whether to allow performing OCR on pdf files
        """
        self._allow_ocr = allow_ocr
        if os.path.isdir(root):
            self._get_all_file_paths(root)
        else:
            self._paths = [root]
        self._get_existing_files()
        self._paths = [path for path in self._paths if path not in self._existing]

    def _reset_state(self):
        """
        Resets class parameters after the text extraction process
        """
        self._allow_ocr = False
        self._existing = []
        self._paths = []

    def _get_existing_files(self):
        """
        Excludes files already processed from new text extraction
        """
        if not os.path.exists(self._documents_folder):
            os.mkdir(self._documents_folder)
        else:
            self._existing = list(pd.read_csv(f'{self._index_folder}/indexed_files.csv')['pdf_path'].values)

    def _get_all_file_paths(self, path):
        """
        Collects the paths for all pdf files inside root folder and its subdirectories
        :param path: current directory path
        """
        file_paths = [os.path.join(path, p) for p in os.listdir(path)]
        for p in file_paths:
            if os.path.isdir(p):
                self._get_all_file_paths(p)
            else:
                if p.split('.')[-1] == 'pdf':
                    self._paths.append(p)
