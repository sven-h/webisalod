import csv
import numpy as np
from utilwebisadb import set_csv_field_size


def generate_final_dataset_all(full_file_path, prediction_path, out_path):
    correct_relation_to_uncertainty = {}
    incorrect_relation_to_uncertainty = {}
    with open(prediction_path) as prediction_file:
        prediction_reader = csv.reader(prediction_file)
        for i, row in enumerate(prediction_reader):
            if row[76] == 'yes':
                correct_relation_to_uncertainty[int(float(row[73]))] = float(row[75])
            if row[76] == 'no':
                incorrect_relation_to_uncertainty[int(float(row[73]))] = float(row[75])
    print(len(correct_relation_to_uncertainty))
    with open(full_file_path) as full_file, open(out_path, 'w', newline='') as outfile:
        reader = csv.reader(full_file)
        writer = csv.writer(outfile)
        for row in reader:
            uncertainty = correct_relation_to_uncertainty.get(int(row[0]), None)
            if uncertainty is not None:
                writer.writerow(row + ['yes', uncertainty])
            uncertainty = incorrect_relation_to_uncertainty.get(int(row[0]), None)
            if uncertainty is not None:
                writer.writerow(row + ['no', uncertainty])#uncertainty is always for the positive class
    print('min positive theshold: {}'.format(min(correct_relation_to_uncertainty.values())))
    print('max negative theshold: {}'.format(max(incorrect_relation_to_uncertainty.values())))



def generate_final_dataset(full_file_path, prediction_path, out_path):
    correct_relation_to_uncertainty = {}
    with open(prediction_path) as prediction_file:
        prediction_reader = csv.reader(prediction_file)
        for i, row in enumerate(prediction_reader):
            if row[76] == 'yes':
                correct_relation_to_uncertainty[int(float(row[73]))] = float(row[75])
    print(len(correct_relation_to_uncertainty))
    with open(full_file_path) as full_file, open(out_path, 'w', newline='') as outfile:
        reader = csv.reader(full_file)
        writer = csv.writer(outfile)
        for row in reader:
            uncertainty = correct_relation_to_uncertainty.get(int(row[0]), None)
            if uncertainty is not None:
                writer.writerow(row + ['yes', uncertainty])

def generate_bins(prediction_path):
    yes_scores = []
    with open(prediction_path) as prediction_file:
        prediction_reader = csv.reader(prediction_file)
        for i, row in enumerate(prediction_reader):
            try:
                yes_scores.append(float(row[75]))
            except ValueError:
                pass
    np_yes_scores = np.array(yes_scores)
    print(np.histogram(np_yes_scores, bins=np.linspace(0,1,num=21)))

if __name__ == "__main__":
    #set_csv_field_size()
    #generate_final_dataset_all('webisa_1_with_sent.csv', 'webisa_1_with_sent_analysis/prediction.csv', 'webisa_1_final.csv')
    #generate_final_dataset('webisa_1_with_sent.csv', 'webisa_1_with_sent_analysis/prediction.csv', 'webisa_1_final.csv')
    generate_bins('webisa_1_with_sent_analysis/prediction.csv')
