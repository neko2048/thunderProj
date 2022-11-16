import zipfile
#with zipfile.ZipFile("../CC/download_2022-08-09_16-15-17.zip", "r") as zip_ref:
#    zip_ref.extractall("../CC/")

with zipfile.ZipFile("../download_2022-11-07_14-46-28.zip", "r") as zip_ref:
    zip_ref.extractall("../CFSR-WRF-mid21/")

#with zipfile.ZipFile("../W500/download_2022-08-09_16-49-50.zip", "r") as zip_ref:
#    zip_ref.extractall("../W500/")
