#!/bin/bash

FILE="alterunits2.txt"
#FILE="alterunits.txt"

#$1=serial
#$2=topic unit
#$3=alternate unit 1
#$4=alternate unit 2
#$5=alternate unit 3
#$6=alternate unit 4
#$7=alternate unit 5

mkdir -p sentences
rm sentences/*
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
	python urldigger-02c/urldigger.py -g "$tu" > /tmp/urls
	#cat /tmp/urls		
	
	wiki_url=`cat /tmp/urls | grep -i "en.wikipedia.org" | head -1`
	echo $wiki_url
done