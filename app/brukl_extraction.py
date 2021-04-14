import re
import os
import fnmatch
import glob
import zipfile


def locate_files(path: str, key_phrase: str, ext: str) -> list[str]:
    glob_pat = f'*{key_phrase}*.{ext}'
    rule = re.compile(fnmatch.translate(glob_pat), re.IGNORECASE)
    return [n for n in glob.glob(os.path.join(path, '*')) if rule.match(n)]


def zip_up_files(files: list[str]) -> str:
    archive_name = 'BRUKL_archive.zip'
    archive_path = os.path.join(os.path.dirname(__file__), archive_name)
    archive = zipfile.ZipFile(archive_path, 'w')
    for file in files:
        archive.write(file, compress_type=zipfile.ZIP_DEFLATED)
    archive.close()
    return archive_path
