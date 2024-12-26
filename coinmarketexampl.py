#https://pro.coinmarketcap.com/api/v1#section/Quick-Start-Guide
#This example uses Python 2.7 and the python-request library.
#Be sure to replace the API Key in sample code with your own and use API domain pro-api.coinmarketcap.com or use the test API Key b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c for sandbox-api.coinmarketcap.com testing with our sandbox environment. Please note that our sandbox api has mock data and should not be used in your application.

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

. env.sh
url = 'https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
  'start':'1',
  'limit':'5000',
  'convert':'EUR'
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': 'b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c',
}

session = Session()
session.headers.update(headers)

try:
  response = session.get(url, params=parameters)
  data = json.loads(response.text)
  #print(data)
  print(response.text)
except (ConnectionError, Timeout, TooManyRedirects) as e:
  print(e)
