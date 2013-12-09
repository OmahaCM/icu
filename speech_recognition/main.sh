#!/bin/bash
echo "Recording... Press Ctrl+C to Stop."
./speech2text.sh
#Check if stt.txt exists and is of size greater than zero.
#`man test` or `info coreutils 'test invocation'` 
if [[ ( -e stt.txt ) && ( -s stt.txt ) ]]; then 
  echo "stt.txt exists and greater than zero, lets continue."
else 
  echo "No stt.txt content, aborting.";
  exit 1;
fi

#if 0; then
QUESTION=$(cat stt.txt)
echo "Me: ", $QUESTION
ANSWER=$(python queryprocess.py $QUESTION)
echo "Robot: ", $ANSWER
./text2speech.sh $ANSWER
#fi
