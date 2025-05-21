rm -rf data de 
hudoc --type echr --rss-file echr_short.xml
hudoc --type grevio --rss-file grevio_short.xml --full --threads 5
hudoc --type grevio --link https://hudoc.grevio.coe.int/app/transform/rss\?library=grevioeng\&query=contentsitename:GREVIO\%20AND\%20\(\(greviolanguage=\%22ENG\%22\)\)\&sort=greviodocumentid\%20ascending,greviopublicationdate\%20descending\&start=0



hudoc --type echr --rss-file echr_short.xml --evid --output-dir de --full 


