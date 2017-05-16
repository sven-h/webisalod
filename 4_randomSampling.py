import random

def write_random_samples_huge_files(source, target, k):
    # http://metadatascience.com/2014/02/27/random-sampling-from-very-large-files/
    with open(source, 'r') as f, open(target, "w", newline='') as out:
        linecount = sum(1 for line in f)
        print("finished counting {} lines".format(linecount))
        f.seek(0)
        random_linenos = sorted(random.sample(range(linecount), k), reverse=True)
        lineno = random_linenos.pop()
        for n, line in enumerate(f):
            if n == lineno:
                out.write(line)
                if len(random_linenos) > 0:
                    lineno = random_linenos.pop()
                else:
                    break


if __name__ == "__main__":
    #for i in [20,10,5,3,2,1,0]:
    #    write_random_samples_huge_files('webisa_{}.csv'.format(i), 'webisa_{}_sample_500.csv'.format(i))
    write_random_samples_huge_files('webisa_1.csv', 'webisa_1_sentence_sample_1000.csv', 1000)