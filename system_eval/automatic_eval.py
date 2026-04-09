
#= MY MODIFICATIONS:
#= Extend the per-relation tracking dict to store all four BLEU scores
#= Group relations by their ATOMIC²⁰²⁰ category (social-interaction, event-centred, physical-entity) for a meaningful analysis angle
#= Print a formatted per-relation and per-category summary table

#= SECOND ITERATION
#= A function that supresses stdout and stderr for the duration of a block, to silence the QGEvalCap output during evaluation

# automatic_eval.py

import argparse
import json
import os
from collections import defaultdict
from contextlib import contextmanager

from evaluation.eval import QGEvalCap
from nltk.translate.bleu_score import sentence_bleu
from tabulate import tabulate
from utils import read_jsonl, write_jsonl


@contextmanager
def suppress_fd():
    """
    Suppresses output at the OS file-descriptor level, catching both
    Python-level prints and C-level writes (e.g. from pycocoevalcap).
    """
    with open(os.devnull, 'w') as devnull:
        devnull_fd = devnull.fileno()
        old_stdout_fd = os.dup(1)
        old_stderr_fd = os.dup(2)
        try:
            os.dup2(devnull_fd, 1)
            os.dup2(devnull_fd, 2)
            yield
        finally:
            os.dup2(old_stdout_fd, 1)
            os.dup2(old_stderr_fd, 2)
            os.close(old_stdout_fd)
            os.close(old_stderr_fd)


# Mapping from relation name to ATOMIC2020 category, as defined in the paper (Table 1 / Figure 3)
RELATION_CATEGORIES = {
    # Social-interaction
    "xIntent":      "social-interaction",
    "xAttr":        "social-interaction",
    "xNeed":        "social-interaction",
    "xWant":        "social-interaction",
    "xEffect":      "social-interaction",
    "xReact":       "social-interaction",
    "oWant":        "social-interaction",
    "oEffect":      "social-interaction",
    "oReact":       "social-interaction",
    # Physical-entity
    "ObjectUse":    "physical-entity",
    "AtLocation":   "physical-entity",
    "MadeUpOf":     "physical-entity",
    "HasProperty":  "physical-entity",
    "CapableOf":    "physical-entity",
    "Desires":      "physical-entity",
    "NotDesires":   "physical-entity",
    # Event-centred
    "isAfter":      "event-centred",
    "isBefore":     "event-centred",
    "HinderedBy":   "event-centred",
    "HasSubEvent":  "event-centred",
    "isFilledBy":   "event-centred",
    "Causes":       "event-centred",
    "xReason":      "event-centred",
}


def get_reference_sentences(filename):
    result = []
    with open(filename) as file:
        for line in file:
            result.append([x.strip() for x in line.split('\t')[1].split('|')])
    return result

def postprocess(sentence):
    return sentence

def get_heads_and_relations(filename):
    result = []
    with open(filename) as file:
        for line in file:
            line = line.split('\t')[0]
            head_event = line.split('@@')[0].strip()
            relation = line.split('@@')[1].strip()
            result.append({'head': head_event, 'relation': relation})
    return result

def get_hypothesises(filename):
    result = []
    with open(filename) as file:
        for line in file:
            result.append(json.loads(line)["greedy"])
    return result

def make_bleu_tracker():
    """Returns a fresh per-relation BLEU accumulator dict."""
    return defaultdict(lambda: {"bleu1": 0.0, "bleu2": 0.0, "bleu3": 0.0, "bleu4": 0.0, "count": 0})

def accumulate_bleu(tracker, relation, bleu_1, bleu_2, bleu_3, bleu_4):
    """Adds one example's BLEU scores into the tracker for a given relation."""
    tracker[relation]["bleu1"] += bleu_1
    tracker[relation]["bleu2"] += bleu_2
    tracker[relation]["bleu3"] += bleu_3
    tracker[relation]["bleu4"] += bleu_4
    tracker[relation]["count"] += 1

