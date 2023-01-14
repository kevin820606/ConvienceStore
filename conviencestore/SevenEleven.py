import httpx
import xmltodict

from utils import City, CityTown, save_json

seven_eleven_url = "https://emap.pcsc.com.tw/EMapSDK.aspx"


def _get_town(client: httpx.Client, city: City) -> list[str]:
    towns_xml = xmltodict.parse(
        client.post(
            url=seven_eleven_url, data={"commandid": "GetTown", "cityid": city.value}
        ).text
    )
    towns_dict: list[dict] = towns_xml["iMapSDKOutput"].get("GeoPosition", [])
    towns = [town["TownName"] for town in towns_dict]
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
        data = {"commandid": "SearchStore", "city": city_town.city, "town": town}
        stores_xml: list[dict] | dict = xmltodict.parse(
            client.post(url=seven_eleven_url, data=data).text
        )["iMapSDKOutput"].get("GeoPosition")
        stores_info.extend(
            _process_store_data(city=city_town.city, town=town, preprocess=stores_xml)
        )
    return stores_info


def get_towns() -> list[CityTown]:
    citytowns: list[CityTown] = []
    with httpx.Client() as client:
        for city in City:
            towns = _get_town(client=client, city=city)
            citytowns.append(CityTown(city=city.name, towns=towns))
    return citytowns


def get_all_stores(city_towns: list[CityTown]) -> list[dict]:
    all_stores = []
    with httpx.Client() as client:
        for city_town in city_towns:
            stores = _get_town_stores(client=client, city_town=city_town)
            all_stores.extend(stores)
    return all_stores

def main() -> None:
    citytowns = get_towns()
    stores = get_all_stores(city_towns=citytowns)
    save_json(stores=stores, file_name="7-11.json")

if __name__ == "__main__":
    main()
