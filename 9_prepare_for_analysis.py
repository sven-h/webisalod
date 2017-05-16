import csv
import json
import datetime
from utilwebisadb import set_csv_field_size, mean, search_next_whitespace, min_max_mean_variance


pattern_ids = ['p1', 'p2', 'p3a', 'p4', 'p5', 'p6', 'p7', 'p8a', 'p8b', 'p8c', 'p8d', 'p10', 'p11','p12a','p12b', 'p12c',
               'p13', 'p14', 'p15a', 'p15b', 'p16','p20a', 'p20b', 'p20c', 'p20d', 'p21a', 'p21b', 'p21c', 'p21d',
               'p22a', 'p22b', 'p23a', 'p23b', 'p23c','p23d', 'p23e', 'p24', 'p25', 'p26', 'p27a', 'p27b', 'p28a', 'p28b', 'p28c', 'p28d',
               'p29a', 'p29c', 'p30a', 'p30b', 'p31a', 'p31b', 'p34', 'p36', 'p37', 'p38', 'p39','p42', 'p43']#58



def search_lemma_in_sentence(sent, lemma):
    max_reduce = len(lemma)/2
    current_length = len(lemma)
    while True:
        instance_index = sent.find(lemma[:current_length])
        if instance_index != -1:
            return instance_index
        if current_length < max_reduce:
            print("Not found {} in {}".format(lemma, sent))
            return -1
        current_length -= 1


def calculate_token_diffs_in_sentence(row):
    instance_lemma = row[7].lower()
    class_lemma = row[10].lower()

    sentences = json.loads(row[14])
    token_diffs = []
    for (id, sentence, pld) in sentences:
        sent_lower = sentence.lower()
        instance_index = search_lemma_in_sentence(sent_lower, instance_lemma)
        class_index = search_lemma_in_sentence(sent_lower, class_lemma)

        start = min(instance_index, class_index)
        end = max(instance_index, class_index)
        if start == -1 or end == -1:
            continue
        end = search_next_whitespace(sent_lower, end)
        small_sent = sent_lower[start:end]
        small_sent_tokens = [x for x in small_sent.split() if x]
        token_diffs.append(len(small_sent_tokens))
    return min_max_mean_variance(token_diffs)


def prepare_gold_standard_for_analysis(results_file, analysis_file):
    with open(results_file) as results, open(analysis_file, "w", newline='') as out:
        results_reader = csv.reader(results)
        out_writer = csv.writer(out)
        out_writer.writerow(['label', 'frequency', 'pidspread', 'pldspread',
                             'sent_diff_min', 'sent_diff_max', 'sent_diff_avg', 'sent_diff_variance',
                             'instance_token_count', 'instance_avg_token_length', 'instance_has_pre', 'instance_has_post',
                             'class_token_count', 'class_avg_token_length', 'class_has_pre', 'class_has_post']
                            + pattern_ids)
        for row in results_reader:
            if row[15] != 'yes' and row[15] != 'no':
                continue

            pids = set([x for x in row[12].split(';') if x])
            instance_tokens = [x for x in row[1].split() if x]
            class_tokens = [x for x in row[2].split() if x]

            sentence_diffs = calculate_token_diffs_in_sentence(row)
            instance_info = [len(instance_tokens), mean([len(token) for token in instance_tokens]),int(bool(row[6].strip())), int(bool(row[8].strip()))]
            class_info =    [len(class_tokens),    mean([len(token) for token in class_tokens]),   int(bool(row[9].strip())), int(bool(row[11].strip()))]
            pattern_info =  [int(pattern in pids) for pattern in pattern_ids]

            out_writer.writerow([row[15]] + row[3:6] + sentence_diffs + instance_info + class_info + pattern_info)


