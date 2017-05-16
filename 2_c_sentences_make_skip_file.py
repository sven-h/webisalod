import csv
import json
from utilwebisadb import set_csv_field_size


def generate_sentences_sorted_equidistant():
    with open('sentences_info.json', 'r') as fp:
        data = json.load(fp)
    max_length_sentence = data['max_length_sentence']
    max_length_pld = data['max_length_pld']

    with open('sentences_sorted_equidistant.bin', 'wb') as out, open('sentences_sorted.csv') as f:
        reader = csv.reader(f)
        row = next(reader, None)
        for i in range(data['min_id'], data['max_id'] + 1):
            if int(row[0]) == i:
                sentence = row[1].ljust(max_length_sentence).encode('UTF-8')
                pld = row[2].ljust(max_length_pld).encode('UTF-8')
                row = next(reader, None)
            else:
                sentence = ''.ljust(max_length_sentence).encode('UTF-8')
                pld = ''.ljust(max_length_pld).encode('UTF-8')
            out.write(sentence)
            out.write(pld)

if __name__ == "__main__":
    set_csv_field_size()
    generate_sentences_sorted_equidistant()