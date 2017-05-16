import csv
from collections import defaultdict, Counter
from utilwebisadb import set_csv_field_size


def get_map_id_to_list_of_answer(results):
    id_to_list_of_answer = defaultdict(list)
    with open(results) as _results_file:
        results_reader = csv.reader(_results_file)

        header = next(results_reader)
        index_list = []
        relation_id_list = []
        for i, item in enumerate(header):
            if item.startswith("Answer."):
                index_list.append(i)
                relation_id_list.append(int(item.split(".")[1]))

        for row in results_reader:
            for i, index in enumerate(index_list):
                if row[index]:
                    relation_id = relation_id_list[i]
                    id_to_list_of_answer[relation_id].append(row[index])

    return id_to_list_of_answer


def get_majority_voting(list_of_votings):
    if list_of_votings.count("yes") > 4:
        return "yes"
    elif list_of_votings.count("no") > 4:
        return "no"
    else:
        return "uncertain"



def translate_files(samples,mturk_results, out):
    id_to_list_of_answer = get_map_id_to_list_of_answer(mturk_results)

    majority_list = []
    with open(samples) as samples_file, open(out, "w", newline='') as out_file:
        sample_reader = csv.reader(samples_file)
        writer = csv.writer(out_file)

        for row in sample_reader:
            anwers = id_to_list_of_answer[int(row[0])]
            majority = get_majority_voting(anwers)
            majority_list.append(majority)
            writer.writerow(row + [majority, anwers.count("yes"), anwers.count("uncertain"), anwers.count("no")])
    print("file: {} - counts: {}".format(samples, Counter(majority_list)))

if __name__ == "__main__":
    set_csv_field_size()
    for i in [0,1,2,3,5,10,20]:
        translate_files('webisa_{}_sample_500.csv'.format(i), 'webisa_{}_sample_mturk_results.csv'.format(i), 'webisa_{}_sample_results.csv'.format(i))