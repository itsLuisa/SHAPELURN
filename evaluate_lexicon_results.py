from collections import defaultdict

"""
This file contains the functions to extract the learnt rules and their weights for the end of level 3 from the weight.csv files.
Running overview_rules() creates a file with all input words paired with all rules and the learnt weights for each participant
and the information if the rule was still present at the end of the game or deleted earlier
"""

def overview_rules(weight_files, output_file):
    """
    :param weight_files: list(tuples), a list of tuples where each first entry of a tuple is the name of one evaluation file
                        and the second entry is the name under which the data for this participant should be stored (i.e. the subject ID)
    :param output_file: the name for the file that should be created
    """
    complete_rule_set = process_all_rules()

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("Subject\tWord\tRule\tCategory\tWeight\tDeleted\n")

    for file in weight_files:
        weight_f = file[0]
        subject = file[1]
        words, mappings = read_weights(weight_f)

        complete = get_rules(mappings[3], complete_rule_set)

        with open(output_file, "a", encoding="utf-8") as out:
            for word in complete:
                for (rule, category, weight, deleted) in complete[word]:
                    out.write(subject + "\t" + word + "\t" + rule + "\t" + category + "\t" + str(weight) + "\t" + deleted + "\n")



def read_weights(weight_file):
    """
    reads in the evaluation file and extracts the used words and the rules and learnt weights
    :param weight_file: an weight file
    :return: a dictionary where each key is the level and the value a set of all words that were in the lexicon at the end of this level
             a dictionary where each key is the level and the value is again a dictionary with one entry for each word and
            as value the list with all tuples (rule, weight) for this word
    """
    with open(weight_file, "r", encoding="utf-8") as f:
        header = f.readline()
        words = defaultdict(set)
        mappings = defaultdict(dict)
        for line in f:
            infos = line.split("\t")
            level = int(infos[0])
            weight = float(infos[2])
            tuple = infos[1]
            tuple = tuple[1:]
            tuple = tuple[:-1]

            pair = ""
            if infos[3] == '-\n':
                helper_list = tuple.split(" ")
                helper_list = helper_list[:-1]

                helper_str = " ".join(helper_list)
                pair += helper_str[:-1]
            else:
                helper_str = tuple
                pair += helper_str

            pair = pair[:-1]
            pair = pair[1:]
            pair = pair.replace("', '", "'\t'")

            pair_list = pair.split("\t")
            removed_double = []
            for p in pair_list:
                removed_double.append(p.replace("'", ""))

            word = removed_double[0]
            rule = removed_double[1]

            if word == '' or word == "top":
                continue
            else:
                words[level].add(word)
                try:
                    mappings[level][word].append((rule, weight))
                except:
                    mappings[level][word] = [(rule, weight)]
        return words, mappings



def get_rules(lex, complete_rule_set):
    """
    backtraces which rules were actually still present at the end of the level to which lex belongs by:
    labelling all rules with weight smaller or equal to -0.1 as deleted
    adding all rules that were not in the dictionary, e.g. that were not changed by the learning and hence are still 0
    labelling all rules with a weight equal or smaller than 0 as deleted if one of the rules for the word reaches the upper threshold 1

    :param lex: a dictionary with one entry for each word and as value the list with all tuples (rule, weight) for this word
    :param complete_rule_set: the dictionary with all rules as returned by process_all_rules()
    """
    processed_lex = dict()
    for word in lex:
        processed_lex[word] = []
        all_r = complete_rule_set.copy()
        upper_threshold = False

        for entry in lex[word]:
            category = all_r[entry[0]]
            del all_r[entry[0]]
            weight = entry[1]
            deleted = 'No'
            if weight <= -0.1:
                deleted = 'Yes'
            processed_lex[word].append((entry[0], category, entry[1], deleted))

            if weight >= 1:
                upper_threshold = True

        # add potentially missing rules
        for remaining_r in all_r:
            processed_lex[word].append((remaining_r, all_r[remaining_r], 0, 'No'))

        if upper_threshold:
            for i, entry in enumerate(processed_lex[word]):
                weight = entry[2]
                if weight <= 0:
                    processed_lex[word][i] = (entry[0], entry[1], entry[2], 'Yes')

    return processed_lex



def process_all_rules():
    """
    :return: creates a dictionary with an entry for each rule in all_rules below
    the keys are the lexical rules and the value is the corresponding category
    """
    complete_rule_set = dict()
    for (category, rule) in all_rules:
        complete_rule_set[rule] = category

    return complete_rule_set



all_rules = [
    ('B', 'block_filter([], allblocks)'),
    ('B', 'block_filter([lambda b: b.shape=="rectangle"], allblocks)'),
    ('B', 'block_filter([(lambda b: b.shape == "triangle")], allblocks)'),
    ('B', 'block_filter([(lambda b: b.shape == "circle")], allblocks)'),
    ('N','range(1,17)'),
    ('N','[1]'),
    ('N','[2]'),
    ('N','[3]'),
    ('C', 'green'),
    ('C', 'yellow'),
    ('C', 'blue'),
    ('C', 'red'),
    ('POS', 'under'),
    ('POS', 'over'),
    ('POS', 'next'),
    ('POS', 'left'),
    ('POS', 'right'),
    ('CONJ', 'und'),
    ('CONJ', 'oder'),
    ('CONJ', 'xoder')

]

if __name__ == "__main__":
    overview_rules([("./Daten/Bob_weights.csv", "P1_Eng"), ("./Daten/Etienne_weights.csv", "P2_Eng"), ("./Daten/Patty S1_weights.csv", "P3_Ger")], "./Daten/results_learning.csv")
    #overview_rules([("./Daten/Patty S1_weights.csv", "P3_Ger")], "./Daten/test.csv")

