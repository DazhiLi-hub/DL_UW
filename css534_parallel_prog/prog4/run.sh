#!/bin/sh

spark-submit --class ShortestPath --master spark://cssmpi8h:58240 --executor-memory 1G --total-executor-cores $4 ShortestPath.jar $1 $2 $3
