import csv
import json
import codecs
import datetime
import requests
import os.path
from collections import defaultdict, Counter
from utilwebisadb import set_csv_field_size, read_redirects, read_labels_resource_set

#### generate raw result file

def get_map_id_to_list_of_answer(results):
    instance_page = defaultdict(list)
    instance_category = defaultdict(list)
    class_page = defaultdict(list)
    class_category = defaultdict(list)

    with open(results) as _results_file:
        results_reader = csv.reader(_results_file)

        header = next(results_reader)
        index_list = []
        relation_id_list = []
        for i, item in enumerate(header):
            if item.startswith("Answer."):
                index_list.append(i)
                id_ = item.split(".")[1]
                idsplit = id_.split('_', 1)
                relation_id_list.append((idsplit[0], idsplit[1]))

        amount_of_filled_cells = 0
        for row in results_reader:
            for i, index in enumerate(index_list):
                cell_content = row[index]
                if cell_content:
                    amount_of_filled_cells += 1
                    relation_id, type_of_dict = relation_id_list[i]
                    relation_id_int = int(relation_id)
                    if type_of_dict == 'instance_page':
                        instance_page[relation_id_int].append(cell_content)
                    elif type_of_dict == 'instance_category':
                        instance_category[relation_id_int].append(cell_content)
                    elif type_of_dict == 'class_page':
                        class_page[relation_id_int].append(cell_content)
                    elif type_of_dict == 'class_category':
                        class_category[relation_id_int].append(cell_content)
                    else:
                        print('wrong type - please check')
        print('amount_of_filled_cells: {}'.format(amount_of_filled_cells))
    return instance_page, instance_category, class_page, class_category


def translate_files(samples, mturk_results, out):
    instance_page, instance_category, class_page, class_category = get_map_id_to_list_of_answer(mturk_results)
    with open(samples) as samples_file, open(out, "w", newline='') as out_file:
        sample_reader = csv.reader(samples_file)
        writer = csv.writer(out_file)
        for row in sample_reader:
            id_ = int(row[0])
            writer.writerow(row + ['','','',''] + [json.dumps(instance_page.get(id_, [])),
                                                   json.dumps(instance_category.get(id_, [])),
                                                   json.dumps(class_page.get(id_, [])),
                                                   json.dumps(class_category.get(id_, []))])

###generate checked dbpedia url file

#cache
if os.path.isfile('redirect_wiki_cache.txt'):
    with open('redirect_wiki_cache.txt') as data_file:
        redirect_cache = json.load(data_file)
else:
    redirect_cache = {}


def get_redirected_url_from_live_wikipedia(url):
    cache_result = redirect_cache.get(url, None)
    if cache_result is None:
        r = requests.head(url, allow_redirects=True)
        redirect_cache[url] = r.url
        with open('redirect_wiki_cache.txt', 'w') as outfile:
            json.dump(redirect_cache, outfile)
        return r.url
    else:
        return cache_result


def check_page_or_category(url_list, redirects, resources, start_with, starting_length):
    new_set = set()
    not_possibel_is_conatined = False
    for url in url_list:
        url = url.strip()
        if url.startswith('not:'):
            not_possibel_is_conatined = True
            continue
        if not url.startswith(start_with):
            print('ignoring - the following url do not start with "{}": {}'.format(start_with, url))
            continue
        dbpedia_url = 'http://dbpedia.org/resource/' + url[starting_length:]
        redirected_depedia_url = redirects.get(dbpedia_url, dbpedia_url)
        if redirected_depedia_url in resources:
            new_set.add(redirected_depedia_url)
        else:
            redirect_wikipedia = get_redirected_url_from_live_wikipedia(url)
            dbpedia_url = 'http://dbpedia.org/resource/' + redirect_wikipedia[starting_length:]
            redirected_depedia_url = redirects.get(dbpedia_url, dbpedia_url)
            if redirected_depedia_url in resources:
                new_set.add(redirected_depedia_url)
            else:
                print('url not in dbpedia: {} based on wikipedia url: {}'.format(redirected_depedia_url, url))
    if len(new_set) > 0:
        return list(new_set)
    else:
        if not_possibel_is_conatined:
            return ['not:possible']
        else:
            return []


def postprocess_file_and_keep_only_valid_links(in_path, out_path):
    redirects = read_redirects()
    all_pages = read_labels_resource_set('labels_en.ttl', redirects)
    all_categories = read_labels_resource_set('category_labels_en.ttl', redirects)

    with open(in_path) as in_file, open(out_path, "w", newline='') as out_file:
        reader = csv.reader(in_file)
        writer = csv.writer(out_file)
        for row in reader:

            new_instance_pages = check_page_or_category(json.loads(row[19]), redirects, all_pages, 'https://en.wikipedia.org/wiki/', 30)
            new_instance_categories = check_page_or_category(json.loads(row[20]), redirects, all_categories, 'https://en.wikipedia.org/wiki/Category:', 30)
            new_class_pages = check_page_or_category(json.loads(row[21]), redirects, all_pages, 'https://en.wikipedia.org/wiki/', 30)
            new_class_categories = check_page_or_category(json.loads(row[22]), redirects, all_categories, 'https://en.wikipedia.org/wiki/Category:', 30)

            writer.writerow(row[:19] + [json.dumps(new_instance_pages), json.dumps(new_instance_categories), json.dumps(new_class_pages), json.dumps(new_class_categories)])


if __name__ == "__main__":
    set_csv_field_size()
    #translate_files('webisa_1_sentence_sample_1000.csv','webisa_1_sentence_mturk_results.csv', 'webisa_1_sentence_raw_results.csv')
    postprocess_file_and_keep_only_valid_links('webisa_1_sentence_raw_results.csv', 'webisa_1_sentence_results.csv')
    #print(get_redirected_url_from_live_wikipedia('https://en.wikipedia.org/wiki/yes'))
