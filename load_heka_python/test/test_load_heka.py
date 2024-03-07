import sys

sys.path.append(r"C:\fMRIData\git-repo\load-heka-python")

from .runners import heka_reader_tester
from os.path import join
import pytest


class TestFiles:
    """
    run as `pytest . -s` to see running output, as each individual
    test can take some time to run through all series.
    """

    @pytest.fixture
    def base_path(self):
        return r"C:\fMRIData\git-repo\load-heka-python\ee_test_files\stim_extraction"

    def test_f1_v2x90_2(self, base_path):

        version = "f1_v2x90.2"
        group_num_series_num_to_test = [["1", "1"], ["1", "18"], ["5", "6"], ["7", "3"], ["8", "16"]]
        heka_reader_tester(base_path, version, group_num_series_num_to_test, dp_thr=1e-04)

    def test_f2_v2x90_2(self, base_path):

        version = "f2_v2x90.2"
        group_num_series_num_to_test = [
            ["1", "4"],
            ["1", "1"],
            ["1", "2"],
            ["1", "3"],
            ["1", "4"],
            ["1", "5"],
            ["1", "6"],
            ["1", "7"],
            ["1", "8"],
            ["1", "9"],
        ]
        heka_reader_tester(base_path, version, group_num_series_num_to_test, dp_thr=1e-02)

    def test_f3_v2x90_2(self, base_path):

        version = "f3_v2x90.2"
        group_num_series_num_to_test = [
            ["1", "1"],
            ["1", "2"],
            ["1", "3"],
            ["1", "4"],
            ["1", "5"],
            ["1", "6"],
            ["1", "7"],
            ["1", "8"],
            ["1", "9"],
        ]
        heka_reader_tester(base_path, version, group_num_series_num_to_test, dp_thr=1e-03)

    def test_f4_v2x90_5(self, base_path):

        version = "f4_v2x90.5"
        group_num_series_num_to_test = [
            ["1", "1"],
            ["1", "2"],
            ["1", "3"],
            ["1", "4"],
            ["1", "5"],
            ["1", "14"],
            ["1", "16"],
            ["1", "17"],
            ["1", "18"],
            ["1", "19"],
            ["1", "20"],
            ["1", "22"],
            ["1", "23"],
            ["1", "24"],
            ["1", "25"],
            ["1", "26"],
            ["1", "27"],
            ["1", "28"],
            ["1", "29"],
            ["1", "30"],
            ["1", "31"],
            ["1", "32"],
            ["1", "33"],
            ["1", "34"],
            ["1", "35"],
            ["1", "36"],
            ["2", "1"],
            ["2", "2"],
            ["2", "3"],
            ["2", "4"],
            ["2", "5"],
            ["2", "6"],
            ["2", "7"],
            ["2", "9"],
            ["2", "12"],
            ["2", "14"],
            ["2", "15"],
            ["2", "16"],
            ["2", "18"],
            ["2", "21"],
            ["2", "24"],
            ["2", "25"],
            ["2", "26"],
            ["2", "27"],
            ["2", "28"],
            ["2", "29"],
            ["2", "30"],
            ["2", "31"],
            ["2", "32"],
            ["2", "33"],
            ["2", "34"],
            ["2", "35"],
            ["2", "36"],
            ["2", "37"],
            ["2", "38"],
            ["2", "39"],
            ["2", "40"],
        ]
        heka_reader_tester(base_path, version, group_num_series_num_to_test, dp_thr=1e-03)

    def test_f5_v2x90_5(self, base_path):
        version = "f5_v2x90.5"
        group_num_series_num_to_test = [
            ["1", "1"],
            ["1", "4"],
            ["1", "5"],
            ["1", "6"],  # ["3", "3"], series has records with three channels
            ["1", "7"],
            ["3", "9"],
            ["5", "6"],
            ["5", "8"],
            ["5", "10"],
            ["6", "2"],
            ["6", "14"],
            ["6", "20"],
        ]
        heka_reader_tester(base_path, version, group_num_series_num_to_test, dp_thr=1e-03)

    def f6_1_2_0_build_1469(self, base_path):
        version = "f6_1.2.0_[Build 1469]"
        group_num_series_num_to_test = [
            ["1", "1"],
            ["1", "2"],
            ["1", "3"],
            ["1", "4"],  # ["1", "6"] series has records with three channels
            ["1", "5"],
            ["1", "7"],
            ["1", "8"],
            ["1", "9"],
            ["1", "10"],
            ["1", "11"],
            ["1", "12"],
            ["1", "13"],
        ]
        heka_reader_tester(base_path, version, group_num_series_num_to_test, assert_time=False, dp_thr=1e-02)

    def f7_1_2_0_build_1469(self, base_path):

        version = "f7_1.2.0_[Build 1469]"
        group_num_series_num_to_test = [
            ["1", "1"],
            ["1", "2"],
            ["1", "3"],
            ["1", "4"],
            ["1", "5"],  # ["1", "8"], series has records with three channels
            ["1", "6"],
            ["1", "7"],
            ["1", "9"],
            ["1", "10"],
            ["1", "11"],
            ["1", "12"],
            ["1", "13"],
            ["1", "14"],
        ]
        heka_reader_tester(base_path, version, group_num_series_num_to_test, dp_thr=1e-03)

    def test_f8_v2x65(self, base_path):
        """Stimulus reconstruction for versions before 2x90 is not supported"""
        version = "f8_v2x65"
        group_num_series_num_to_test = [["1", "6"], ["1", "13"], ["3", "1"]]
        heka_reader_tester(base_path, version, group_num_series_num_to_test, dp_thr=1e-05, include_stim_protocol=False)

    def test_f9_v2x65(self, base_path):
        """Stimulus reconstruction for versions before 2x90 is not supported"""
        version = "f9_v2x65"
        group_num_series_num_to_test = [["1", "1"], ["1", "2"]]
        heka_reader_tester(base_path, version, group_num_series_num_to_test, dp_thr=1e-04, include_stim_protocol=False)

    def test_f10_v2x91(self, base_path):
        version = "f10_v2x91"
        group_num_series_num_to_test = [["1", "1"], ["1", "3"], ["1", "5"], ["1", "9"]]
        heka_reader_tester(base_path, version, group_num_series_num_to_test, dp_thr=1e-04)

    def test_f11_v2x90_3(self, base_path):
        """
        This is an annoying file that is offset by 0.005 s in the software (x_start = 0.005) but
        cannot export it in such a way that it is relative to the sweep but maintains
        the 0.05 s offset - the software is correcting it somewhere but not making the
        option to turn off correction available (at least that I could find).
        This is not a severe issue for our tests as the time is read correctly, just
        the offset is not automatically removed (as it is in HEKA).
        Nonetheless Vm is loading well so keep here as a successful test.

        There is also a problem with the stimulus, which is all zeros in the
        file but was loading with array dimension longer than the time of the recording
        in load_heka, so is loaded as False. This is most likely due to the user manually stopping
        the recording before it has finished.
        """
        version = "f11_v2x90.3"
        group_num_series_num_to_test = [["1", "1"], ["1", "2"], ["1", "4"], ["1", "11"], ["1", "12"]]
        heka_reader_tester(
            base_path,
            version,
            group_num_series_num_to_test,
            dp_thr=1e-04,
            assert_time=False,
            include_stim_protocol=False,
        )

    def test_f12_v2x90_4(self, base_path):
        """
        The same issue with some stimulus reconstruction as described above is observed on this
        test file. However, most stimulus are reconstructed successfully, further suggesting it
        is a problem with the user manually stopping the recording too quickly.
        """
        version = "f12_v2x90.4"
        group_num_series_num_to_test = [["1", "1"], ["1", "3"], ["1", "5"], ["3", "3"]]
        heka_reader_tester(base_path, version, group_num_series_num_to_test, dp_thr=1e-03, include_stim_protocol=False)

    def test_f13_v2x92(self, base_path):
        """
        This is the only file that contains interleaved records.
        Some stimulus are NaN in this file, so not included.
        """
        version = "f13_v2x92"
        group_num_series_num_to_test = [["1", "4"], ["2", "2"], ["3", "4"], ["5", "4"], ["6", "2"]]
        heka_reader_tester(base_path, version, group_num_series_num_to_test, dp_thr=1e-04, include_stim_protocol=False)

    def test_1_4_1_with_leak(self, base_path):
        """"""
        version = "f14_1.4.1[Build 1036]leak"
        group_num_series_num_to_test = [["1", "1"], ["2", "2"], ["4", "3"]]
        heka_reader_tester(
            base_path, version, group_num_series_num_to_test, dp_thr=1e-04, include_stim_protocol=False, has_leak=True
        )
