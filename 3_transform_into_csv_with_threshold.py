import csv
import os
import sys
import ujson
from utilwebisadb import set_csv_field_size


def get_full_label(premod, lemma, postmod):
    return " ".join(filter(None, [premod, lemma, postmod]))


def get_csv_array(instance_lemma, class_lemma, modification):
    return [modification["_id"]["$numberLong"],  # id
            get_full_label(modification["ipremod"], instance_lemma, modification["ipostmod"]),
            get_full_label(modification["cpremod"], class_lemma, modification["cpostmod"]),
            int(float(modification["frequency"])),
            modification["pidspread"],
            modification["pldspread"],
            modification["ipremod"],
            instance_lemma,
            modification["ipostmod"],
            modification["cpremod"],
            class_lemma,
            modification["cpostmod"],
            modification["pids"],
            modification["plds"],
            modification["provids"]
    ]

def translate_csv():

    with open('webisa_0.csv', 'w', newline='') as file_0,\
         open('webisa_1.csv', 'w', newline='') as file_1, \
         open('webisa_2.csv', 'w', newline='') as file_2,\
         open('webisa_3.csv', 'w', newline='') as file_3, \
         open('webisa_5.csv', 'w', newline='') as file_5, \
         open('webisa_10.csv', 'w', newline='') as file_10, \
         open('webisa_20.csv', 'w', newline='') as file_20, \
         open('webisa_40.csv', 'w', newline='') as file_40:

        #header = ['id', 'instance', 'class', 'frequency', 'pidspread', 'pldspread', 'ipremod', 'ilemma', 'ipostmod',
        #          'cpremod', 'clemma', 'cpostmod', 'pids', 'plds', 'provids']

        #0 - id
        #1 - instance
        #2 - class
        #3 - frequency
        #4 - pidspread
        #5 - pldspread
        #6 - ipremod
        #7 - ilemma
        #8 - ipostmod
        #9 - cpremod
        #10- clemma
        #11- cpostmod
        #12- pids
        #13- plds
        #14- provids
        #15- majority voting
        #16- yes (counts)
        #17- uncertain (counts)
        #18- no (counts)
        #19- mapping instance to dbpedia page (json array)
        #20- mapping instance to dbpedia category (json array)
        #21- mapping class to dbpedia page (json array)
        #22- mapping class to dbpedia category (json array)
        #23 -mapping instance to yago (string)
        #24 -mapping class to yago (string)


        writer_0 = csv.writer(file_0)
        writer_1 = csv.writer(file_1)
        writer_2 = csv.writer(file_2)
        writer_3 = csv.writer(file_3)
        writer_5 = csv.writer(file_5)
        writer_10 = csv.writer(file_10)
        writer_20 = csv.writer(file_20)
        writer_40 = csv.writer(file_40)

        for file in os.listdir("tuplesdb_files"):
            if file.endswith(".csv"):
                with open(os.path.join("tuplesdb_files", file)) as input_file:
                    reader = csv.reader((line.replace('\0', '') for line in input_file))#replace Null bytes
                    next(reader, None)  # skip the headers
                    for row in reader:
                        modifications = ujson.loads(row[6])
                        if len(modifications) == 0:
                            print("Error - no modifications")
                        for modification in modifications:
                            csv_array = get_csv_array(row[1], row[2], modification)
                            writer_0.writerow(csv_array)
                            pidspread = int(modification["pidspread"])
                            pldspread = int(modification["pldspread"])
                            if pidspread > 1 and pldspread > 1:
                                writer_1.writerow(csv_array)
                                if pidspread > 2 and pldspread > 2:
                                    writer_2.writerow(csv_array)
                                    if pidspread > 3 and pldspread > 3:
                                        writer_3.writerow(csv_array)
                                        if pidspread > 5 and pldspread > 5:
                                            writer_5.writerow(csv_array)
                                            if pidspread > 10 and pldspread > 10:
                                                writer_10.writerow(csv_array)
                                                if pidspread > 20 and pldspread > 20:
                                                    writer_20.writerow(csv_array)
                                                    if pidspread > 40 and pldspread > 40:
                                                        writer_40.writerow(csv_array)
                print("Processed file {}".format(file))

if __name__ == "__main__":
    set_csv_field_size()
    translate_csv()
