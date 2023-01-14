import httpx
from utils import City, CityTown, save_json
from bs4 import BeautifulSoup, element

hilife_url = "https://www.hilife.com.tw/storeInquiry_street.aspx"


def get_validation(client: httpx.Client) -> dict:
    response = client.get(url=hilife_url).text
    soup = BeautifulSoup(response, features="html.parser")
    soup.select("input#__VIEWSTATE")[0].get("value")
    return {
        "__VIEWSTATE": soup.select("input#__VIEWSTATE")[0].get("value"),
        "__EVENTVALIDATION": soup.select("input#__EVENTVALIDATION")[0].get("value"),
    }


def _get_town(client: httpx.Client, city: City, validation: dict) -> list[str]:
    data = {"CITY": city.name, "AREA": "信義區"} | validation
    raw_towns = client.post(url=hilife_url, data=data).text
    towns_html = BeautifulSoup(raw_towns, features="html.parser").select(
        "select[id='AREA'] > option"
    )
    towns = [town.text for town in towns_html]
    return towns


def _process_store_data(
    city: str, town: str, preprocess: list[element.Tag]
) -> list[dict]:
    stores_list = []
    for store in preprocess:
        stores_list.append(
            {
                "City": city,
                "Town": town,
                "store_id": store.select("th")[0].text,
                "store_name": store.select("th")[1].text,
                "store_address": store.select("a")[0].text,
            }
        )
    return stores_list


def _get_town_stores(
    client: httpx.Client, city_town: CityTown, validation: dict
) -> list[dict]:
    stores_info = []
    for town in city_town.towns:
        data = {"CITY": city_town.city, "AREA": town} | validation
        raw_stores = client.post(url=hilife_url, data=data).text
        stores_html = BeautifulSoup(raw_stores, features="html.parser").select(
            "div[class='searchResults'] > table > tr"
        )
        stores_info.extend(
            _process_store_data(city=city_town.city, town=town, preprocess=stores_html)
        )
    return stores_info


def get_towns(client:httpx.Client, validation: dict) -> list[CityTown]:
    citytowns: list[CityTown] = []
    for city in City:
        towns = _get_town(client=client, city=city, validation=validation)
        citytowns.append(CityTown(city=city.name, towns=towns))
    return citytowns


def get_all_stores(client:httpx.Client, city_towns: list[CityTown], validation: dict) -> list[dict]:
    all_stores = []
    for city_town in city_towns:
        stores = _get_town_stores(client=client, city_town=city_town, validation=validation)
        all_stores.extend(stores)
    return all_stores


def main() -> None:
    with httpx.Client() as client:
        validation = get_validation(client=client)
        citytowns = get_towns(client = client, validation=validation)
        stores = get_all_stores(client = client, city_towns=citytowns, validation=validation)
    print(len(stores))
    save_json(stores, file_name="hilife.json")


if __name__ == "__main__":
    main()
