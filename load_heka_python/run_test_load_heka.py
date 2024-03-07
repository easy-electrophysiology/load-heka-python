from test import test_load_heka
from os.path import join, basename, dirname
import glob


def test_file(test_path, dp_thr=1e-6, info_type="max_dp_match", assert_mode=False):
    """
    Convenience function around test_load_heka.test_heka_reader()

    To test your file, first export the data from Patchmaster. Make sure stimulus is on (Tweak > Export > tick 'Stimulus'),
    Zero offset is subtracted and display filter is off (see README.md for more details).
    Export the series you want to test under the filename (and in the same directory as the test file):

    e.g. if your filename is test_file.dat

    ./.../test_file/test_file.dat
                    test_file_group-1_series-1.asc
                    test_file_group-1_series-2.asc ...

    """
    base_path = dirname(test_path)
    version = basename(test_path)
    ascii_files = glob.glob(join(test_path, "*_group-?_series-?.asc"))
    filenames = list(map(basename, ascii_files))

    if len(ascii_files) == 0:
        raise Exception("no files found in " + base_path)

    group_series_to_test = [[filename.split("group-")[1][0], filename.split("series-")[1][0]] for filename in filenames]

    test_load_heka.test_heka_reader(base_path, version, group_series_to_test, dp_thr, info_type, assert_mode)
