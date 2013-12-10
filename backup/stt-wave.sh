#!/bin/bash -x

#ASSUMES arecord.wav is a real WAV file at 8000
wget -q -U "Mozilla/5.0" --post-file arecord.wav --header "Content-Type: audio/x-wav; rate=8000" -O - "http://www.google.com/speech-api/v1/recognize?lang=en-us&client=chromium"  >stt-wave.txt