def compute_averages(tracker):
    """Converts accumulated totals in tracker to per-relation averages."""
    averages = {}
    for relation, vals in tracker.items():
        n = vals["count"]
        averages[relation] = {
            "bleu1": vals["bleu1"] / n,
            "bleu2": vals["bleu2"] / n,
            "bleu3": vals["bleu3"] / n,
            "bleu4": vals["bleu4"] / n,
            "count": n,
        }
    return averages

def compute_category_averages(relation_averages):
    """
    Aggregates per-relation averages up to the three ATOMIC2020 categories.
    Relations not present in RELATION_CATEGORIES are placed in 'unknown'.
    """
    category_totals = defaultdict(lambda: {"bleu1": 0.0, "bleu2": 0.0, "bleu3": 0.0, "bleu4": 0.0, "count": 0})
    for relation, scores in relation_averages.items():
        category = RELATION_CATEGORIES.get(relation, "unknown")
        n = scores["count"]
        category_totals[category]["bleu1"] += scores["bleu1"] * n
        category_totals[category]["bleu2"] += scores["bleu2"] * n
        category_totals[category]["bleu3"] += scores["bleu3"] * n
        category_totals[category]["bleu4"] += scores["bleu4"] * n
        category_totals[category]["count"] += n

    category_averages = {}
    for category, vals in category_totals.items():
        n = vals["count"]
        category_averages[category] = {
            "bleu1": vals["bleu1"] / n,
            "bleu2": vals["bleu2"] / n,
            "bleu3": vals["bleu3"] / n,
            "bleu4": vals["bleu4"] / n,
            "count": n,
        }
    return category_averages

def print_bleu_table(title, averages_dict, sort_by="bleu1"):
    """Prints a formatted BLEU table (per-relation or per-category) to stdout."""
    rows = []
    for name, scores in sorted(averages_dict.items(), key=lambda x: -x[1][sort_by]):
        rows.append([
            name,
            scores["count"],
            f"{scores['bleu1']:.3f}",
            f"{scores['bleu2']:.3f}",
            f"{scores['bleu3']:.3f}",
            f"{scores['bleu4']:.3f}",
        ])
    headers = ["Name", "Count", "BLEU-1", "BLEU-2", "BLEU-3", "BLEU-4"]
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)
    print(tabulate(rows, headers=headers, tablefmt="github"))

def preprocess_generations(args):
    input_file = args.input_file

    outfile_path = os.path.join(
        os.path.dirname(input_file),
        os.path.basename(input_file).split('.')[0] + "_gens.jsonl"
    )
    outfile = open(outfile_path, 'w')

    references_list = get_reference_sentences('test.tsv')
    heads_relations = get_heads_and_relations('test.tsv')
    hypothesises = get_hypothesises(args.input_file)

    total_bleu_1 = 0.0
    total_bleu_2 = 0.0
    total_bleu_3 = 0.0
    total_bleu_4 = 0.0

    relation_tracker = make_bleu_tracker()
    count = 0

    for head_relation, references, hypothesis in zip(heads_relations, references_list, hypothesises):
        bleu_1 = sentence_bleu(references, hypothesis, weights=[1.0])
        bleu_2 = sentence_bleu(references, hypothesis, weights=[0.5, 0.5])
        bleu_3 = sentence_bleu(references, hypothesis, weights=[0.34, 0.33, 0.33])
        bleu_4 = sentence_bleu(references, hypothesis)

        result = {
            'generation': postprocess(hypothesis),
            'references': [postprocess(reference) for reference in references],
            'input': head_relation
        }

        if hypothesis != 'none':
            total_bleu_1 += bleu_1
            total_bleu_2 += bleu_2
            total_bleu_3 += bleu_3
            total_bleu_4 += bleu_4
            accumulate_bleu(relation_tracker, head_relation["relation"], bleu_1, bleu_2, bleu_3, bleu_4)
            count += 1

        outfile.write(json.dumps(result) + "\n")

    print('gens non-none', count)

    summary = {
        'bleu1': total_bleu_1 / count,
        'bleu2': total_bleu_2 / count,
        'bleu3': total_bleu_3 / count,
        'bleu4': total_bleu_4 / count,
    }

    relation_averages = compute_averages(relation_tracker)
    category_averages = compute_category_averages(relation_averages)

    print_bleu_table("BLEU scores per relation type", relation_averages)
    print_bleu_table("BLEU scores per ATOMIC2020 category", category_averages)

    outfile_scores = open(
        os.path.join(os.path.dirname(input_file),
        os.path.basename(input_file).split('.')[0] + "_scores.jsonl"), 'w'
    )
    scores_to_save = dict(summary)
    for relation, scores in relation_averages.items():
        scores_to_save[relation] = scores
    outfile_scores.write(json.dumps(scores_to_save) + "\n")

    print(f"\nOverall: BLEU-1={summary['bleu1']:.3f}  BLEU-2={summary['bleu2']:.3f}  "
          f"BLEU-3={summary['bleu3']:.3f}  BLEU-4={summary['bleu4']:.3f}")
    print(f"Saved gens in {outfile_path}")

    return os.path.abspath(outfile_path)

