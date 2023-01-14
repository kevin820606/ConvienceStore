import httpx
import json
from utils import City, CityTown, save_json


familymart_url = "https://www.family.com.tw/Marketing/storemap/"


def _get_town(client: httpx.Client, city: City) -> list[str]:
    query_url = f"https://api.map.com.tw/net/familyShop.aspx?searchType=ShowTownList&type=&city={city.name}&fun=storeTownList&key=6F30E8BF706D653965BDE302661D1241F8BE9EBC"
    towns_json = json.loads(client.get(url=query_url).text[:-1].replace("storeTownList(", ""))
    towns = [town["town"] for town in towns_json]
    return towns


def _process_store_data(
    city: str, town: str, preprocess: dict | list | None
) -> list[dict]:
    if preprocess is None:
        return []
    if isinstance(preprocess, dict):
        return [{"City": city, "Town": town} | preprocess]
    return [{"City": city, "Town": town} | info for info in preprocess]


def _get_town_stores(client: httpx.Client, city_town: CityTown) -> list[dict]:
    stores_info = []
    for town in city_town.towns:
        query_url = f"https://api.map.com.tw/net/familyShop.aspx?searchType=ShopList&type=&city={city_town.city}&area={town}&road=&fun=showStoreList&key=6F30E8BF706D653965BDE302661D1241F8BE9EBC"
        stores_xml: list[dict] | dict = json.loads(client.get(url=query_url).text[:-1].replace("showStoreList(", ""))
        stores_info.extend(
            _process_store_data(city=city_town.city, town=town, preprocess=stores_xml)
        )
    return stores_info


def get_towns() -> list[CityTown]:
    citytowns: list[CityTown] = []
    with httpx.Client(headers=httpx.Headers({"referer":"https://www.family.com.tw/"})) as client:
        for city in City:
            towns = _get_town(client=client, city=city)
            citytowns.append(CityTown(city=city.name, towns=towns))
    return citytowns


def get_all_stores(city_towns: list[CityTown]) -> list[dict]:
    all_stores = []
    with httpx.Client(headers=httpx.Headers({"referer":"https://www.family.com.tw/"})) as client:
        for city_town in city_towns:
            stores = _get_town_stores(client=client, city_town=city_town)
            all_stores.extend(stores)
    return all_stores

def main() -> None:
    citytowns = get_towns()
    stores = get_all_stores(city_towns=citytowns)
    print(len(stores))
    save_json(stores, file_name="familymart.json")

if __name__ == "__main__":
    main()
