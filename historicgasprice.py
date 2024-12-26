from elasticsearch import Elasticsearch
from datetime import datetime
import os

os.system('. ./env.sh') # Load the Environment Variables
es_api_key=os.getenv('ES_API_KEY')

# network Parameter for the different Networks:
def initialize_elastic(network):
    es = Elasticsearch(hosts=[network],
                   http_auth=('kadmus@nexgo.de',
                              es_api_key),
                               request_timeout=1800)
    return es

# Create a List with the Networks we use for this analysis:
networks = ['https://api.anyblock.tools/ethereum/ethereum/mainnet/es/',
            'https://api.anyblock.tools/poa/xdai/es/',
            'https://api.anyblock.tools/ewf/ewc/es/',
            'https://api.anyblock.tools/ethereum/classic/mainnet/es'
            ]

# define a function to get all data for the Period of 1 Min
# for the last Day. We get the average GasPrice per Min
# and the 30,60,90,10 Percentile GasPrice per Min

def fetch_gas_min(fromdt, todt, network):
    es = initialize_elastic(network)
    return es.search(index='tx', doc_type='tx', body = {
        "_source":["timestamp","gasPrice.num"],
        "query": {
        "bool": {
            "must": [{
                    
                "range":{
                    "timestamp": {
                        "gte": fromdt,
                        "lt":  todt
                    }
                }}
                
            ]
        }
        },
        "aggs": {
        "minute_bucket": {
            "date_histogram": {
                "field": "timestamp",
                "interval": "1m",
                "format": "yyyy-MM-dd HH:mm"
            },
            "aggs": {
                "percentilesMin": {
                    "percentiles": {
                    "field": "gasPrice.num",
                    "percents": [35,60,90,100]
                }},
                "avgGasMin": {
                    "avg": {
                        "field": "gasPrice.num"
                    }
                }}}
    }
    })

#dt=int(datetime(2022, 1, 1).timestamp())
dt=int(datetime(2022, 2, 21, 15, 57).timestamp())
enddt=int(datetime.now().timestamp())
while dt < enddt:
    eth_min = fetch_gas_min(dt, dt+24*3600, networks[0])
    dt = dt+24*3600
    #print(eth_min['aggregations'])
    for b in eth_min['aggregations']['minute_bucket']['buckets']: 
        if b['doc_count'] > 0:
            print("%s,%f,%f,%f,%f,%f"  % (\
                b['key_as_string'],
                b['percentilesMin']['values']['35.0']/1E9,
                b['percentilesMin']['values']['60.0']/1E9,
                b['percentilesMin']['values']['90.0']/1E9,
                b['percentilesMin']['values']['100.0']/1E9,
                b['avgGasMin']['value']/1E9))
