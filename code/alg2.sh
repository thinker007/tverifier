#!/bin/bash

#FILE="alterunits2.txt"
FILE="alterunits.txt"

#$1=serial
#$2=topic unit
#$3=alternate unit 1
#$4=alternate unit 2
#$5=alternate unit 3
#$6=alternate unit 4
#$7=alternate unit 5

mkdir -p sentences
mkdir -p output_alg2

rm sentences/*
rm output_alg2/*

python process_sentences.py $FILE

#cat $FILE | awk -F"\t" 'BEGIN{OFS="\t"} {print file=$1,$2,$3,$4,$5,$6,$7 > "sentences/NR"}'

#read each sentences from each file
for file in `ls sentences`; do
	#read tu au1 au2 <<<$(awk -F"\t" 'BEGIN{OFS="\t"} {print $2,$3,$4}' sentences/$file)
	#echo $tu"*"$au1"*"$au2 
	
	#save topic unit and five alternate untis
	awk -F"\t" 'BEGIN{OFS="\t"} {print $2 > "/tmp/tu" 
								 print $3 > "/tmp/au1" 
								 print $4 > "/tmp/au2"
								 print $5 > "/tmp/au3"
								 print $6 > "/tmp/au4"
								 print $7 > "/tmp/au5"
							  }' sentences/$file
							  
	
	#use urldigger to find most relavant wikipedia url	
	#[TODO: need to use only wiki search if any wiki url is not fount at first]	
	tu=`cat /tmp/tu`
	python urldigger-02c/urldigger.py -g "site:en.wikipedia.org $tu" > /tmp/urls
	#cat /tmp/urls		
	
	wiki_url=`cat /tmp/urls | grep -i "en.wikipedia.org" | head -1`
	echo $wiki_url
	
	#get wikipedia page and save
	wget $wiki_url -O /tmp/webpage.html -o /tmp/log
	
	#convert from html to text and arrange sentences in lines
	cat /tmp/webpage.html | html2text -nobs | tr "." "\n" | tr "_" " " > /tmp/webpage.txt
	
	for au in au1 au2 au3 au4 au5; do
		cat /tmp/webpage.txt | grep -i "`cat /tmp/$au`" > /tmp/match_$au
	done
	
	#remove stopwords from the tu
	#\b(boundary) replaces whole word only rather than within word also
	cat /tmp/tu | sed 's/[[:<:]]is[[:>:]]//g; s/[[:<:]]was[[:>:]]//g; s/[[:<:]]the[[:>:]]//g; s/[[:<:]]in[[:>:]]//g; s/[[:<:]]not[[:>:]]//g; s/[[:<:]]be[[:>:]]//g; s/[[:<:]]of[[:>:]]//g; s/[[:<:]]on[[:>:]]//g; s/[[:<:]]a[[:>:]]//g;' > /tmp/tu_stop_removed 
	
	#match content words from tu in the sentences obtained after matching tu
	content_words=`cat /tmp/tu_stop_removed` 
	
	rm /tmp/output
	for au in au1 au2 au3 au4 au5; do
		count=0
		for word in $content_words; do
			match=`cat /tmp/match_$au | grep -i $word`
			if [ ! -z "$match" ]; then
				count=$(($count+1))
			fi
		done
		echo $count `cat /tmp/$au` >> /tmp/output
	done
	
	cat /tmp/tu >> output_alg2/$file
	cat /tmp/output | sort -nr >> output_alg2/$file 
	
	
done