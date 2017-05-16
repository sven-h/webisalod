import csv
import sys
import operator
import datetime
import codecs


def set_csv_field_size():
    maxInt = sys.maxsize
    decrement = True
    while decrement:
        decrement = False
        try:
            csv.field_size_limit(maxInt)
        except OverflowError:
            maxInt = int(maxInt / 10)
            decrement = True
    return maxInt

def get_ids_in_range(prov_ids, min_id, max_id):
    prov_id_set = set()
    for x in prov_ids.split(';'):
        if x:
            prov_id = int(x)
            if prov_id >= min_id and prov_id <= max_id:
                prov_id_set.add(prov_id)
    return list(prov_id_set)

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def min_max_mean_variance(numbers):
    if len(numbers) == 0:
        return [0,0,0,0]
    calc_mean = float(sum(numbers)) / len(numbers)
    calc_variance = float(sum([(xi - calc_mean) ** 2 for xi in numbers])) / len(numbers)
    calc_min = numbers[0]
    calc_max = numbers[0]
    for number in numbers[1:]:
        if number > calc_max:
            calc_max = number
        if number < calc_min:
            calc_min = number
    return [calc_min, calc_max, calc_mean, calc_variance]


def read_labels_dict(file_path, redirects):
    labels = {}
    with codecs.open(file_path, 'r', encoding='utf8') as file:
        for line in file:
            if line[0] != '<':
                print('line did not start with <: {}'.format(line))
                continue
            subject = line[1:line.index('>')]
            label = line[line.index('"') + 1:line.rindex('"')]
            redirected_subject = redirects.get(subject, subject)
            labels[redirected_subject] = label
    return labels

def read_labels_resource_set(file_path, redirects):
    print("{} - start loading {}".format(datetime.datetime.now(), file_path))
    resources = set()
    with codecs.open(file_path, 'r', encoding='utf8') as file:
        for i, line in enumerate(file):
            if line[0] != '<':
                print('line did not start with <: {}'.format(line))
                continue
            subject = line[1:line.index('>')]
            resources.add(redirects.get(subject, subject))
            if i % 100000 == 0:
                print("{} - {} imported".format(datetime.datetime.now(), i))
            #if i > 100000:
            #    break
    print("{} - finished loading {}".format(datetime.datetime.now(), file_path))
    return resources

def read_redirects():
    print("{} - start loading redirects".format(datetime.datetime.now()))
    redirects = {}
    with codecs.open('transitive_redirects_en.ttl', 'r', encoding='utf8') as file:
        for i, line in enumerate(file):
            if line[0] != '<':
                continue
            subject = line[1:line.index('>')]
            redirect = line[line.rindex('<') + 1:line.rindex('>')]
            redirects[subject] = redirect
            if i % 100000 == 0:
                print("{} - {} imported".format(datetime.datetime.now(), i))
            #if i > 100000:
            #    break
    print("{} - finished loading redirects".format(datetime.datetime.now()))
    return redirects





### functions for search_start_end_index_in_sentence

def search_next_whitespace(str, index):
    whitespace_index = str.find(' ', index)
    if whitespace_index == -1:
        return len(str)
    return whitespace_index


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)


def search_one_token_reducing_suffix(sent, token):
    max_reduce = len(token) / 2
    current_length = len(token)
    while True:
        instance_index = list(find_all(sent,token[:current_length]))
        if len(instance_index) > 0:
            return instance_index
        if current_length < max_reduce:
            return []
        current_length -= 1


def is_match(start_end_pos, sent, token):
    score_list = [0] * len(start_end_pos)  # contains 1 if token is in specified range, 0 otherwise
    max_reduce = len(token) / 2
    current_length = len(token)
    while True:
        for i, (start, end) in enumerate(start_end_pos):
            if sent.find(token[:current_length], start, end) != -1:
                score_list[i] = 1
        if sum(score_list) > 0 or current_length < max_reduce:
            return score_list
        current_length -= 1

def find_one_maximum(my_list):
    max_value = 0
    max_index = 0
    for i, item in enumerate(my_list):
        if item > max_value:
            max_value = item
            max_index = i
        elif item == max_value:
            #we have two
            return -1
    return max_index


def search_correct_position(sent, list_min_len_2, reverse_direction = False):
    possible_indices = []
    pos = 0
    if reverse_direction:
        list_min_len_2 = list(reversed(list_min_len_2))
    for i, item in enumerate(list_min_len_2):
        possible_indices = search_one_token_reducing_suffix(sent, item)
        if len(possible_indices) > 0:
            pos = i
            break
    if len(possible_indices) == 0:
        return -1
    elif len(possible_indices) == 1:
        return possible_indices[0]
    else:

        start_end_pos = list(zip(possible_indices[:], possible_indices[1:]))
        if reverse_direction:
            start_end_pos = [(0,possible_indices[0])] + start_end_pos
        else:
            start_end_pos.append((possible_indices[-1], len(sent)))

        score_list = [0] * len(start_end_pos)
        for token in list_min_len_2[pos + 1:]:
            score_list = [one + two for (one, two) in zip(score_list,is_match(start_end_pos, sent, token))]
            max_index, max_value = max(enumerate(score_list), key=operator.itemgetter(1))
            how_often_max = score_list.count(max_value)
            if how_often_max == 1:
                if reverse_direction:
                    return start_end_pos[max_index][1]
                return start_end_pos[max_index][0]
        # can't get better choose one of the best
        max_index, max_value = max(enumerate(score_list), key=operator.itemgetter(1))
        if reverse_direction:
            return start_end_pos[max_index][1]
        return start_end_pos[max_index][0]



def search_start_end_index_in_sentence(sent, np):
    """ Already lowercased parameters. Returns start and end indices."""

    nps = [x for x in np.split() if x]
    if len(nps) == 0:
        return (-1, -1)
    elif len(nps) == 1:
        indices = search_one_token_reducing_suffix(sent, np)
        if len(indices) > 0:
            return (indices[0], search_next_whitespace(sent, indices[0]))
        else:
            return (-1, -1)
    else:
        # search start:
        start = search_correct_position(sent, nps)
        end = search_correct_position(sent, nps, True)
        if end != -1:
            end = search_next_whitespace(sent, end)
        return (start,end)