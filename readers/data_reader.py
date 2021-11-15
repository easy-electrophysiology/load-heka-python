import numpy as np
import struct

def fill_pul_with_data(pul, fh, group_idx, series_idx):
    """
    Fill the ["data"] field of all pulse tree records for the specified group and series with raw data from file.

    The record header contains the starting bit of the raw data, and parameters for its reconstruction.
    """
    series = pul["ch"][group_idx]["ch"][series_idx]

    for sweep in series["ch"]:
        for rec in sweep["ch"]:

            start = rec["hd"]["TrData"]
            length = rec["hd"]["TrDataPoints"]
            data_kind = rec["hd"]["TrDataKind"]

            endian = "<" if data_kind["IsLittleEndian"] else ">"

            fmt, size, np_dtype = get_dataformat(rec["hd"]["TrDataFormat"])

            fh.seek(start)
            data = struct.unpack(endian + fmt * length,
                                 fh.read(size * length))
            data = np.array(data, dtype=np_dtype)

            # Scale and recast to float64
            if np_dtype in [np.int16, np.int32]:
                scaling_factor = np.array(rec["hd"]["TrDataScaler"], dtype=np.float64)
                data = (data * scaling_factor) - rec["hd"]["TrZeroData"]

            elif np_dtype == np.float32:
                data = data.astype(np.float64)

            rec["data"] = data

            run_checks(rec, data, data_kind)

def run_checks(rec, data, data_kind):
    """
    """
    assert data_kind["IsLittleEndian"], "big endian data not tested"
    assert not data_kind["IsLeak"], "isLeak channels not tested"
    assert not data_kind["IsVirtual"], "isVirtual channels not tested"

    # Checks Interleave - Not Tested Yet
    interleave_size = rec["hd"]["TrInterleaveSize"]
    interleave_skip1 = rec["hd"]["TrInterleaveSkip"]
    interleave_skip2 = rec["hd"]["TrInterleaveSkip"]
    assert interleave_size == 0, "Interleave not tested"

    # Ensure assumptions are all true for the forseeable future, test these when counter examples come up
    assert rec["hd"]["TrDataPoints"] == len(data)
    assert rec["hd"]["TrYOffset"] == 0.0
    assert rec["hd"]["TrGLeak"] == 0.0
    assert rec["hd"]["TrXUnit"] == "s"
    assert rec["hd"]["TrYUnit"] in ["A", "V"]

def get_dataformat(idx):

    if idx == 0:
        return "h", 2, np.int16

    elif idx == 1:
        raise Exception("int32 datatype not tested ")
        return "i", 4, np.int32

    elif idx == 2:
        return "f", 4, np.float32

    elif idx == 3:
        raise Exception("double datatype not tested")
        return "d", 8, np.float64

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Check Parameters are the Same Across All Sweeps in a Series
# ----------------------------------------------------------------------------------------------------------------------------------------------------

def check_sweep_params_are_equal_for_every_series_in_file(pul):
    """
    Check that parameters assumed to be the same across a series (within within or between Im and Vm records) are so
    for all series.
    """
    for group_idx, group in enumerate(pul["ch"]):
        for series_idx, series in enumerate(group["ch"]):

            recs_in_sweeps = np.unique([len(sweep["ch"]) for sweep in series["ch"]])
            assert len(recs_in_sweeps) == 1, "number of recs is not equal for al sweeps in group: {0}, series: {1}".format(group_idx,
                                                                                                                           series_idx)
            for param_key in ["TrDataScaler", "TrYUnit", "TrDataFormat", "TrAdcChannel", "TrRecordingMode"]:
                for rec_idx in range(recs_in_sweeps[0]):
                    check_sweep_params_are_equal(pul, group_idx, series_idx, rec_idx, param_key)

            for param_key in ["TrXUnit", "TrXInterval", "TrCellPotential"]:
                check_sweep_params_are_equal(pul, group_idx, series_idx, "all", param_key)

def check_sweep_params_are_equal(pul, group_idx, series_idx, rec_idx, param_key):
    """
    Determine whether all records for all sweeps in a series have the same parameters. For some these are expected to be
    different across records (i.e. TrDataScaler between Im and Vm traces). In this case pass the index of the record to
    check.

    In other cases these would be expected to be the same TODO: add sampling frequency. In this case compar both Im and Vm records.
    """
    series = pul["ch"][group_idx]["ch"][series_idx]
    params = []
    for sweep in series["ch"]:

        if rec_idx != "all":
            params.append(sweep["ch"][rec_idx]["hd"][param_key])
        else:
            for rec in sweep["ch"]:
                params.append(rec["hd"][param_key])

    all_equal = True if np.unique(params).size == 1 else False

    assert all_equal, "Group: {0}, Series: {1} {2} parameters are not the same for all sweeps, records: {3}".format(group_idx,
                                                                                                                    series_idx,
                                                                                                                    param_key,
                                                                                                                    rec_idx)
