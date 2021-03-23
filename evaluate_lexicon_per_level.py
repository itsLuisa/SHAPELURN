from collections import defaultdict

"""
This file contains the functions to extract the learnt rules and their weights for each level from the weight.csv files.
Running evaluate_lexicon creates a file with the number of rules and number of words for each of the first three levels.
And additionally computes the average number of rules per word for each level. This is done for each participant.
The numbers for Level 3 are also the overall numbers
"""

def evaluate_lexicon(weight_files, output_file):
    """
    :param weight_files: list(tuples), a list of tuples where each first entry of a tuple is the name of one evaluation file
                        and the second entry is the name under which the data for this participant should be stored (i.e. the subject ID)
    :param output_file: the name for the file that should be created
    """
    complete_rule_set = process_all_rules()

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("Subject\tLevel1_N_Rules\tLevel1_N_Words\tLevel1_averaged\tLevel2_N_Rules\tLevel2_N_Words\tLevel2_averaged\tLevel3_N_Rules\tLevel3_N_Words\tLevel3_averaged\n")

    for file in weight_files:
        weight_f = file[0]
        subject = file[1]
        words, mappings = read_weights(weight_f)

        processed_lex = dict()
        for l in range(3):
            processed_lex[l+1] = process_rules(mappings[l+1], complete_rule_set)

        l1_n_words = 0
        l1_n_rules = 0
        for word in processed_lex[1]:
            l1_n_words += 1
            for rule in processed_lex[1][word]:
                l1_n_rules += 1
        l1_aver = l1_n_rules / l1_n_words
        l1_aver = round(l1_aver, 2)

        l2_n_words = 0
        l2_n_rules = 0
        for word in processed_lex[2]:
            l2_n_words += 1
            for rule in processed_lex[2][word]:
                l2_n_rules += 1
        l2_aver = l2_n_rules / l2_n_words
        l2_aver = round(l2_aver, 2)

        l3_n_words = 0
        l3_n_rules = 0
        for word in processed_lex[3]:
            l3_n_words += 1
            for rule in processed_lex[3][word]:
                l3_n_rules += 1
        l3_aver = l3_n_rules / l3_n_words
        l3_aver = round(l3_aver,2)

        with open(output_file, "a", encoding="utf-8") as out:
            out.write(subject + "\t" + str(l1_n_rules) + "\t" + str(l1_n_words) + "\t" + str(l1_aver) + "\t"
                      + str(l2_n_rules) + "\t" + str(l2_n_words) + "\t" + str(l2_aver) + "\t"
                      + str(l3_n_rules) + "\t" + str(l3_n_words) + "\t" + str(l3_aver) + "\n")





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



def process_rules(lex, complete_rule_set):
    """
    backtraces which rules were actually still present at the end of the level to which lex belongs by:
    removing all rules with weight smaller or equal to -0.1
    adding all rules that were not in the dictionary, e.g. that were not changed by the learning and hence are still 0
    removing all rules with a weight equal or smaller than 0 if one of the rules for the word reaches the upper threshold 1

    :param lex: a dictionary with one entry for each word and as value the list with all tuples (rule, weight) for this word
    :param complete_rule_set: the dictionary with all rules as returned by process_all_rules()
    """
    processed_lex = dict()
    for word in lex:
        processed_lex[word] = []
        upper_threshold = False
        all_r = complete_rule_set.copy()

        # remove rules with weight below or equal -0.1
        for entry in lex[word]:
            del all_r[entry[0]]
            weight = entry[1]
            if weight <= -0.1:
                continue
            else:
                processed_lex[word].append(entry)
            if weight >= 1:
                upper_threshold = True

        # add potentially missing rules
        for remaining_r in all_r:
            processed_lex[word].append((remaining_r, 0))

        # delete rules equal or below 0 if one of the rules has weight 1 or higher
        if upper_threshold:
            to_delete =[]
            for entry in processed_lex[word]:
                weight = entry[1]
                if weight <= 0:
                    to_delete.append(entry)
            for t_d in to_delete:
                processed_lex[word].remove(t_d)
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
    evaluate_lexicon([("./Daten/Bob_weights.csv", "P1_Eng"), ("./Daten/Etienne_weights.csv", "P2_Eng"), ("./Daten/Patty S1_weights.csv", "P3_Ger")], "./Daten/rules_per_level.csv")


