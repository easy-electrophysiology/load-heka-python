import warnings
import numpy as np
from load_heka import LoadHeka
from os.path import join

def test_heka_reader(base_path, version, group_series_to_test, dp_thr=1e-6, info_type="mean_dp_match", assert_mode=False):
    """
    Test the data read my LoadHeka matches the the data when loading into Patchmaster. Data must be exported from Patchmaster
    using 'Export Sweep' as ascii for comparison with LoadHeka. See the main README.md (section 5) on details
    on the file organisation and Export sweep options expceted by this function.

    Note that all tests are conducted with units scaled to pA, mV, s.

    This test function is a little unusual as by default it does not assert to an exact match between the data and Patchmaster.
    For reasons that are not currently clear (have emailed HEKA) the Im and Vm data does not match the exported HEKA sweep
    perfectly, but usually to around ~5 d.p. This varies a little between series. While this percision is sufficient, it would
    be nice if they matched perfectly, and we could test with assert to 7 d.p. (similar to time and stimulus protocol, which are
    not effected by this issue). Because of this, optiosn to print the average decimal place match, or the % of samples
    that match to dp_thr decimal places is provided.

    base_path - path to the test directory (see README.md)
    version - name you have given to this test file (see README.md)
    group_series_to_test - list of group numbers (not index) and series to test (in str format)
                           e.g. to test the third series of the second group, and the fourth series of the third group,
                           = [["2", "3"], ["3", "4"]]

    dp_thr - decimal place threshold, used as the number of decimal places to test matches to (for info_type = "perc_dp_match", "assert_dp_match")

    info_type -
               "mean_dp_match" - print the mean and standard deviation of the number of decimal places LoadHeka matches Patchmaster for Im
                                 and Vm data (scaled to pA and mV respectively). These are typically ~5

                "perc_dp_match" - print the percent of samples that match Patchmaster to dp_thr decimal places or more

                "assert_dp_match" - raise exception if any sample does not match Patchmaster to dp_thr decimal places or more

    assert_mode - Tests are usually printed so the results for all series are run. However, if assert_mode is True, an exception will be
                  raised if data and Patchmaster do not matched to pre-set cutoff values (see TestSeries().handle_assert() for details.
    """
    print("Testing " + version + "----------------------------------------------------------------------------------------------------------------\n")

    heka_file = LoadHeka(join(base_path, version, version + ".dat"),
                         only_load_header=True)

    for group_num, series_num in group_series_to_test:

        filename = version + "_group-{0}_series-{1}.asc".format(group_num,
                                                                series_num)

        raw_heka = read_heka_test_ascii(join(base_path, version, filename))

        supress_time = supress_stim = False
        for im_or_vm in ["Im", "Vm"]:

            load_heka = heka_file.get_series_data(im_or_vm,
                                                  int(group_num) - 1,
                                                  int(series_num) - 1,
                                                  include_stim_protocol=True)
            test = TestSeries(raw_heka,
                              load_heka,
                              group_num,
                              series_num,
                              dp_thr,
                              im_or_vm,
                              info_type,
                              assert_mode,
                              supress_time,
                              supress_stim,
                              )

            if test.stim_tested_flag:
                supress_stim = True
            if test.time_tested_flag:
                supress_time = True

        print("\n")

class TestSeries:
    def __init__(self, raw_heka, load_heka, group_num, series_num, dp_thr, im_or_vm, info_type, assert_mode, supress_time, supress_stim):
        """
        Class to test the Data (Im or Vm), reconstructued stimulus and time against exported Patchmaster data. Data is converted to pA
        and mV. For a reason that is not clear, the output of the Im and Vm data does not match HEKA perfectly, but to around 5 decimal
        places on average. This precision is sufficient but we have emailed HEKA to check if any additional settings are causing
        this slight difference. See test_heka_reader() for details.

        NOTES:
            For the HEKA exported data, the number of samples in each stimulus segment does not match the HEKA Gui. For example,
            e.g. in Heka test file f3, the stimulus segments should have 5000, 50000, 10000 samples.
            However the stimulus output actually as 5001, 50000, 4999 samples.

            Here the HEKA data are  shifted back 1 idx and extended 1 index so that the samples are correct (i.e. match the HEKA GUI)
             - this is done under the assumption that the HEKA GUI is correct.

            For the ramp, f2 group-1 series-8 should be 20,000 samples, 20,0000 samples, 20,000 samples. The first step of the ramp is sample 20,002,
            the last sample is 220,001 (this is exactly 200,000 samples). Thus the ramp does not start at 0 but at 0 + one step.

            Data and time must be tested per-sweep because they can be different lengths but the reconstructured stimulis is always the same num samples
            per sweep
        """
        self.raw_heka = raw_heka
        self.load_heka = load_heka
        self.group_num = group_num
        self.series_num = series_num
        self.im_or_vm = im_or_vm
        self.info_type = info_type
        self.assert_mode = assert_mode
        self.dp_thr = dp_thr
        self.stim_tested_flag = False
        self.time_tested_flag = False

        if self.info_type == "mean_dp_match":
            self.print_mean_and_sd_demical_place_match()
        else:
            sweeps_percent_close = self.get_list_of_percent_close_per_sweep()

            if sweeps_percent_close:
                if self.info_type == "perc_dp_match":
                    self.print_percent_over_deminal_place_match(sweeps_percent_close)

                if self.info_type == "assert_dp_match":
                    self.handle_assert(sweeps_percent_close, self.info_type)

        if not supress_time:
            self.test_time()

        if not supress_stim:
            self.test_reconstructed_stimulus()

