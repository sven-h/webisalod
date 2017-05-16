import csv
import os
import sys
import json
from utilwebisadb import set_csv_field_size

def make_one_file():
    files = [os.path.join("contextsdb_files", file) for file in os.listdir("contextsdb_files") if file.endswith(".csv")]
    max_length_sentence = 0
    max_length_pld = 0
    min_id = sys.maxint
    max_id = 0
    with open('sentences.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for file in files:
            print("file {}".format(file))
            with open(file) as f:
                reader = csv.reader((line.replace('\0','') for line in f))
                next(reader, None)  # skip the headers
                for row in reader:
                    writer.writerow(row[1:])
                    max_length_sentence = max(max_length_sentence, len(row[2]))
                    max_length_pld = max(max_length_pld, len(row[3]))
                    prov_id = int(row[1])
                    min_id = min(min_id, prov_id)
                    max_id = min(max_id, prov_id)

    with open('sentences_info.json', 'w') as jsonfile:
        json.dump({'max_length_sentence': max_length_sentence,
                   'max_length_pld': max_length_pld,
                   'min_id': min_id,
                   'max_id': max_id}, jsonfile)


if __name__ == "__main__":
    set_csv_field_size()
    make_one_file()
