# WebIsALOD: Providing Hypernymy Relations extracted from the Web as Linked Open Data

This repository contains all the code used for the WebIsALOD paper.

## Abstract
Hypernymy relations are an important asset in many applications,and a central ingredient to Semantic Web ontologies. 
The IsA database is a large collection of such hypernymy relations extracted from the Common Crawl. 
In this paper, we introduce WebIsALOD, a Linked Open Data version of the IsA database, containing 11.7M hyernymy relations, 
each provided with rich provenance information. As the original dataset contained more than 80% wrong, noisy extractions, we run a machine learning algorithm to assign confdence scores to the individual statements.


## Structure of the files

All files starting with a number are files to generate the csv files, mappings and nquad generation.
The files starting with mTurk are HTML surveys used to generate the ground truth.
Files with the name "webisa_{threshold}_sample_results" are the samples from corresponding thresholds together with the majority vote and the answer of each worker.
webisa_1_sentence_results.csv conatins the results from the mapping to Wikipedia pages and categories.


Most of the csv files are structed as follows:
1. id
2. instance
3. class
4. frequency
5. pidspread
6. pldspread
7. ipremod
8. ilemma
9. ipostmod
10. cpremod
11. clemma
12. cpostmod
13. pids
14. plds
15. provids
16. majority voting
17. yes (counts)
18. uncertain (counts)
19. no (counts)
20. mapping instance to dbpedia page (json array)
21. mapping instance to dbpedia category (json array)
22. mapping class to dbpedia page (json array)
23. mapping class to dbpedia category (json array)
24. mapping instance to yago (string)
25. mapping class to yago (string)