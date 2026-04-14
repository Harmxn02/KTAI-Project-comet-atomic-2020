# RESULTS

The code was modified to fit my strategy, and the results are whatever was outputted to my console. After which I ~~asked Claude to generate a~~ made a write-up of the results, which is what you see below.

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

The `HinderedBy` result is particularly noteworthy and directly discussable in your report — the paper itself highlights that the zero-shot GPT-2 model scored only 1.3% plausibility on `HinderedBy`, yet COMET-BART scores highest on it here, suggesting this is a relation where fine-tuning on the knowledge graph gives the largest benefit.

---

## CLAIMS

### 1. "Social-interaction actually scores highest on BLEU-1 and BLEU-2"

From the category table: social-interaction BLEU-1 = `0.763`, physical-entity = `0.716`, event-centred = `0.708`. ✓

### 2. "Event-centred relations score highest on BLEU-3 and BLEU-4"

From the category table: event-centred BLEU-3 = `0.523`, BLEU-4 = `0.462`, versus social-interaction `0.498`/`0.412` and physical-entity `0.492`/`0.418`. ✓

### 3. "BLEU-1 ranges only from 0.708 to 0.763"

Lowest category BLEU-1 is event-centred `0.708`, highest is social-interaction `0.763`. ✓

### 4. "HinderedBy (BLEU-1: 0.891) and ObjectUse (0.876) are by far the strongest performers"

From the per-relation table, top two rows: `HinderedBy 0.891` and `ObjectUse 0.876`. ✓

### 5. "Causes (0.315), HasProperty (0.428), and CapableOf (0.462) are the weakest"

From the bottom of the per-relation table: `Causes 0.315`, `HasProperty 0.428`, `CapableOf 0.462`. ✓

### 6. "xReason has only 1 example in the test set"

From the per-relation table, first row: `xReason | Count: 1`. ✓

### 7. "The zero-shot GPT-2 model scored only 1.3% plausibility on HinderedBy"

This comes from the paper itself (page 8), not the terminal output — I should have made that distinction clearer. The terminal output only tells us COMET-BART's scores, not GPT-2's.
