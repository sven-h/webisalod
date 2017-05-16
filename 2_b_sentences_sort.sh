mkdir sort_tmp
sort -t "," -n -k 1,1 -T ./sort_tmp sentences.csv -o sentences_sorted.csv
rm -r sort_tmp