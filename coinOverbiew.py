import requests
import os

apikey=os.getenv('RAPIDAPI_KEY')

url = "https://investing-cryptocurrency-markets.p.rapidapi.com/coins/get-overview"

headers = {
    'x-rapidapi-host': "investing-cryptocurrency-markets.p.rapidapi.com",
    'x-rapidapi-key': apikey
    }

for pairId in ['1010776', '1001803','997650', '49800']:
    querystring = {"pair_ID":pairId,"time_utc_offset":"28800","lang_ID":"1"}
    response = requests.request("GET", url, headers=headers, params=querystring)

    attributes=response.json()['data'][0]['screen_data']['pairs_attr'][0]
    print("Name: "+attributes['pair_name_base'])
    print("Exchange: "+attributes['exchange_name'])
    overview=response.json()['data'][0]['screen_data']['pairs_data'][0]['overview_table']
    for lin in overview:
        print(lin['key']+': '+lin['val'])
    print()
