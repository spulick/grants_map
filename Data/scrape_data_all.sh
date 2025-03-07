#cd /mnt/d/GitHub/grants_map/Data/Grants Archive

lynx --useragent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0" \
"https://www.grants.gov.au/reports/gaweeklyexport" -dump -listonly -nonumbers | grep /Reports/GaWeeklyExportDownload > ./uuid_urls.txt

xargs --max-lines=1 lynx --useragent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0" --cmd_script=./lynx-log < ./uuid_urls.txt