#!/bin/bash

FILE="alterunits2.txt"

#$1=serial
#$2=topic unit
#$3=alternate unit 1
#$4=alternate unit 2
#$5=alternate unit 3
#$6=alternate unit 4
#$7=alternate unit 5
cat $FILE | awk -F"\t" '{print $2}'