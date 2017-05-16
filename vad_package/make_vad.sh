docker run -it -v /media/sf_dev/mannheim/virtuoso_make_vad/webisalod:/import joernhees/virtuoso bash
#within bash
cd /import
virtuoso-t
isql-vt ERRORS=STDOUT VERBOSE=OFF PROMPT=OFF "EXEC=DB.DBA.VAD_PACK('/import/webisalod_vad_sticker.xml', '.', '/import/webisalod_dav.vad');"  >> vad_log.txt

#test vad

docker run -it -v /media/sf_dev/mannheim/virtuoso_make_vad/virtuoso_db:/var/lib/virtuoso-opensource-7 joernhees/virtuoso
rm -f /media/sf_dev/mannheim/virtuoso_make_vad/virtuoso_db/db/virtuoso.lck
docker run -it -v /media/sf_dev/mannheim/virtuoso_make_vad/virtuoso_db:/var/lib/virtuoso-opensource-7 \
    -p 8890:8890 \
    -e "NumberOfBuffers=$((8*85000))" \
    joernhees/virtuoso

docker run -p 8890:8890 joernhees/virtuoso


