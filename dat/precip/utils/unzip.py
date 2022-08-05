import zipfile
with zipfile.ZipFile("../download.zip", "r") as zip_ref:
    zip_ref.extractall("../data")

with zipfile.ZipFile("../1km/觀測_日資料_東部_降雨量.zip", "r") as zip_ref:
    zip_ref.extractall("../east/")

with zipfile.ZipFile("../1km/觀測_日資料_中部_降雨量.zip", "r") as zip_ref:
    zip_ref.extractall("../west/")

with zipfile.ZipFile("../1km/觀測_日資料_南部_降雨量.zip", "r") as zip_ref:
    zip_ref.extractall("../south/")

with zipfile.ZipFile("../1km/觀測_日資料_北部_降雨量.zip", "r") as zip_ref:
    zip_ref.extractall("../north/")

