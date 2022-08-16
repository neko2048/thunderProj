import zipfile
#with zipfile.ZipFile("../CC/download_2022-08-09_16-15-17.zip", "r") as zip_ref:
#    zip_ref.extractall("../CC/")

with zipfile.ZipFile("../CFSR-WRF-new/download_2022-08-11_20-14-46.zip", "r") as zip_ref:
    zip_ref.extractall("../W_max/")

#with zipfile.ZipFile("../W500/download_2022-08-09_16-49-50.zip", "r") as zip_ref:
#    zip_ref.extractall("../W500/")
