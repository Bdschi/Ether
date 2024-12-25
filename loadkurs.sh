#Date,Open,High,Low,Close,Adj Close,Volume
crtbl()
{
sqlite3 << INPUT
.open currencies.db
drop table if exists rates; 
create table rates (fcur varchar(30), tcur varchar(30), date date, open float, high float, low float, close float, adjclose float, volume int, time timestamp default current_timestamp);
INPUT
}

loadtbl()
{
sqlite3 << INPUT
.open currencies.db
.mode csv
.import eur.csv rates
INPUT
}

showtbl()
{
sqlite3 << INPUT
.open currencies.db
select * from rates;
INPUT
}

sqltohori()
{
awk -F\| '{
	c[$1]=1
	r[$2]=1
	x[$1,$2]=$3
}
END {
	n=asorti(r, rs)
	printf "%10s", ""
	for(col in c) {
		printf "%5s", col
	}
	printf "\n"
	for(i=1;i<=n;i++) {
		row=rs[i]
	#for(row in r) {
		printf "%10s", row
		for(col in c) {
			printf "%5s", x[col, row]
		}
		printf "\n"
	}

}'
}

showtblhorizontal()
{
sqlite3  << INPUT | sqltohori
.open currencies.db
select tcur, date, count(*)
from rates
where date>'2023-05-01'
group by tcur, date;
INPUT
}

del20220925()
{
sqlite3  -line<< INPUT
.open currencies.db
delete from rates
where date>'2022-09-24';
INPUT
}

showtblhorizontal
exit

#showtbl
showtbl
#crtbl
#exit

period1=`date +"%s" -d2022-05-06`
period2=`date +"%s" -d2022-05-06`
#this loads data for one day: 2022-05-05
#possible reason: 6th 00 CET is 5th UTC

period1=`date +"%s" -d2024-09-01`
period2=`date +"%s" -d2024-09-10`
rm eur.csv
for cur in 'ETH' 'BTC' 'BCH' 'BTG' 'BSV' 'LTC' 'XRP' 'DOGE'
do
	echo $cur
	curl -o x.csv -L "https://query1.finance.yahoo.com/v7/finance/download/$cur-EUR?period1=$period1&period2=$period2&interval=1d&events=history&includeAdjustedClose=true"
	wc -l < x.csv
	time=`date +"%y-%m-%d %H:%M:%S"`
	tail -n +2 x.csv |sed "s/^/EUR,$cur,/;s/$/,$time/" >> eur.csv
	#no newline in last line
	printf "\n" >> eur.csv
done
loadtbl
