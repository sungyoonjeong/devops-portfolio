#!/bin/bash
mkdir -p /webdata
while true
do
	df -h / > /webdata/index.html
	sleep 10
done
