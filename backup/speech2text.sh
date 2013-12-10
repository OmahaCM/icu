#!/bin/bash          
DEBUG=0
DURATION=--duration=7
AUDIOFORMAT=--format=cd         # U8         # cd
REMOVEOLDFILES=1
REMOVECONFIDENCE=1
PRINTOUT=

if [[ 1 -eq $REMOVEOLDFILES ]]; then
  rm file.flac stt.json stt.txt > /dev/null 2>&1
fi;

arecord --mmap --start-delay=0 -D 'plughw:1,0' $DURATION -q $AUDIOFORMAT -t wav | ffmpeg -loglevel panic -y -i - -ar 16000 -acodec flac file.flac > /dev/null 2>&1
if [[ 1 -le $DEBUG ]]; then 
  echo done recording, lets upload. 
fi;

if [[ 0 -eq 1 ]]; then
  wget -q -U 'Mozilla/5.0' --post-file arecord.wav \
   --header 'Content-Type: audio/x-wav; rate=8000;' \
   -O stt-wave.txt \
   'http://www.google.com/speech-api/v1/recognize?lang=en-us&client=chromium'  
fi;

wget -q -U 'Mozilla/5.0' --post-file file.flac \
     --header 'Content-Type: audio/x-flac; rate=16000' \
     -O stt.json \
     'http://www.google.com/speech-api/v1/recognize?lang=en-us&client=chromium'  
if [[ 1 -le $DEBUG ]]; then 
  echo done uploading, getting stt.json.
fi;

if [[ 1 -eq $REMOVECONFIDENCE ]]; then
  PRINTOUT=' $1 ';  #PRINTS JUST THE UTTERANCE
  cat stt.json | cut -d: -f5-7 | sed -e 's/,\"confidence\":/=/' | sed -e 's/}]}//' | awk -F = '{ print $1 }'  > stt.txt

else

  PRINTOUT=' $2 = "$1" ';  #PRINTS CONFIDENCE of SPEECH REC UTTERANCE
  cat stt.json | cut -d: -f5-7 | sed -e 's/,\"confidence\":/=/' | sed -e 's/}]}//' | awk -F = '{ print $PRINTOUT }'  |sort --reverse --numeric-sort --field-separator== --key=2 > stt.txt

fi;
