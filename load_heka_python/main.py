from load_heka_python import load_heka

file_path = r"C:\Users\User\Downloads\20230926.dat"

data = load_heka.LoadHeka(file_path, only_load_header=False)

breakpoint()