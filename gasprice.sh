#!/bin/bash

crtbl()
{
sqlite3 << INPUT
.open currencies.db
drop table if exists gasprices; 
create table gasprices (price float, time timestamp default current_timestamp);
INPUT
}

regprice()
{
sqlite3 << INPUT
.open currencies.db
insert into gasprices (price) values($1);
INPUT
}


url="https://api.etherscan.io/api?module=gastracker&action=gasoracle"

gasprice()
{
curl $url | jq '.result.SafeGasPrice | tonumber'
}

fastgasprice()
{
curl $url | jq '.result.FastGasPrice | tonumber'
}

#crtbl
while true
do
	price=`gasprice`
	echo "Ether gas price: $price"
	regprice $price
	sleep 10
done
