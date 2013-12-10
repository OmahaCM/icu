#!/bin/bash
strace arecord --verbose --duration=5 -D "plughw:1,0" > arecord.wav 2> arecord-strace.txt