# Test Im or Vm --------------------------------------------------------------------------------------------------------------------------------------

    def get_list_of_percent_close_per_sweep(self):
        """
        Continue i.e. if Vm skip Im
        """
        if not np.any(self.load_heka["data"]):
            return

        percent_close = []
        for raw_heka_sweep, load_heka_sweep in zip(self.raw_heka[self.im_or_vm],
                                                   self.load_heka["data"]):

            percent_close.append(self.percent_isclose(self.clean_data(raw_heka_sweep), self.clean_data(load_heka_sweep), self.dp_thr))

        return percent_close

    def print_mean_and_sd_demical_place_match(self):
        """
        """
        all_num_dp = []

        if not np.any(self.load_heka["data"]):
            return

        for raw_heka_sweep, load_heka_sweep in zip(self.raw_heka[self.im_or_vm],
                                                   self.load_heka["data"]):

            difference = self.clean_data(raw_heka_sweep, expected_len=len(load_heka_sweep)) - self.clean_data(load_heka_sweep)
            num_dp = self.num_dp(np.abs(difference))
            all_num_dp.append(num_dp)

        if all_num_dp:
            all_num_dp = np.hstack(all_num_dp)
            mean_dp = np.mean(all_num_dp)
            print("mean: {0:.2f}, sd: {1:.2} decimal place match Patchmaster for group {2} series {3} {4}".format(mean_dp,
                                                                                                                  np.std(all_num_dp),
                                                                                                                  self.group_num,
                                                                                                                  self.series_num,
                                                                                                                  self.im_or_vm))
            self.handle_assert(mean_dp, "mean_dp_match")

    def print_percent_over_deminal_place_match(self, sweeps_percent_close):
        """
        """
        mean_percent_close = np.mean(sweeps_percent_close)
        print("{0:.3f} percent of samples in group {1} series {2} match Pachmaster to {3} decimal places".format(mean_percent_close,
                                                                                                                 self.group_num,
                                                                                                                 self.series_num,
                                                                                                                 self.printable_dp()))
        self.handle_assert(mean_percent_close, "perc_dp_match")

# Test Time ------------------------------------------------------------------------------------------------------------------------------------------

    def test_time(self):
        """
        """
        if not np.any(self.load_heka["time"]):
            return

        time_sweeps_correct = []
        for raw_sweep_time, load_heka_sweep_time in zip(self.raw_heka["time_" + self.im_or_vm],
                                                        self.load_heka["time"]):

            sweep_correct = np.allclose(self.clean_time(raw_sweep_time, expected_len=len(load_heka_sweep_time)),
                                        load_heka_sweep_time,
                                        atol=1e-10, rtol=0)
            time_sweeps_correct.append(sweep_correct)

        if all(time_sweeps_correct):
            print("time correct for group {0} series {1}".format(self.group_num,
                                                                 self.series_num))
        else:
            print("Time INCORRECT for group {0} series {1}".format(self.group_num,
                                                                   self.series_num))
        self.time_tested_flag = True

        self.handle_assert(all(time_sweeps_correct), "test_time")


