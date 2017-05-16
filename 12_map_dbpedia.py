import requests
import json
import csv
import codecs
import datetime
import ujson
from collections import defaultdict
import operator
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix, classification_report
from utilwebisadb import set_csv_field_size, get_ids_in_range, search_start_end_index_in_sentence, read_redirects


#################### spotlight query

# build spotlight:
# https://github.com/dbpedia-spotlight/dbpedia-spotlight/wiki/faq
# https://github.com/dbpedia-spotlight/lucene-quickstarter

def mapping_dbpedia_with_spotlight(text):
    # https://github.com/dbpedia-spotlight/dbpedia-spotlight/wiki/Web-service
    # https://github.com/dbpedia-spotlight/dbpedia-spotlight/wiki/User%27s-manual
    headers = {'Accept': 'application/json'}
    params = {'confidence': 0.05, 'support': 1, 'text': text}
    r = requests.get('http://localhost:2222/rest/annotate', headers=headers, params=params)
    if r.status_code != requests.codes.ok:
        print("ERROR: " + r.text)
        return []
    return r.json().get('Resources', [])


def filter_mappings_based_on_indices(mappings, start, end):
    filtered_mappings = []
    for mapping in mappings:
        mapping_start = int(mapping['@offset'])
        mapping_end = mapping_start + len(mapping['@surfaceForm'])
        if mapping_start >= start and mapping_end <= end:
            #coverage = float(len(mapping['@surfaceForm'])) / (end - start)
            #mapping['coverage'] = coverage
            filtered_mappings.append(mapping)
    return filtered_mappings


def query_spotlight(sentences, search):
    if len(sentences) == 0:
        return ''
    uris_to_hits = defaultdict(list)
    for sentence_data in sentences:
        sentence = sentence_data[1]
        start, end = search_start_end_index_in_sentence(sentence.lower(), search.lower())
        possible_mappings = mapping_dbpedia_with_spotlight(sentence)
        filtered_mappings = filter_mappings_based_on_indices(possible_mappings, start, end)
        for mapping in filtered_mappings:
            uris_to_hits[mapping['@URI']].append(mapping)
    if len(uris_to_hits) == 0:
        return ''
    elif len(uris_to_hits) == 1:
        return next(iter(uris_to_hits.keys()))
    # sum up and normalise
    score_list = []
    for uri, hits in uris_to_hits.items():
        #normalised_coverage = float(sum([hit['coverage'] for hit in hits])) / len(hits)
        normalised_score = float(sum([float(hit['@similarityScore']) for hit in hits])) / len(sentences)
        score_list.append((uri, normalised_score))#normalised_coverage,

    score_list.sort(key=lambda x: (x[1]), reverse=True)#key=lambda x: (x[1], x[2])
    #print(score_list[0][0])
    return score_list[0][0]


####################Elasticsearch - index


def create_index(index_name, type_name):
    r = requests.delete('http://localhost:9200/{}'.format(index_name))
    print("delete index: {}\n".format(r.status_code))
    payload = {
        'settings': {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'keyword_strip_lowercase_analyser': {
                        'type': 'custom',
                        'tokenizer': 'keyword',
                        'filter': ['lowercase', 'trim']
                    }
                }
            }
        },
        'mappings': {
            type_name: {
                'properties': {
                    'uri': {'type': 'keyword'},
                    'label': {'type': 'text', 'analyzer':'keyword_strip_lowercase_analyser', 'search_analyzer':'keyword_strip_lowercase_analyser'}
                }
            }
        }
    }
    r = requests.put('http://localhost:9200/{}'.format(index_name), json=payload)
    print("create index: {}\n".format(r.status_code))


def populate_elasticsearch(in_path, redirects, index_name, type_name):
    print("{} - start loading labels".format(datetime.datetime.now()))
    chunks = []
    with codecs.open(in_path, 'r', encoding='utf8') as file:
        for line in file:
            if line[0] != '<':
                continue
            subject = line[1:line.index('>')]
            label = line[line.index('"') + 1:line.rindex('"')]
            redirected_subject = redirects.get(subject, subject)

            chunks.append(ujson.dumps({'index': {'_index': index_name, '_type': type_name}}))
            chunks.append(ujson.dumps({'uri': redirected_subject, 'label': label}))
            if len(chunks) >= 2000:
                res = requests.post(url='http://localhost:9200/_bulk', data='\n'.join(chunks) + '\n',
                                    headers={'Content-Type': 'application/x-ndjson'})
                print("{} status code: {} len: {}".format(datetime.datetime.now(), res.status_code, len(chunks)))
                chunks.clear()
        if len(chunks) > 0:
            res = requests.post(url='http://localhost:9200/_bulk', data='\n'.join(chunks) + '\n',
                                headers={'Content-Type': 'application/x-ndjson'})
            print("{} last status code: {} len: {}".format(datetime.datetime.now(), res.status_code, len(chunks)))
            chunks.clear()
    print("{} - finished loading".format(datetime.datetime.now()))


