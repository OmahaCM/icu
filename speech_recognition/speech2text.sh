#!/bin/bash -x

arecord -D 'plughw:1,0' -q -f cd -t wav | ffmpeg -loglevel panic -y -i - -ar 16000 -acodec flac file.flac 

echo done recording, lets upload.
#wget -q -U 'Mozilla/5.0' --post-file arecord.wav \
     --header 'Content-Type: audio/x-wav; rate=8000;' \
     -O stt-wave.txt \
     'http://www.google.com/speech-api/v1/recognize?lang=en-us&client=chromium'  

wget -q -U 'Mozilla/5.0' --post-file file.flac \
     --header 'Content-Type: audio/x-flac; rate=16000' \
     -O stt.txt \
     'http://www.google.com/speech-api/v1/recognize?lang=en-us&client=chromium'  
echo done uploading
#rm file.flac  > /dev/null 2>&1
