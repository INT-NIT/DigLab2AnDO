import os
import tempfile
import shutil
import pathlib
test_directory = pathlib.Path(tempfile.gettempdir()) / 'diglab2bids_testfiles'


def initialize_test_directory(clean=True):
    """
    Create main test folder if required

    Parameters
    ----------
    clean: (bool)
        Remove test folder first in case it exists.

    Returns
    -------
    test_directory: (str)
        path of the test directory
    """
    if clean and os.path.exists(test_directory):
        shutil.rmtree(test_directory)

    if not os.path.exists(test_directory):
        os.mkdir(test_directory)
    packaged_testfolder = pathlib.Path(__file__).parent / 'test_files'
    shutil.copytree(packaged_testfolder, test_directory / 'test_files')

    return test_directory