def index_files():
    redirects = read_redirects()

    create_index('labels_index', 'labels')
    populate_elasticsearch('labels_en.ttl', redirects, 'labels_index', 'labels')

    create_index('category_index', 'categories')
    populate_elasticsearch('category_labels_en.ttl', redirects, 'category_index', 'categories')

    create_index('anchor_index', 'anchors')
    populate_elasticsearch('anchor_text_en.ttl', redirects, 'anchor_index', 'anchors')


####################Elasticsearch - quey

def query_es(index_name, type_name, search):
    res = requests.get(url='http://localhost:9200/{}/{}/_search'.format(index_name, type_name),
                       headers={'Content-Type': 'application/json'},
                       json={
                           'query': {
                               'multi_match': {
                                   'query': search,
                                   'fields': ['label']
                               }
                           }
                       })
    return res.json()['hits']['hits']


def query_es_first_uri(index_name, type_name, search):
    result = query_es(index_name, type_name, search)
    if len(result) == 0:
        return ''
    return result[0]['_source']['uri']


def query_es_first_uri_page(search):
    return query_es_first_uri('labels_index', 'labels', search)


def query_es_first_uri_category(search):
    return query_es_first_uri('category_index', 'categories', search)


def query_es_first_uri_anchor(search):
    return query_es_first_uri('anchor_index', 'anchors', search)



### fast match like ES
def get_count_same_cases(str_a, str_b):
    count = 0
    for i in range(len(str_a)):
        if (str_a[i].islower() and str_b[i].islower()) or (str_a[i].isupper() and str_b[i].isupper()):
            count += 1
    return count

class fast_match:
    def __init__(self, redirects, file_path):
        self.lowercased = defaultdict(list)

        with codecs.open(file_path, 'r', encoding='utf8') as file:
            for i, line in enumerate(file):
                if line[0] != '<':
                    print('line did not start with <: {}'.format(line))
                    continue
                subject = line[1:line.index('>')]
                label = line[line.index('"') + 1:line.rindex('"')]
                redirected_subject = redirects.get(subject, subject)
                label = label.strip()

                self.lowercased[label.lower()].append((label, redirected_subject))

                #if i > 500000:
                #    break


    def query(self, search):
        search = search.strip()
        candidates = self.lowercased.get(search.lower(), [])
        if len(candidates) == 0:
            return ''
        if len(candidates) == 1:
            return candidates[0][1]

        list_to_sort = [(get_count_same_cases(search, original_label), uri) for (original_label, uri) in candidates]
        list_to_sort.sort(key=lambda x: x[0], reverse=True)
        return list_to_sort[0][1]

    #def query_with_s(self, search):
    #    search = search.strip()
    #    candidates = self.lowercased.get(search.lower(), [])
    #    if len(candidates) == 0:
    #        return self.query(search + "s")
    #    if len(candidates) == 1:
    #        return candidates[0][1]
    #    list_to_sort = [(get_count_same_cases(search, original_label), uri) for (original_label, uri) in candidates]
    #    list_to_sort.sort(key=lambda x: x[0], reverse=True)
    #    return list_to_sort[0][1]


def read_label_and_category():
    redirects = read_redirects()
    fast_match_page = fast_match(redirects, 'labels_en.ttl')
    fast_match_category = fast_match(redirects, 'category_labels_en.ttl')
    return fast_match_page, fast_match_category


####################evaluate all approaches


def get_y_true(gold_list):
    if gold_list[0] == 'not:possible':
        return 'not_found'
    else:
        return 'found'

def get_y_pred(gold_list, result):
    if gold_list[0] == 'not:possible':
        if result == '':
            return 'not_found'
        else:
            return 'found'
    else:
        if result in gold_list:
            return 'found'
        else:
            return 'not_found'


