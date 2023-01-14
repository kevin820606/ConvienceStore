import json
from enum import Enum
from typing import NamedTuple
class City(Enum):
    台北市 = "01"
    基隆市 = "02"
    新北市 = "03"
    桃園市 = "04"
    新竹市 = "05"
    新竹縣 = "06"
    苗栗縣 = "07"
    台中市 = "08"
    台中縣 = "09"
    彰化縣 = "10"
    南投縣 = "11"
    雲林縣 = "12"
    嘉義市 = "13"
    嘉義縣 = "14"
    台南市 = "15"
    台南縣 = "16"
    高雄市 = "17"
    高雄縣 = "18"
    屏東縣 = "19"
    宜蘭縣 = "20"
    花蓮縣 = "21"
    台東縣 = "22"
    澎湖縣 = "23"
    金門縣 = "25"
    連江縣 = "24"

class CityTown(NamedTuple):
    city: str
    towns: list[str]
def save_json(stores:dict, file_name:str):
    with open(f"data/{file_name}", mode="w", encoding="utf-8") as stores_json:
        json.dump(obj=stores, fp=stores_json, ensure_ascii=False, indent=4)