# Test Stimululus ------------------------------------------------------------------------------------------------------------------------------------

    def test_reconstructed_stimulus(self):
        """
        """
        if not self.load_heka["stim"]:
            return

        raw_stim = self.get_raw_stim()
        if raw_stim is False:
            return

        load_heka_stim = self.conv(self.load_heka["stim"]["data"], self.load_heka["stim"]["units"])  # stim output is A and V for consistency

        stim_is_close = np.allclose(raw_stim, load_heka_stim, atol=1e-07, rtol=0)

        if stim_is_close:
            print("stimulus was correctly reconstructed for group {0} series {1} {2}".format(self.group_num,
                                                                                             self.series_num,
                                                                                             self.im_or_vm))
        else:
            print("stimulus was NOT correctly reconstructed for group {0} series {1} {2}".format(self.group_num,
                                                                                                 self.series_num,
                                                                                                 self.im_or_vm))
        self.stim_tested_flag = True

        self.handle_assert(stim_is_close, "test_stim")

    def get_raw_stim(self):
        """
        raw stim is output from ascii script as ragged array of numpy, so necessary to check they are all the same size.
        We also need to fix the issue with HEKA export output, see __Init__ doc for details
        """
        raw_heka_output = self.raw_heka["stim_" + self.im_or_vm]

        if not self.all_sweeps_are_same_num_samples(raw_heka_output):
            warnings.warn("stimulus not tested, the record sizes are not equal for all sweeps")
            return False

        stim_data = self.clean_raw_stim(raw_heka_output)
        stim_data = stim_data[:, 1:]
        stim_data = np.append(stim_data, np.atleast_2d(stim_data[:, -1]).T, axis=1)

        return stim_data

# Utils ----------------------------------------------------------------------------------------------------------------------------------------------

    def handle_assert(self, param, test_type):
        """
        Assert if parameters for various tests do not fall over critial values.

        "assert_dp_match" - all samples must match Patchmaster data to more than the number of decimal places supplied in dp_thr. The 'param'
                            is a list of percent of samples that patch patchmaster to more than dp_thr decimal places

        "mean_dp_match" - param is the aveage number of decimal places that the data matches Patchmaster data
        "perc_dp_match" - param is the percent of samples that match Patchmaster to dp_thr decimal places or more
        "test_time" - param is a bool from iclose() (see test_time())
        "test_stim" - param is bool from isclose (see test_reconstructed_stimulus())
        """
        if test_type == "assert_dp_match":
            assert (np.array(param) == 100).all(), "group {0} series {1} does not match Patchmaster to {2} decimal places".format(self.group_num,
                                                                                                                                  self.series_num,
                                                                                                                                  self.printable_dp())
        if self.assert_mode:

            if test_type == "mean_dp_match":
                assert param > 4, "Mean difference from Patchmaster is more than 5 decimal places"

            elif test_type == "perc_dp_match":
                assert param > 99, "Less that 99% of samples are mode that {0} decimal places from Patchmaster".format(self.dp_thr)

            elif test_type == "test_time":
                assert param, "Time does not match Patchmaster to 10 decimal places"

            elif test_type == "test_stim":
                assert param, "Stimulus reconstruction does not match Patchmaster to 7 decimal places"

    def clean_data(self, data, expected_len=None):
        """
        """
        if expected_len:
            if len(data) != expected_len:
                data = self.pad_short_data_with_mean(data, expected_len)

        data = self.conv(data,
                         self.im_or_vm)
        return data

    def clean_time(self, data, expected_len=None):

        if expected_len:
            if len(data) != expected_len:
                data = self.pad_short_time_with_extra_time(data, expected_len)

        return data

    @staticmethod
    def pad_short_time_with_extra_time(data, expected_len):
        """
        HEKA export data is not full, is a sweep is cut short it will be missing the end. However HekaLoad will always
        export full time. So pad heka export data here to match
        """
        new_data = np.full(expected_len, np.nan)
        len_data = len(data)
        len_empty_data = expected_len - len_data

        new_data[0:len_data] = data
        ts = data[1] - data[0]

        pad_data = np.arange(1, len_empty_data + 1) * ts + data[-1]
        new_data[len_data:] = pad_data

        return new_data

    @staticmethod
    def pad_short_data_with_mean(data, expected_len):

        len_short_data = len(data)

        new_data = np.full(expected_len, np.nan)
        new_data[0:len_short_data] = data
        new_data[len_short_data:] = np.mean(data)

        return new_data

    def clean_raw_stim(self, raw_heka_output):
        """
        Raw stim is output from ascii script as a list of np arrays (sweeps)

        For some reason when stim doesn't exist heka export as NaN but LoadHeka will export as holding current
        """
        stim_data = np.array(raw_heka_output)
        if np.isnan(stim_data).all():
            stim_data = np.zeros(np.shape(stim_data))

        conv_stim_data = self.conv(stim_data,
                                   self.load_heka["stim"]["units"])
        return conv_stim_data

    @staticmethod
    def conv(data, units):
        """
        HEKA data is always saved in A or V (this is tested with assert on import). Here we want it in pA or mV
        for both consistency with EE and easier testing.
        """
        if units in ["Im", "A"]:
            factor = 1000000000000
        elif units in ["Vm", "V"]:
            factor = 1000
        elif units == "mV":
            factor = 1

        return data * factor

    @staticmethod
    def all_sweeps_are_same_num_samples(raw_heka_output):
        return len(np.unique([len(sweep) for sweep in raw_heka_output])) == 1

    @staticmethod
    def num_dp(dec, clear_inf=True):
        dp = np.floor(np.abs(np.log10(dec + np.finfo(float).eps)))
        if clear_inf:
            dp = dp[~np.isinf(dp)]
        return dp

    @staticmethod
    def percent_isclose(array1, array2, tolerance):
        isclose_bool = np.isclose(array1, array2, atol=tolerance, rtol=0)
        percent_close = np.count_nonzero(isclose_bool) / len(array1)
        percent_close *= 100
        return percent_close

    def printable_dp(self):
        return abs(int(f'{self.dp_thr:e}'.split('e')[-1]))

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Read Patchmaster Export Sweep ASCII
# ----------------------------------------------------------------------------------------------------------------------------------------------------