def get_page_mapping_results(gold_list, search, sentences, y_true, y_pred_anchor, y_pred_spotlight, y_pred_fast, fast_match_obj):
    if len(gold_list) > 0:
        y_true.append(get_y_true(gold_list))
        y_pred_anchor.append(get_y_pred(gold_list, query_es_first_uri_anchor(search)))
        y_pred_spotlight.append(get_y_pred(gold_list, query_spotlight(sentences, search)))
        y_pred_fast.append(get_y_pred(gold_list, fast_match_obj.query(search)))


def get_category_mapping_results(gold_list, search, sentences, y_true, y_pred_anchor, y_pred_spotlight, y_pred_fast, fast_match_obj):
    if len(gold_list) > 0:
        y_true.append(get_y_true(gold_list))
        y_pred_anchor.append(get_y_pred(gold_list, query_es_first_uri_anchor(search)))
        y_pred_spotlight.append(get_y_pred(gold_list, query_spotlight(sentences, search)))
        y_pred_fast.append(get_y_pred(gold_list, fast_match_obj.query(search)))


def evaluate_on_gold_set():
    y_true_page = []
    y_true_category = []

    y_pred_anchor_page = []
    y_pred_anchor_category = []

    y_pred_spotlight_page = []
    y_pred_spotlight_category = []

    y_pred_fast_page = []
    y_pred_fast_category = []

    fast_match_page, fast_match_category = read_label_and_category()

    with open('webisa_1_sentence_results_with_sent.csv') as in_file:
        reader = csv.reader(in_file)
        for i, row in enumerate(reader):
            instance_to_page = json.loads(row[19])
            instance_to_category = json.loads(row[20])
            class_to_page = json.loads(row[21])
            class_to_category = json.loads(row[22])

            instance = row[1]
            clazz = row[2]
            sentences = json.loads(row[14])

            get_page_mapping_results(instance_to_page, instance, sentences, y_true_page, y_pred_anchor_page,y_pred_spotlight_page, y_pred_fast_page, fast_match_page)
            get_category_mapping_results(instance_to_category, instance, sentences, y_true_category, y_pred_anchor_category, y_pred_spotlight_category, y_pred_fast_category, fast_match_category)

            get_page_mapping_results(class_to_page, clazz, sentences, y_true_page, y_pred_anchor_page, y_pred_spotlight_page, y_pred_fast_page, fast_match_page)
            get_category_mapping_results(class_to_category, clazz, sentences, y_true_category, y_pred_anchor_category,y_pred_spotlight_category, y_pred_fast_category, fast_match_category)


            print("finished line {}".format(i))

    print('anchor search:')
    print('only pages:')
    print(confusion_matrix(y_true_page, y_pred_anchor_page))
    print(classification_report(y_true_page, y_pred_anchor_page))
    print('only categories:')
    print(confusion_matrix(y_true_category, y_pred_anchor_category))
    print(classification_report(y_true_category, y_pred_anchor_category))
    print('both:')
    print(confusion_matrix(y_true_page + y_true_category, y_pred_anchor_page + y_pred_anchor_category))
    print(classification_report(y_true_page + y_true_category, y_pred_anchor_page + y_pred_anchor_category))

    print('spotlight search:')
    print('only pages:')
    print(confusion_matrix(y_true_page, y_pred_spotlight_page))
    print(classification_report(y_true_page, y_pred_spotlight_page))
    print('only categories:')
    print(confusion_matrix(y_true_category, y_pred_spotlight_category))
    print(classification_report(y_true_category, y_pred_spotlight_category))
    print('both:')
    print(confusion_matrix(y_true_page + y_true_category, y_pred_spotlight_page + y_pred_spotlight_category))
    print(classification_report(y_true_page + y_true_category, y_pred_spotlight_page + y_pred_spotlight_category))

    print('fast search:')
    print('only pages:')
    print(confusion_matrix(y_true_page, y_pred_fast_page))
    print(classification_report(y_true_page, y_pred_fast_page))
    print('only categories:')
    print(confusion_matrix(y_true_category, y_pred_fast_category))
    print(classification_report(y_true_category, y_pred_fast_category))
    print('both:')
    print(confusion_matrix(y_true_page + y_true_category, y_pred_fast_page + y_pred_fast_category))
    print(classification_report(y_true_page + y_true_category, y_pred_fast_page + y_pred_fast_category))




########## prediction

def get_json_list(result):
    if result == '':
        return '[]'
    else:
        return json.dumps([result])

