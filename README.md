# Heka Loader for Python

1) Introduction and Acknowledgements
2) Usage Instructions
3) Lazy Loading
4) Supported File Versions and Recording Settings
5) Testing your files

## 1) Introduction and Acknowledgements

This module will load HEKA files created by PatchMaster software into Python. Note this module
is still in the testing phase, please see section 4 and 5 for details. 

Much guidance has been gained from Luke Campagnola's [Heka Reader](https://github.com/campagnola/heka_reader) 
with a few code snippets and functions included with permission. 
Inspiration has also been taken from Christian Keine / Sammy Katta's [MATLAB HEKA loading modules](https://www.mathworks.com/matlabcentral/fileexchange/70164-heka-patchmaster-importer).

We would also like to acknowledge [Stimfits HEKA module](https://github.com/neurodroid/stimfit) and [SigTools module](https://pubmed.ncbi.nlm.nih.gov/19056423/)
on which the above examples were based, and HEKA for their detailed documentation on the filetype, available the network drive: server.hekahome.de

## 2) Usage Instructions

By default, the HEKA loader will load the entire file (i.e. header information + data) into memory.
The argument only_load_header=True can be used for lazy loading (i.e. only loading the header into memory, 
before specifying which series data to load, see section 3).

### Getting Started

To install, clone the github repo. Change directory to the repo and type `pip install .` to install the package.

The HEKA file loader can be used directly or with a context manager:

Directly:
```
from load_heka_python.load_heka import LoadHeka

full_path_to_file = r"C:\path\to\a\file.dat"

heka_file = LoadHeka(full_path_to_file) 
series_data = heka_file.get_series_data("Vm", group_idx=0, series_idx=0)
heka_file.close()
```

Once loaded, the user must remember to close the file with `heka_file.close()`. If not, the file
will be closed when garbage collection occurs, but this is not ideal.

With a context manager:
```
with LoadHeka(full_path_to_file) as heka_file:
	series_data = heka_file.get_series_data("Vm", group_idx=0, series_idx=0)
```
This will ensure the file is closed automatically once the block has finished.

#### File Structure

HEKA files are structured in a 'Tree format'. For example, the 'pulse'
tree contains information on the recorded data. The pulse tree is structured:

Root > Group > Series > Sweep > Record

Which corresponds to the sections on the left hand side of the PatchMaster software when
viewing data. The pulse tree can be accessed with
```
heka_file.pul
```
In LoadHeka, all trees are structured as a dictionary in which each level has the entries
`["hd"]` (header) and `["ch"]` (children). `["hd"]` is a dictionary containng the header information
for that level of the tree. The `["ch"]` is a list of children, each with same structure.

The exception to this rule is the Record level, which has the fields `["hd"]` and `["data"]`.
`["data"]` is where raw data will be stored when loaded into memory.

e.g. to load a heka file and access the header for the first record, first sweep, first series, first group
```
heka_file = LoadHeka(full_path_to_file)
heka_file.pul["ch"][0]["ch"][0]["ch"][0]["ch"][0]["hd"] 
heka_file.close()
```
or the data
```
heka_file.pul["ch"][0]["ch"][0]["ch"][0]["ch"][0]["data"]
```
Other trees can be accessed in a similar way

#### Convenience Functions for Loading Data

In HEKA files, a Series is a recording from a group that shares the same stimulus protocol, recording mode etc. This is 
analogous to a file of a single recording in other software. As such, this is the level that makes most sense to
load into a contigious block.

Convenience functions are provided to return Series data as well as key information on the recording,
and the stimulation protocol if requested (reconstructed from the StimTree).

Public Functions:
```
heka_file.print_group_names()
heka_file.print_series_names(group_idx)
heka_file.get_series_data(Im_or_Vm="Im" or "Vm", group_idx=int, series_idx=int, include_stim_protocol=bool)
```
First, to get the indexes of the group and series you want to load, you can use:
```
heka_file.print_group_names()
```
or
```
heka_file.print_series_names(group_idx)
```
This will print out the names of the group / series as they appear in PatchMaster, as well as their index.

Next, we can load a series using its index (zero indexed). For example, to load the Vm channel of the third group, 
second series, we can use:
```
series = heka_file.get_series_data("Vm", group_idx=2, series_idx=1, include_stim_protocol=True, fill_with_mean=False)
```
This will return the dictionary data with series:

`series["data"]` - a num sweeps x num samples numpy array containing the data. Note that in HEKA it is possible for 
                   differrent sweeps in the same series to have a different number of samples. In this instance, the end
				   of the shorter sweeps will be padded with Nan by default, or the average of the existing sweep if
				   fill_with_mean=True.

`series["time"]` - a num_sweeps x num_samples matrix of the record timings.

`series["stim"]` - if requested, a num_sweeps x num_samples matrix of the stimulus protocol 
				   reconstructed from the StimTree (note not all protocols currently supported, see section 4).

as well as number of fields `("labels", "ts", "data_kinds", "num_samples", "t_starts", "t_stops")` containing information for each sweep.  


In theory, these are the only methods you will need to use, however the class has many private methods that might be useful (see source code).


## 3) Lazy Loading

By default, the entire file is loaded into memory (i.e. the `["data"]` field of the pulse records
are all filled). 

However, as HEKA files can be very large (e.g. ~200 MB) options are provided
for 'lazy' loading. This will only load the header infromation and no data. To load the data, the function `get_series_data()` is used.

If the series is loaded with `get_series_data()`, then this selected series only
will be loaded into memory (i.e. the `["data"]` fields on the pulse tree, on the selected records only, will be filled)
before the data is returned.


## 4) Supported File Versions and Recording Settings

HEKA has been in business for over 40 years and as such has many file versions. Furthermore,
it is a highly flexible filetype with many many options and parameter combinations.

The approach taken here is to only allow the module to run for versions and recording options that
have been tested. Testing refers to saving data from HEKA patchmaster using 'Export' / 'Export Full Sweep' 
button and comparing the output of LoadHeka to this (see test_load_heka). As more versions and files are submitted for testing, 
these will be added to the test suite and supported.

When using this module for the first time, please check that your data appears as it does in the PatchMaster file. 
Also, please send your files to support@easyelectrophysiology.com so they can be added to our test suite. Please open an Issue in case of any problems.

Known settings currently not tested / supported:
- big endian encoding
- data stored as int32 and float64
- interleaved data
- leak and virtual data
- units not in s, A, V
- currently only Constant (positive), Ramp (positive) and Continous stimulus protocol reconstruction is supported
- sweeps with more than two records are not supported

However, there may be other setting combinations that have not been anticipated. So far, all tested files match the HEKA
data output well (see `./test/test_load_heka.py` for details). Again, please send your files to support@easyelectrophysiology.com so they can be added 
during the testing phase so they can be added to the test suite to check for any unexpected recording settings.

### HEKA Version Details:

Unsupported: pre version v2x00. These are DAT1 (unbundled filetypes). These can be converted to Bundled files in Patchmaster.

Unsupported / Untested: v2x00-v2x05, v2x10-v2x15, v2x20, v2x30-v2x35, v2x40-v2x43, v2x52-v2x53, v2x60-v2x60, v2x71-v2x73, v2x80.

Supported and test:
```
v9:
	v2x90.2
	v2x90.3

v1000
	v2x90.4 
	v2x90.5 
	v2x91
        v2x92
	v1.2  
```
## 5) Testing Your Files

Options are provided to test the data read by LoadHeka against the data as displayed in Patchmaster. This is reccomended during the ongoing testing phase.

To test your file, Series to test must be exported from Patchmaster as an ASCII file. You must keep these ASCII exported series
in a folder with the same name as your HEKA filename, without .dat. The name of the ascii files must conform
to the standard file_name_group-X_series-X.asc (see below).
```
e.g. if your filename is test_file.dat

./.../test_file/test_file.dat
				test_file_group-1_series-1.asc
				test_file_group-1_series-2.asc ...
```
Notes on exporting from HEKA:

1) Go to 'Tweak' > 'Export' and make sure 'text' output is selected and 'stimulus' box is checked. 
2) Make sure Display filter is off.
3) Ensure data is displayed with 'Subtract Zero Offset' on.
4) Export 1 series at a time.
5) In general select 'Data' > 'Export Full Sweep' to ignore the way the trace is dispayed on the graph (i.e. if it is zoomed in).
6) For very long stimuli, the entire record is not exported by default. To export the full record, go to:
    oscl button > Manual X-range > set the X range to the full record time
    use 'Export' (NOT 'Export Full Sweep' which for some reason does not work in this case)

To run tests, see run_test_load_heka.py
