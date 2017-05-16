import csv
import sys
import time
import datetime
from collections import defaultdict
from struct import *
import bisect
from utilwebisadb import set_csv_field_size

def load_dicts_from_csv(csv_file):
    node_to_node_id = {}
    node_id_to_succ_ids_and_edge_info = defaultdict(list)
    i = 0
    with open(csv_file) as f:
        reader = csv.reader((line.replace('\0','') for line in f))
        for row in reader:
            instance = (row[6], row[7], row[8])
            clazz = (row[9], row[10], row[11])
            if instance == clazz: # remove all reflexive edges because these cycles are always true i.e. city is a city, action is a action, answer is a answer
                continue

            instance_id = node_to_node_id.get(instance)
            if instance_id == None:
                instance_id = i
                node_to_node_id[instance] = i
                i += 1

            clazz_id = node_to_node_id.get(clazz)
            if clazz_id == None:
                clazz_id = i
                node_to_node_id[clazz] = i
                i += 1

            node_id_to_succ_ids_and_edge_info[instance_id].append(pack('LLL', clazz_id, int(row[0]), int(float(row[3])))) # neighbour id, edge id, edge/relation frequency
    return node_to_node_id.values(), node_id_to_succ_ids_and_edge_info


def move(element, first_set, second_set):
    first_set.remove(element)
    second_set.add(element)

#http://stackoverflow.com/questions/26840413/insert-a-custom-object-in-a-sorted-list
#http://stackoverflow.com/questions/27672494/using-bisect-insort-with-key
class MyElement:
    def __init__(self, id, freq, index):
        self.id = id
        self.freq = freq
        self.index = index

    def __lt__(self, other):
        return self.freq < other.freq

    def __repr__(self):
        return 'MyElement({}, {}, {})'.format(self.id, self.freq, self.index)

class Min_Max_of_Sliced_List:
    def __init__(self):
        self.list = []
        self.sortedList = []

    def push(self, id, freq):
        if id == None:
            return
        self.list.append((id, freq))
        bisect.insort_left(self.sortedList, MyElement(id, freq, len(self.list)))

    def pop(self):
        if len(self.list) == 0:
            return
        pop_id, pop_freq = self.list.pop()
        #delete in sorted list
        i = bisect.bisect_left(self.sortedList, MyElement(0, pop_freq, 0))
        while True:
            if self.sortedList[i].id == pop_id:
                del self.sortedList[i]
                break
            i += 1

    def find_min_max_from_index(self, index):
        min, max = 0,0
        for item in self.sortedList:
            if item.index >= index:
                min = item
                break
        for item in reversed(self.sortedList):
            if item.index >= index:
                max = item
                break
        return min.id, min.freq, max.id, max.freq




def dfs_iterative(nodes, succ, out_file, log): #G):
    white = set()  # unvisited
    gray = set()  # on the stack
    black = set()  # = finished (we backtracked from it, seen everywhere we can reach from it)

    total_length = len(nodes)
    for node in nodes:
        white.add(node)

    log_counter = 0
    with open(out_file, "w") as out:
        while len(white) > 0:
            start_node = next(iter(white))
            # true means enter function , false means returning from the function/recusrion see
            # http://stackoverflow.com/questions/21952770/how-to-convert-this-non-tail-recursion-function-to-a-loop-or-a-tail-recursion-ve
            stack = [(False, start_node, (None, None)), (True, start_node, (None, None))]
            call_stack = []
            call_stack_dict = {}
            sorted_stack = Min_Max_of_Sliced_List()

            while stack:
                (enter_or_return, current, (current_edge_id, current_edge_freq)) = stack.pop()
                if current in black:#already observed
                    continue
                if enter_or_return: #entering the function
                    move(current, white, gray)
                    call_stack.append(current)
                    call_stack_dict[current] = len(call_stack) - 1
                    sorted_stack.push(current_edge_id, current_edge_freq)
                    for packed in succ[current]:
                        neighbor, edge_id, freq = unpack('LLL',packed)
                        if neighbor in white:
                            stack.append((False, neighbor, (None, None)))
                            stack.append((True, neighbor, (edge_id, freq)))
                        elif neighbor in gray:
                            #path = call_stack[call_stack_dict[neighbor]:]
                            #path.append(neighbor)

                            sorted_stack.push(edge_id,freq)
                            min_id, min_freq,max_id,max_freq = sorted_stack.find_min_max_from_index(call_stack_dict[neighbor] + 1)
                            sorted_stack.pop()

                            out.write('no,{}\nyes,{}\n'.format(min_id, max_id))

                else: #returning back from the function
                    move(current, gray, black)
                    del call_stack_dict[call_stack.pop()]
                    sorted_stack.pop()
                    log_counter += 1
                    log.write("{} - out {}/{}\n".format(datetime.datetime.now(), log_counter, total_length))


def calc_cycles(log_file, out_file, dict_file):
    with open(log_file, "w") as log:
        startTime = time.time()
        nodes, succ= load_dicts_from_csv(dict_file)
        log.write('finished loading graph in {} s\n'.format(time.time() - startTime))

        startTime = time.time()
        dfs_iterative(nodes, succ, out_file, log)
        log.write('finished processing graph in {} s\n'.format(time.time() - startTime))


def post_process_cycles(full_file, cycle_file, out_file):
    yes_set = set()
    no_set = set()
    with open(cycle_file) as f:
        for row in csv.reader(f):
            if row[0] == 'no':
                no_set.add(int(row[1]))
            elif row[0] == 'yes':
                yes_set.add(int(row[1]))

    #remove all ids which occur in both sets
    only_yes_set = yes_set.difference(no_set)
    only_no_set = no_set.difference(yes_set)

    with open(full_file) as full, open(out_file, "w", newline='') as out:
        full_reader = csv.reader(full)
        out_writer = csv.writer(out)

        for row in full_reader:
            if int(row[0]) in only_yes_set:
                out_writer.writerow(row + ['yes'])
            elif int(row[0]) in only_no_set:
                out_writer.writerow(row + ['no'])


if __name__ == "__main__":
    set_csv_field_size()
    for i in [1]:  # 20,10,5,3,2,1,0
        calc_cycles('webisa_{}_cycles_log.txt'.format(i), 'webisa_{}_cycles_raw.csv'.format(i), 'webisa_{}.csv'.format(i))
        post_process_cycles('webisa_{}.csv'.format(i), 'webisa_{}_cycles_raw.csv'.format(i), 'webisa_{}_cycles_results.csv'.format(i))