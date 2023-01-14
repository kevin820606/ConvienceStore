import httpx
import re
from utils import City, save_json
from bs4 import BeautifulSoup
re.match
def _get_district_name(city:str, addr:str) -> str:
    addr = addr.replace(city, "")
    return re.match(".*[鄉鎮市區]", addr[:4])[0]

def _get_city_stores(client: httpx.Client, city: City) -> list[dict]:
    query_url = f"http://www.okmart.com.tw/convenient_shopSearch_Result.aspx?city={city.name}"
    raw_stores = BeautifulSoup(client.get(url = query_url).text, features="html.parser")
    stores_names = [{
        "City":city.name,
        "Town":_get_district_name(city = city.name, addr = address.text.strip()),
        "Name":name.text.strip(),
        "Address":address.text.strip()} for name, address in zip(
            raw_stores.find_all("h2"), raw_stores.find_all("span"))]
    return stores_names

def get_all_stores() -> list[dict]:
    all_stores = []
    with httpx.Client(headers=httpx.Headers({"referer":"https://www.family.com.tw/"})) as client:
        for city in City:
            stores = _get_city_stores(client=client, city=city)
            all_stores.extend(stores)
    return all_stores

def main() -> None:
    stores = get_all_stores()
    print(len(stores))
    save_json(stores, file_name="okmart.json")

if __name__ == "__main__":
    main()
