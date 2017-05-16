import csv
import datetime
import codecs
import ujson
from rdflib import Graph, URIRef, RDFS
from collections import Counter, defaultdict
from utilwebisadb import set_csv_field_size, read_redirects


def read_types(redirects, subject_object, file_path):
    print("{} - start loading {}".format(datetime.datetime.now(), file_path))
    with codecs.open(file_path, 'r', encoding='utf8') as file:
        for i, line in enumerate(file):
            if line[0] != '<':
                continue
            subject = line[1:line.index('>')]
            subject = redirects.get(subject, subject)
            object = line[line.rindex('<') + 1:line.rindex('>')]
            if object.startswith('http://dbpedia.org/ontology/'):
                object_list = subject_object[subject]
                if object not in object_list:
                    object_list.append(object)
            if i % 1000000 == 0:
                print("{} - {} imported".format(datetime.datetime.now(), i))
            #if i > 1000:
            #    break


def read_instance_types():

    redirects = read_redirects()
    subject_object = defaultdict(list)

    read_types(redirects, subject_object, 'instance_types_en.ttl')
    #read_types(redirects, subject_object, 'instance_types_transitive_en.ttl')
    #read_types(redirects, subject_object, 'instance_types_lhd_dbo_en.ttl')
    read_types(redirects, subject_object, 'instance_types_sdtyped_dbo_en.ttl')
    #read_types(redirects, subject_object, 'instance_types_dbtax_dbo_en.ttl')

    print('write json')
    with open('instance_types.json', 'w') as outfile:
        ujson.dump(subject_object, outfile)
    print('finish')


def read_sub_class_of():
    sub_class_of = {}
    g = Graph()
    g.parse("dbpedia_2016-04.nt", format="nt")
    for s, o in g.subject_objects(RDFS.subClassOf):
        str_s = str(s)
        str_o = str(o)
        if str_s.startswith('http://dbpedia.org/ontology/') and str_o.startswith('http://dbpedia.org/ontology/'):
            sub_class_of[str_s] = str_o
    return sub_class_of

def get_highest_class(list_of_types, sub_class_of):
    for type in list_of_types:
        while True:
            higher_type = sub_class_of.get(type, None)
            if higher_type == None or \
                            higher_type == 'http://dbpedia.org/ontology/Agent' or \
                            higher_type == 'http://dbpedia.org/ontology/Work' or \
                            higher_type == 'http://dbpedia.org/ontology/Person' or\
                            higher_type == 'http://dbpedia.org/ontology/Organisation' or \
                            higher_type == 'http://dbpedia.org/ontology/Place':
                return type
            type = higher_type
    return 'http://www.w3.org/2002/07/owl#Thing'

def get_highest_class_with_distance(list_of_types, sub_class_of, distance):
    if len(list_of_types) == 0:
        return 'http://www.w3.org/2002/07/owl#Thing'
    my_type = list_of_types[0]
    my_list = get_list_of_class_with_super_classes(my_type, sub_class_of)
    return my_list[:distance][-1]#shink to 3 elements and use last


def get_list_of_class_with_super_classes(clazz, sub_class_of):
    list_of_super_classes = [clazz]
    while True:
        higher_type = sub_class_of.get(clazz, None)
        if higher_type == None:
            return list(reversed(list_of_super_classes))
        list_of_super_classes.append(higher_type)
        clazz = higher_type

def get_local_name(str):
    return str[str.rfind('/')+1:].strip()

def analyse():
    print("{} - read instance_types".format(datetime.datetime.now()))
    with open('instance_types.json') as data_file:
        subject_object = ujson.load(data_file)

    print("{} - read subclassof".format(datetime.datetime.now()))
    sub_class_of = read_sub_class_of()

    print("{} - read mappings".format(datetime.datetime.now()))
    mapped_resources = set()
    with open('webisa_1_final_with_mapping.csv') as in_file:
        reader = csv.reader(in_file)
        for i, row in enumerate(reader):
            for entity in ujson.loads(row[19]):#actually only has one
                mapped_resources.add(entity)
            for entity in ujson.loads(row[21]):
                mapped_resources.add(entity)
            #if i > 10000:
            #    break
    print("{} - analyse".format(datetime.datetime.now()))
    instance_types = []
    for mapped_resource in mapped_resources:
        types = subject_object.get(mapped_resource, [])
        highest_type = get_highest_class_with_distance(types, sub_class_of, 3)#get_highest_class(types, sub_class_of)
        #print('{} -> {}    \t->{}'.format(mapped_resource, highest_type, types))#highest_types))

        instance_types.append(highest_type)

    print("{} - count and write".format(datetime.datetime.now()))

    counter = Counter(instance_types)
    print(counter)

    resulting_list = []
    for (concept, count) in counter.most_common():
        local_names = [get_local_name(x) for x in get_list_of_class_with_super_classes(concept, sub_class_of)]
        local_names += [''] * (3 - len(local_names))  # fill with '' if lost is too small
        resulting_list.append(local_names + [count])



    resulting_list_sorted = sorted(resulting_list, key=lambda x: (x[0], x[1], x[2]))

    with open('type_analysis.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in resulting_list_sorted:
            writer.writerow(row)

    print("{} - finish".format(datetime.datetime.now()))

if __name__ == "__main__":
    set_csv_field_size()
    #read_instance_types()
    analyse()