def prepare_gold_standard_for_analysis_with_weights(results_file, analysis_file):
    with open(results_file) as results, open(analysis_file, "w", newline='') as out:
        results_reader = csv.reader(results)
        out_writer = csv.writer(out)
        out_writer.writerow(['label','weight','frequency', 'pidspread', 'pldspread',
                             'sent_diff_min', 'sent_diff_max', 'sent_diff_avg', 'sent_diff_variance',
                             'instance_token_count', 'instance_avg_token_length', 'instance_has_pre', 'instance_has_post',
                             'class_token_count', 'class_avg_token_length', 'class_has_pre', 'class_has_post']
                            + pattern_ids)
        for row in results_reader:
            label = 'uncertain'
            weight = 0.0
            yes = int(row[16])
            uncertain = int(row[17])
            no = int(row[18])
            all = yes + uncertain + no
            if yes > no:
                label = 'yes'
                weight = float(yes / all)
            elif no > yes:
                label = 'no'
                weight = float(no / all)
            else:
                print('continue: yes {} no {} uncertain {}'.format(yes, no, uncertain))
                continue

            pids = set([x for x in row[12].split(';') if x])
            instance_tokens = [x for x in row[1].split() if x]
            class_tokens = [x for x in row[2].split() if x]

            sentence_diffs = calculate_token_diffs_in_sentence(row)
            instance_info = [len(instance_tokens), mean([len(token) for token in instance_tokens]),int(bool(row[6].strip())), int(bool(row[8].strip()))]
            class_info =    [len(class_tokens),    mean([len(token) for token in class_tokens]),   int(bool(row[9].strip())), int(bool(row[11].strip()))]
            pattern_info =  [int(pattern in pids) for pattern in pattern_ids]

            out_writer.writerow([label, weight] + row[3:6] + sentence_diffs + instance_info + class_info + pattern_info)


def prepare_unlabeled_for_analysis(in_path, out_path):
    with open(in_path) as in_file, open(out_path, "w", newline='') as out_file:
        results_reader = csv.reader((line.replace('\0', '') for line in in_file))
        out_writer = csv.writer(out_file)
        out_writer.writerow(['id', 'frequency', 'pidspread', 'pldspread',
                             #'sent_diff_min', 'sent_diff_max', 'sent_diff_avg', 'sent_diff_variance',
                             'instance_token_count', 'instance_avg_token_length', 'instance_has_pre', 'instance_has_post',
                             'class_token_count', 'class_avg_token_length', 'class_has_pre', 'class_has_post']
                            + pattern_ids)

        for i, row in enumerate(results_reader):
            pids = set([x for x in row[12].split(';') if x])
            instance_tokens = [x for x in row[1].split() if x]
            class_tokens = [x for x in row[2].split() if x]

            #sentence_diffs = calculate_token_diffs_in_sentence(row)
            instance_info = [len(instance_tokens),mean([len(token) for token in instance_tokens]),int(bool(row[6].strip())),int(bool(row[8].strip()))]
            class_info = [len(class_tokens), mean([len(token) for token in class_tokens]),int(bool(row[9].strip())), int(bool(row[11].strip()))]
            pattern_info = [int(pattern in pids) for pattern in pattern_ids]

            #out_writer.writerow([row[0]] + row[3:6] + sentence_diffs + instance_info + class_info + pattern_info)
            out_writer.writerow([row[0]] + row[3:6] + instance_info + class_info + pattern_info)

            if i % 1000000 == 0:
                print("{} - {}".format(datetime.datetime.now(), i))


if __name__ == "__main__":
    set_csv_field_size()
    #prepare_for_analysis('webisa_0_sample_results.csv','webisa_0_sample_results_for_analysis.csv')
    #for i in [1]: #[20, 10, 5, 3, 2, 1, 0]:
    #    prepare_for_analysis('webisa_{}_cycles_results.csv'.format(i), 'webisa_{}_cycles_results_for_analysis.csv'.format(i))
        #prepare_for_analysis_with_weights('webisa_{}_sample_results.csv'.format(i), 'webisa_{}_sample_results_for_analysis_with_weights.csv'.format(i))
    #    prepare_for_analysis('webisa_{}_sample_results.csv'.format(i), 'webisa_{}_sample_results_for_analysis_sentence_feature.csv'.format(i))

    #prepare_gold_standard_for_analysis('webisa_0_sample_results_with_sent.csv', 'webisa_0_sample_results_analysis.csv')
    #prepare_gold_standard_for_analysis('webisa_1_cycles_results_with_sent.csv', 'webisa_1_cycles_results_analysis.csv')
    #prepare_unlabeled_for_analysis('webisa_1_with_sent.csv', 'webisa_1_with_sent_analysis.csv')
    prepare_unlabeled_for_analysis('webisa_0.csv', 'webisa_0_analysis.csv')

