#!/bin/bash
DEBUG=0
NICE='nice -n -10'
NICE=

while [[ 1 ]]; do
  echo "Recording... Say \"GoodBye\" or Press Ctrl+C to Stop."
  $NICE ./speech2text.sh
  #Check if stt.txt exists and is of size greater than zero.
  #`man test` or `info coreutils 'test invocation'` 
  if [[ ( -e stt.txt ) && ( -s stt.txt ) ]]; then 
   if [[ 1 -le $DEBUG ]]; then
    echo "stt.txt exists and greater than zero, lets continue."
   fi;
  else 
    echo -n "No stt.txt content, ";
    if [[ 1 -le $DEBUG ]]; then
      echo " aborting.";
      exit 1;
    fi;
    echo " recording again." 
    continue;
  fi;
  
  #if 0; then
  QUESTION=$(cat stt.txt)
  echo "Me: " $QUESTION
  ANSWER=$(python queryprocess.py $QUESTION)
  echo "Robot: ", $ANSWER
  ./text2speech.sh $ANSWER
  if [[ 1 -le `grep --count -E -i "GoodBye" stt.txt` ]]; then
    exit;
  fi;
  #fi
done; 
