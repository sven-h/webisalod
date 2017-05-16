import csv
import ujson
import time
import datetime
from utilwebisadb import set_csv_field_size, get_ids_in_range
import mmap


#@profile
def append_sentences(in_path, out_path):
	#need SSD otherwise very, very slow
    # load sentences info
    with open('sentences_info.json', 'r') as fp:
        data = ujson.load(fp)
    max_length_sentence = data['max_length_sentence']
    max_length_pld = data['max_length_pld']
    length_one_entry = max_length_sentence + max_length_pld
    min_id = data['min_id']
    max_id = data['max_id']


    with open(in_path) as in_file, open(out_path, "w", newline='') as out_file, open('E:\\sentences_sorted_equidistant.bin', 'rb') as sentences_sorted_equidistant_file:
        reader = csv.reader(in_file)
        writer = csv.writer(out_file)

        start = time.perf_counter()
        for i, row in enumerate(reader):
            prov_id_list = get_ids_in_range(row[14], min_id, max_id)
            prov_list = []
            for id in prov_id_list:
                skip = (id - min_id) * length_one_entry
                sentences_sorted_equidistant_file.seek(skip)
                sentence = sentences_sorted_equidistant_file.read(max_length_sentence).decode("utf-8").rstrip()
                pld = sentences_sorted_equidistant_file.read(max_length_pld).decode("utf-8").rstrip()				
                prov_list.append((id, sentence, pld))
            writer.writerow(row[:14] + [ujson.dumps(prov_list)] + row[15:])
            
            #print("{} - {}".format(i, len(prov_id_list)))
            if i % 1000 == 0:
                print("{} - {}".format(datetime.datetime.now(), i))
            #print(i)
        print('finished in  {} sec'.format(time.perf_counter()-start))



if __name__ == "__main__":
    set_csv_field_size()
    #for i in [0]:
        #append_sentences('webisa_{}.csv'.format(i), 'webisa_{}_with_sent.csv'.format(i))
        #append_sentences('webisa_{}_sample_results.csv'.format(i),'webisa_{}_sample_results_with_sent.csv'.format(i))
        #append_sentences('webisa_{}_cycles_results.csv'.format(i), 'webisa_{}_cycles_results_with_sent.csv'.format(i))
    append_sentences('webisa_1_sentence_results.csv', 'webisa_1_sentence_results_with_sent.csv')
    #append_sentences('webisa_5_sample_results.csv', 'webisa_5_sample_results_with_sent.csv')
