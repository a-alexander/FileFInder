import pytest
import os
from app.brukl_extraction import locate_files, zip_up_files


def test_locate_files():
    test_path = '.'
    files = locate_files(test_path, 'brukl', 'pdf')
    assert files
    assert len(files) == 3


def test_zip_files():
    files = ['BRUKL_first.pdf',
             'case_sens_BRukL.pdf',
             'first_brukl.pdf']

    archive = zip_up_files(files)
    assert os.path.exists(archive)
    os.remove(archive)


