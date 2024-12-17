import requests
import math
from scrapy import Selector
import json
import time

startTime = time.time() 
# Getting all the stores details
url = "https://storelocator.unes.it/wp-admin/admin-ajax.php?action=get_all_store"
stores = requests.get(url).json()

data = []
for store in stores:
    storeId = store["id"]
    storeUrl = f"https://storelocator.unes.it/wp-admin/admin-ajax.php?action=get_store&id_store={storeId}"
    storeDetails = requests.get(storeUrl).json()
    for key, value in store.items():
        if key not in storeDetails:
            storeDetails[key] = value
    data.append(storeDetails)

with open("unes_stores.json", "w") as file:
    json.dump(data, file, indent=4) 

# Getting the products details
url = "https://www.spesaonline.unes.it/"
response = requests.get(url)

selector = Selector(text=response.text)
urls = selector.xpath("//label[@class='body2--mobile body3--desktop header__content__subelement--label']/a/@href").getall()
categoryIds = []
for url in urls:
    _id = url.split("/")[-1]
    if _id.isnumeric():
        categoryIds.append(_id)

url = "https://d3gokg1ssu-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.24.0)%3B%20Browser%20(lite)%3B%20instantsearch.js%20(4.36.0)%3B%20JS%20Helper%20(3.22.5)&x-algolia-api-key=3d6a1904772a0bc84e423239b8e2672b&x-algolia-application-id=D3GOKG1SSU"

payload = '''{"requests":[{"indexName":"production_0064-index","params":"clickAnalytics=true&facets=%5B%22brand%22%2C%22categoryNames_it%22%2C%22diets%22%2C%22newsPromo%22%2C%22tags%22%5D&filters=categories%3A{}&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=1000&maxValuesPerFacet=100&page=0&userToken=anonymous-53756464-f1c7-45e0-85a3-7d2536feab6c"}]}'''

headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "connection": "keep-alive",
    "content-type": "application/x-www-form-urlencoded",
    "host": "d3gokg1ssu-dsn.algolia.net",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

products = []
for categoryId in categoryIds:
    categoryPayload = payload.replace("categories%3A{}", f"categories%3A{categoryId}")
    data = requests.post(url, data=categoryPayload, headers=headers).json()
    products.extend(data["results"][0]["hits"])
    nprods = data["results"][0]["nbHits"]
    if nprods > 1000:
        npages = math.ceil(nprods / 1000)
        for page in range(1, npages):
            categoryPayload = payload.replace("categories%3A{}", f"categories%3A{categoryId}").replace("&page=0", f"&page={page}")
            data = requests.post(url, data=categoryPayload, headers=headers).json()
            products.extend(data["results"][0]["hits"])

with open("unes_products.json", "w") as file:
    json.dump(products, file, indent=4) 

# Getting the stores details under specific zip code
zipCode = "20121"
latitude = "45.4720482"
longitude = "9.1920381"
url = f"https://www.spesaonline.unes.it/onboarding/services?cap={zipCode}&latitude={latitude}&longitude={longitude}"
headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en,en-US;q=0.9,ar;q=0.8",
    "connection": "keep-alive",
    "content-type": "application/json",
    "host": "www.spesaonline.unes.it",
    "referer": "https://www.spesaonline.unes.it/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

data = requests.get(url, headers=headers).json()
stores = data["services"][0]["stores"]
with open(f"{zipCode}_stores.json", "w") as file:
    json.dump(stores, file, indent=4)

elapsedTime = round(((time.time() - startTime) / 60), 2)
print(f"Scraping Time: {elapsedTime} mins")