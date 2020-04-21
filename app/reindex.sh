#!/bin/bash
codes=( ag al bc bo cp cr ed el es fa hs pe )
for code in "${codes[@]}"
do
        echo
        echo Indexing $code
	python3 app.py --delete --index --progress --code $code
done
python3 app.py --upload_index
sudo service jdbot-restutil restart
