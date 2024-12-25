#!/bin/bash

. ./env.sh

# get channel id
# https://api.telegram.org/bot<YourBOTToken>/getUpdates

# crontab
#  */5 * * * bash /path/gas_alert.sh 2>&1 | logger -t gas_alert
#bot user: BSEGPBot

#curl -v "https://api.telegram.org/bot$TELEGRAM_TOKEN/getUpdates"

gweiprice()
{
msg=$(echo $rate $1 $price | awk '{printf "Price%%20of%%20%d%%20gas%%20€%.2f\n", $2, $1*$2*$3/10^9}')
echo "$msg"
}

url="https://api.etherscan.io/api?module=gastracker&action=gasoracle"

cheapPrice=40
price=$(curl $url | jq '.result.SafeGasPrice | tonumber' )

iprice=$(echo $price | awk '{printf "%d", $1}')
if [ -n "$iprice" -a "$iprice" -lt $cheapPrice ]
then
omsg="Ether%20gas%20price:%20${price}%20gwei"


rate=$( curl --request GET \
	--url 'https://investing-cryptocurrency-markets.p.rapidapi.com/currencies/get-rate?fromCurrency=195&toCurrency=17&lang_ID=1&time_utc_offset=28800' \
	--header 'x-rapidapi-host: investing-cryptocurrency-markets.p.rapidapi.com' \
	--header 'x-rapidapi-key: '$RAPIDAPI_KEY| jq '.data[0][0].basic|tonumber')
echo "Ether price € $rate"

omsg="$omsg%0A"`gweiprice 21000`
omsg="$omsg%0A"`gweiprice 500000`

curl -v "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage?chat_id=$TELEGRAM_CHANNEL_ID&text=$omsg"
fi
