#!/bin/bash
codes=( ag al bc bo cp cr ed el es fa hs pe )
for code in "${codes[@]}"
do
        echo Indexing $code
	python3 app.py --index --progress --code $code
done
python3 app.py --upload