def read_heka_test_ascii(full_filepath):
    """
    Read HEKA Export Sweet ASCII data into a dictionary of data.

    It will load a exported series into a dictionary array including data (e.g. Vm), time (e.g. time_Vm) and stimulus (e.g. stim_Vm)
    for Vm and Im. These are saved as list of numpy array (because each sweep num samples is not garenteed to be the same)
    in the relevant dict fields.

    NOTE: this function expects Exported series in the typical format, with 3 lines before the first data line. In some cases, HEKA will
          export with 4 lines. In this case, at present the text file must be manually edited to move / delete this 4th line.

    INPUT: full_filepath - full path to the ascii

    OUTPUT:
        results dictionary with keys: Im, time_Im, stim_Im, Vm, time_Vm, stim_Vm.
    """
    with open(full_filepath) as fh:

        results = make_empty_param_dict()
        sweep = make_empty_param_dict()

        fh.seek(0)
        i = -1
        while True:

            line = fh.readline()
            i += 1

            if "Time" in line:
                cols = line
                continue

            elif "Series" in line:
                continue

            elif line == "\n":
                continue

            elif line == "":
                break

            elif "Sweep" in line:
                if i > 3:  # ignore first 'Sweep' because it comes at the start of the data block

                    update_results_with_sweep(results, sweep)

                    sweep = make_empty_param_dict()
            else:
                if "[A]" in cols.split(",")[1]:
                    save_line_to_sweep_dict(line, sweep, first="Im", second="Vm")

                elif "[V]" in cols.split(",")[1]:
                    save_line_to_sweep_dict(line, sweep, first="Vm", second="Im")
                else:
                    raise Exception("ascii col not recognised")

        update_results_with_sweep(results, sweep)  # get final sweep_idx

        return results

def save_line_to_sweep_dict(line, sweep, first, second):
    """
    The output ascii will have either 3 or 6 columns, depending on whether Im and Vm or just Im or Vm records are present.
    They can be in either order (e.g. first 3 cols Vm)

    Here save the Im and Vm to the approrpiate fields in the dict accounting for whether Im or Vm is first
    """
    split_line = line.strip().split(",")
    line_time_first, line_first, line_stim_first = split_line[0:3]
    sweep["time_" + first].append(float(line_time_first))
    sweep[first].append(float(line_first))
    sweep["stim_" + first].append(float(line_stim_first))

    if len(split_line) > 3:
        line_time_second, line_second, line_stim_second = split_line[3:6]
        sweep["time_" + second].append(float(line_time_second))
        sweep[second].append(float(line_second))
        sweep["stim_" + second].append(float(line_stim_second))
    else:
        sweep["time_" + second].append(np.nan)
        sweep[second].append(np.nan)
        sweep["stim_" + second].append(np.nan)

def update_results_with_sweep(results, sweep):
    for key, value in sweep.items():
        results[key].append(np.array(value))

def make_empty_param_dict():
    dict_ = {}
    for key in ["Im", "time_Im", "Vm", "time_Vm", "stim_Im", "stim_Vm"]:
        dict_[key] = []

    return dict_