def get_tuple(l):
    gens = [l["generation"]]
    head = l["input"]["head"]
    tails = l["references"]
    relation = l["input"]["relation"]
    return {"head": head, "relation": relation, "tails": tails, "generations": gens}

def get2(l):
    return list(zip(*l))[1]

def topk_eval(model_name, data, k, quiet=False):
    topk_gts = {}
    topk_res = {}
    instances = []
    topk_exact_match = []
    topk_exact_match_not_none = []
    topk_bleu_score = []
    topk_is_head = []

    for i, l in enumerate(data):
        t = get_tuple(l)
        gens = t["generations"]
        tails = t["tails"]
        head = t["head"]

        for (j, g) in enumerate(gens[:k]):
            instance = t.copy()
            instance["generation"] = g
            instances.append(instance)

            key = str(i) + "_" + str(j)
            topk_gts[key] = tails
            topk_res[key] = [g]

            if g in tails:
                topk_exact_match.append((l, 1))
                if g != "none":
                    topk_exact_match_not_none.append((l, 1))
            else:
                topk_exact_match.append((l, 0))
                if g != "none":
                    topk_exact_match_not_none.append((l, 0))
            if g == head:
                topk_is_head.append((l, 1))
            else:
                topk_is_head.append((l, 0))

    QGEval = QGEvalCap(model_name, topk_gts, topk_res)
    if quiet:
        with suppress_fd():
            score, scores = QGEval.evaluate()
    else:
        score, scores = QGEval.evaluate()

    return score, scores, instances


def eval(data_file, model_name, quiet=False):
    data = read_jsonl(data_file)
    if len(data) == 0:
        return None
    return topk_eval(model_name, data, k=1, quiet=quiet)

def toRow(name, results, columns):
    return [name] + [format(float(results[c]), '#.3f') for c in columns]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, help='Results file on ATOMIC2020 test set')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output from QGEvalCap')
    args = parser.parse_args()

    generations_file = preprocess_generations(args)

    input_file = generations_file
    expts = [
        [input_file, os.path.basename(input_file).split('.')[0]]
    ]

    scores_per_model = []
    add_column = True
    for f, m in expts:
        result_file = './results/{}_scores.jsonl'.format(m)

        s, scores, instances = eval(f, model_name=m, quiet=args.quiet)
        if s is None:
            print("Skipping ", m)
            continue

        for k in scores.keys():
            assert len(scores[k]) == len(instances)

        results = {"model": m, "scores": s, "all_scores": scores, "instances": instances}
        write_jsonl(result_file, [results])

        scores_per_model.append(results)
        columns = list(results["scores"].keys())
        s_row = toRow(results["model"], results["scores"], columns)
        if add_column:
            rows = [[""] + columns]
            add_column = False
        rows.append(s_row)

    import datetime
    date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    print(scores_per_model)

    write_jsonl('./results/scores_{}.jsonl'.format(date), scores_per_model)
    print(tabulate(rows, headers='firstrow', tablefmt='latex', floatfmt='#.3f'))
    print(tabulate(rows, tablefmt='tsv', floatfmt='#.3f'))

if __name__ == "__main__":
    main()