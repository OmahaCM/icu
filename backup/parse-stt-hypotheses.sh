cat stt-hypotheses.txt | cut -d: -f5-7 | sed -e 's/,\"confidence\":/=/' | sed -e 's/}]}//' | awk -F = '{ print $2 " " $1 }'  |sort --reverse --numeric-sort --field-separator== --key=2
