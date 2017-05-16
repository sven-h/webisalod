import csv
from itertools import chain
import random
import json
from utilwebisadb import set_csv_field_size, get_ids_in_range, search_start_end_index_in_sentence



def create_relation_template():
    for i in range(0, 20):
        print(
            """<tr><td style="text-align: left;">${r_?}</td><td><input type="radio" name="${id_?}" value="yes" required="required"/></td><td><input type="radio" name="${id_?}" value="uncertain" required="required"/></td><td><input type="radio" name="${id_?}" value="no" required="required"/></td></tr>"""
            .replace("?", str(i)))


def create_sentence_template():
    for i in range(0, 10):
        print(
"""<li>
<p>${sentence_?}</p>
<div class="form-horizontal">
  <div class="form-group">
    <div class="col-sm-2"><label class="control-label">${label_?_instance}</label></div>
    <div class="col-sm-5"><input type="url" class="form-control" name="${id_?}_instance_page" placeholder="English Wikipedia page URL or 'not:possible'" required></div>
    <div class="col-sm-5"><input type="url" class="form-control" name="${id_?}_instance_category" placeholder="English Wikipedia category URL or 'not:possible'" required></div>
  </div>
  <div class="form-group">
    <div class="col-sm-2"><label class="control-label">${label_?_class}</label></div>
    <div class="col-sm-5"><input type="url" class="form-control" name="${id_?}_class_page" placeholder="English Wikipedia page URL or 'not:possible'" required></div>
    <div class="col-sm-5"><input type="url" class="form-control" name="${id_?}_class_category" placeholder="English Wikipedia category URL or 'not:possible'" required></div>
  </div>
</div>
</li>""".replace("?", str(i)))

def replace_csv_in_template(template_path, data, out):
    template = ""
    with open(template_path, 'r') as template_file:
        template = template_file.read()
    with open(data) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for name in reader.fieldnames:
                template = template.replace("${"+ name + "}", row[name])
                print("replace {} with {}".format("${"+ name + "}", row[name]))
            break #only first line to test
    with open(out, "w") as out:
        out.write(template)


def write_mturk_relation_csv(csv_file, mturk_csv_file, k, has_headers=False):
    with open(mturk_csv_file, "w", newline='') as out :
        writer = csv.writer(out)
        writer.writerow(chain.from_iterable(("r_" + str(i), "id_" + str(i)) for i in range(0, k)))

        relation_id_list = []
        with open(csv_file) as f:
            reader = csv.reader(f)
            if has_headers:
                next(reader, None)  # skip the headers
            for row in reader:
                if len(relation_id_list) == (k*2):
                    writer.writerow(relation_id_list)
                    relation_id_list.clear()
                relation_id_list.append(row[1] + " is a " + row[2])  # relation string
                relation_id_list.append(row[0])  # id
            if len(relation_id_list) == (k * 2): # write last line if it has enough content
                writer.writerow(relation_id_list)


def write_mturk_sentence_csv(csv_file, mturk_sentence_csv_file, k, has_headers=False):

    #load sentences info
    with open('sentences_info.json', 'r') as fp:
        data = json.load(fp)
    max_length_sentence = data['max_length_sentence']
    max_length_pld = data['max_length_pld']
    length_one_entry = max_length_sentence + max_length_pld
    min_id = data['min_id']
    max_id = data['max_id']

    with open(mturk_sentence_csv_file, "w", newline='') as out, open('sentences_sorted_equidistant.bin', 'rb') as sentences_sorted_equidistant_file:
        writer = csv.writer(out)
        writer.writerow(chain.from_iterable(("sentence_{}".format(i), "label_{}_instance".format(i), "id_{}".format(i), "label_{}_class".format(i)) for i in range(0, k)))

        entity_list = []
        with open(csv_file) as f:
            reader = csv.reader(f)
            if has_headers:
                next(reader, None)  # skip the headers
            for row in reader:
                if len(entity_list) == (k*4):
                    writer.writerow(entity_list)
                    entity_list.clear()

                prov_id_list = get_ids_in_range(row[14], min_id, max_id)
                random.shuffle(prov_id_list)

                sentence = ""
                for id in prov_id_list:
                    skip = (id - min_id) * length_one_entry
                    sentences_sorted_equidistant_file.seek(skip)
                    sentence = sentences_sorted_equidistant_file.read(max_length_sentence).decode("utf-8").rstrip()
                    if sentence:
                        break

                if sentence:

                    instance_start, instance_end = search_start_end_index_in_sentence(sentence.lower(), row[1].lower())
                    if instance_start != -1 and instance_end != -1:
                        sentence = sentence[:instance_start] + '<strong>' + sentence[instance_start:instance_end] + '</strong>' + sentence[instance_end:]

                    class_start, class_end = search_start_end_index_in_sentence(sentence.lower(), row[2].lower())
                    if class_start != -1 and class_end != -1:
                        sentence = sentence[:class_start] + '<strong>' + sentence[class_start:class_end] + '</strong>' + sentence[class_end:]
                else:
                    print("No sentence for {}".format(row))

                entity_list.append(sentence)
                entity_list.append(row[1])#instance label
                entity_list.append(row[0])#id
                entity_list.append(row[2])#class label

            if len(entity_list) == (k * 4): # write last line if it has enough content
                writer.writerow(entity_list)


if __name__ == "__main__":
    set_csv_field_size()
    #create_sentence_template()

    #for i in [1]: #[20, 10, 5, 3, 2, 1, 0]:
    #    write_mturk_relation_csv('webisa_{}_sample_500.csv'.format(i), 'webisa_{}_sample_500_mturk.csv'.format(i), 20)

    #write_mturk_sentence_csv('webisa_1_sentence_sample_1000.csv', 'webisa_1_sentence_sample_1000_mturk.csv', 10)

    replace_csv_in_template('mTurk_Sentence.html', 'webisa_1_sentence_sample_1000_mturk.csv','mTurk_Sentence_test_replaced.html')
