import pytest
import os
from app.file_search import locate_files_in_path, zip_up_files, locate_files_in_multiple_paths

TEST_PATH = 'test_directory'


def test_locate_files():
    files = locate_files_in_path(TEST_PATH, 'brukl', 'pdf').result()
    assert len(files) == 5


def test_extension_txt():
    files = locate_files_in_path(TEST_PATH, ext='txt').result()
    assert len(files) == 2


def test_no_extension():
    files = locate_files_in_path(TEST_PATH, 'not').result()
    assert len(files) == 2


def test_no_phrase_no_extension():
    files = locate_files_in_path(TEST_PATH).result()
    assert len(files) == 11


def test_case_sensitive():
    files = locate_files_in_path(TEST_PATH, 'brukl', ignore_case=False).result()
    assert len(files) == 3


def test_multiple_paths():
    all_files = locate_files_in_multiple_paths(['test_directory/brukl', 'test_directory/extra_dir'], ext='pdf')
    assert len(all_files) == 5


def test_zip_files():
    files = ['test_directory/BRUKL_first.pdf',
             'test_directory/case_sens_BRukL.pdf',
             'test_directory/first_brukl.pdf',
             'test_directory/brukl/brukl_find.pdf']

    archive = zip_up_files(files)
    assert os.path.exists(archive)
    os.remove(archive)