def predict():
    with open('webisa_1_final.csv') as in_file, open('webisa_1_final_with_mapping.csv', "w", newline='') as out_file:
        print("start at {}".format(datetime.datetime.now()))
        reader = csv.reader(in_file)
        writer = csv.writer(out_file)

        category_mappings = 0
        page_mappings = 0
        page_mapped = set()
        category_mapped = set()
        all = set()

        fast_match_page, fast_match_category = read_label_and_category()

        for i, row in enumerate(reader):
            instance = row[1]
            clazz = row[2]

            all.add(instance)
            all.add(clazz)

            instance_page = fast_match_page.query(instance)
            instance_category = fast_match_category.query(instance)
            clazz_page = fast_match_page.query(clazz)
            clazz_category = fast_match_category.query(clazz)

            if instance_page != '':
                page_mappings += 1
                page_mapped.add(instance)
            if instance_category != '':
                category_mappings += 1
                category_mapped.add(instance)
            if clazz_page != '':
                page_mappings += 1
                page_mapped.add(clazz)
            if clazz_category != '':
                category_mappings += 1
                category_mapped.add(clazz)

            writer.writerow(row + ['', ''] + [get_json_list(instance_page),get_json_list(instance_category), get_json_list(clazz_page), get_json_list(clazz_category)])

            if i % 100000 == 0:
                print(i)
            #print(i)
            #if i> 1000:
            #    break

        print("{} page mappings".format(page_mappings))
        print("{} category mappings".format(category_mappings))

        print("{} unique page mappings".format(len(page_mapped)))
        print("{} unique category mappings".format(len(category_mapped)))

        print("{} unique resources".format(len(all)))
        print("end at {}".format(datetime.datetime.now()))


def map_yago():
    prefix_yago = 'http://yago-knowledge.org/resource/'
    prefix_dbpedia_cat = 'http://dbpedia.org/resource/Category:'
    print("{} - load yago taxonomie".format(datetime.datetime.now()))
    map_categories_to_yago = {}
    with codecs.open('yagoTaxonomy.tsv', 'r', encoding='utf8') as in_file:
        reader = csv.reader(in_file, delimiter='\t')
        next(reader) # skip header
        for row in reader:
            link = row[1]
            if link.startswith('<wikicat_'):
                wiki_cat_link = prefix_dbpedia_cat + link[9:-1]
                yago_link = prefix_yago + link[1:-1]#remove < and >
                map_categories_to_yago[wiki_cat_link] = yago_link
    print("{} - finished loading yago taxonomie - {} wikicat".format(datetime.datetime.now(), len(map_categories_to_yago)))


    dbpedia_categories_all = set()
    mapped_dbpedia_categories = set()
    #not_mapped =set()
    with open('webisa_1_final_with_mapping.csv') as in_file, open('webisa_1_final_with_mapping_yago_test.csv', "w", newline='') as out_file:
        reader = csv.reader(in_file)
        writer = csv.writer(out_file)
        for i, row in enumerate(reader):
            instance_to_yago = ''
            clazz_to_yago = ''

            instance_category = next(iter(ujson.loads(row[20])), None)
            if instance_category is not None:
                dbpedia_categories_all.add(instance_category)
                instance_to_yago = map_categories_to_yago.get(instance_category, '')
                if instance_to_yago != '':
                    mapped_dbpedia_categories.add(instance_category)
                #else:
                #    not_mapped.add(instance_category)

            clazz_category = next(iter(ujson.loads(row[22])), None)
            if clazz_category is not None:
                dbpedia_categories_all.add(clazz_category)
                clazz_to_yago = map_categories_to_yago.get(clazz_category, '')
                if clazz_to_yago != '':
                    mapped_dbpedia_categories.add(clazz_category)
                #else:
                #    not_mapped.add(instance_category)

            writer.writerow(row + [instance_to_yago, clazz_to_yago])

            #if i > 100000:
            #    break

    #for r in not_mapped:
    #    print("not found: {}".format(r))

    print('unique dbpedia categories: {}'.format(len(dbpedia_categories_all)))
    print('unique mapped categories: {}'.format(len(mapped_dbpedia_categories)))






def count():
    all = set()
    with open('webisa_1_final.csv') as in_file:
        reader = csv.reader(in_file)
        for i, row in enumerate(reader):
            instance = row[1]
            clazz = row[2]
            all.add(instance)
            all.add(clazz)
    print(len(all))

if __name__ == "__main__":
    set_csv_field_size()

    #index_files()
    #evaluate_on_gold_set()

    map_yago()

    #predict()
    #count()


