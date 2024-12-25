. ./env.sh
curl --request GET \
	--url 'https://yh-finance.p.rapidapi.com/auto-complete?q=eth&region=DE' \
	--header 'x-rapidapi-host: yh-finance.p.rapidapi.com' \
	--header 'x-rapidapi-key: '$RAPIDAPI_KEY | python -mjson.tool|more
