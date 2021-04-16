import datetime
import re
import os
import fnmatch
import zipfile
from typing import Optional
from unsync import unsync, Unfuture


class SearchMatch:
    """Individual class for assets, individual file instances"""

    def __init__(self, path):
        self.path = path
        self.file_name = os.path.basename(self.path)
        self.tags = []
        file_details = os.stat(self.path)

        self.date_created = datetime.datetime.fromtimestamp(int(file_details.st_ctime)).strftime('%Y-%m-%d %H:%M:%S')
        self.date_modified = datetime.datetime.fromtimestamp(int(file_details.st_mtime)).strftime('%Y-%m-%d %H:%M:%S')
        self.last_accessed = datetime.datetime.fromtimestamp(int(file_details.st_atime)).strftime('%Y-%m-%d %H:%M:%S')

        self.size = file_details.st_size / 1000.0
        self.file_type = self.path.split('.')[-1]

    def __repr__(self):
        return f'SearchMatch({self.path})'


@unsync
def locate_files_in_path(path: str,
                         key_phrase: Optional[str] = None,
                         ext: Optional[str] = None,
                         ignore_case: bool = True) -> list[str]:
    ext = ext or '*'
    key_phrase = key_phrase or ''
    glob_pat = f'*{key_phrase}*.{ext}'
    flags = re.IGNORECASE if ignore_case else 0
    rule = re.compile(fnmatch.translate(glob_pat), flags=flags)

    return [os.path.join(root, file) for root, dirs, files in os.walk(path) for file in files if rule.match(file)]


@unsync
async def result_processor(single_path_task: list[Unfuture]) -> list[SearchMatch]:
    output = []
    for task in single_path_task:
        result: list[str] = await task
        if not result:
            continue
        output.extend(SearchMatch(path) for path in result)
    return output


def locate_files_in_multiple_paths(paths: list[str],
                                   key_phrase: Optional[str] = None,
                                   ext: Optional[str] = None,
                                   ignore_case: bool = True) -> list[SearchMatch]:
    return result_processor(
        [locate_files_in_path(path, key_phrase=key_phrase, ext=ext, ignore_case=ignore_case) for path in
         paths]).result()


def zip_up_files(files: list[str], save_location: Optional[str] = None, archive_name: Optional[str] = None) -> str:
    archive_name = f'{archive_name}.zip' or 'BRUKL_archive.zip'
    save_location = save_location or os.path.dirname(__file__)
    archive_path = os.path.join(save_location, archive_name)
    archive = zipfile.ZipFile(archive_path, 'w')
    for no, file in enumerate(files, 1):
        new_name = f'{no}_{os.path.basename(file)}'
        archive.write(file, new_name, compress_type=zipfile.ZIP_DEFLATED)
    archive.close()
    return archive_path
