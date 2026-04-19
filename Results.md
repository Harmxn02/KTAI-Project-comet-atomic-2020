# RESULTS

The code was modified to fit my strategy, and the results are whatever was outputted to my console. After which I made a write-up of the results, which is what you see below.

---

## Investigation: BLEU Performance by Relation Category

The partitioning strategy chosen was **relation category** — the three broad groups that ATOMIC²⁰²⁰ itself defines (social-interaction, physical-entity, and event-centred). Each test example was assigned to a category based on its relation type, and BLEU-1 through BLEU-4 were computed separately for each group.

---

## Results

**BLEU scores per relation type:**

| Name        |   Count |   BLEU-1 |   BLEU-2 |   BLEU-3 |   BLEU-4 |
|-------------|---------|----------|----------|----------|----------|
| xReason     |       1 |    0.9   |    0.837 |    0.706 |    0.562 |
| HinderedBy  |     378 |    0.891 |    0.805 |    0.718 |    0.647 |
| ObjectUse   |     192 |    0.876 |    0.777 |    0.664 |    0.57  |
| xWant       |     359 |    0.854 |    0.717 |    0.603 |    0.472 |
| xAttr       |     355 |    0.85  |    0.638 |    0.516 |    0.462 |
| HasSubEvent |      15 |    0.803 |    0.697 |    0.614 |    0.518 |
| isFilledBy  |     129 |    0.787 |    0.574 |    0.472 |    0.362 |
| xEffect     |     257 |    0.781 |    0.596 |    0.449 |    0.346 |
| xNeed       |     363 |    0.774 |    0.647 |    0.54  |    0.433 |
| oWant       |     135 |    0.769 |    0.626 |    0.519 |    0.404 |
| xIntent     |     287 |    0.688 |    0.551 |    0.465 |    0.365 |
| oEffect     |      27 |    0.684 |    0.524 |    0.379 |    0.309 |
| xReact      |     362 |    0.655 |    0.489 |    0.411 |    0.388 |
| oReact      |      77 |    0.635 |    0.492 |    0.418 |    0.362 |
| isBefore    |     424 |    0.623 |    0.518 |    0.452 |    0.403 |
| isAfter     |     432 |    0.612 |    0.507 |    0.441 |    0.394 |
| AtLocation  |      88 |    0.6   |    0.452 |    0.407 |    0.327 |
| NotDesires  |       1 |    0.5   |    0     |    0     |    0     |
| CapableOf   |      31 |    0.462 |    0.238 |    0.153 |    0.139 |
| MadeUpOf    |      19 |    0.442 |    0.263 |    0.202 |    0.202 |
| HasProperty |      24 |    0.428 |    0.233 |    0.135 |    0.112 |
| Desires     |       1 |    0.35  |    0.235 |    0     |    0     |
| Causes      |       9 |    0.315 |    0.197 |    0.131 |    0.111 |

**Per category (the headline finding):**

| Name               |   Count |   BLEU-1 |   BLEU-2 |   BLEU-3 |   BLEU-4 |
|--------------------|---------|----------|----------|----------|----------|
| social-interaction |    2222 |    0.763 |    0.605 |    0.498 |    0.412 |
| physical-entity    |     356 |    0.716 |    0.582 |    0.492 |    0.418 |
| event-centred      |    1388 |    0.708 |    0.598 |    0.523 |    0.462 |

> [!NOTE]
> Basically they all perform similarly. If you take account of the COUNTS per relation type, the bad performers don't have much influence on the overall category scores, which is why the category-level differences are small.
>
> In the first table there are quite a few low scores (Desires, Causes, HasProperty, CapableOf, MadeUpOf), but they also have very low counts (1, 9, 24, 31, 19 respectively), so they don't drag down the category averages much.

The differences between categories are surprisingly small — BLEU-1 ranges only from 0.708 to 0.763, which partially contradicts the hypothesis that social-interaction relations would be hardest. Social-interaction actually scores _highest_ on BLEU-1 and BLEU-2, likely because its tails tend to be short and formulaic (e.g. `"to be kind"`, `"relieved"`). Event-centred relations score highest on BLEU-3 and BLEU-4, suggesting their longer outputs have better n-gram overlap when they do match.

**The more interesting story is at the per-relation level**, where variance is enormous:

- `HinderedBy` (BLEU-1: 0.891) and `ObjectUse` (0.876) are by far the strongest performers
- `Causes` (0.315), `HasProperty` (0.428), and `CapableOf` (0.462) are the weakest
- `xReason` has only 1 example in the test set, so its score (0.9) should be treated with caution
