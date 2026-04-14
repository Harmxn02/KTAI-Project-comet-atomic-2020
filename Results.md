# RESULTS

The code was modified to fit my strategy, and the results are whatever was outputted to my console. After which I ~~asked Claude to generate a~~ made a write-up of the results, which is what you see below.

---

## Investigation: BLEU Performance by Relation Category

The partitioning strategy chosen was **relation category** — the three broad groups that ATOMIC²⁰²⁰ itself defines (social-interaction, physical-entity, and event-centred). Each test example was assigned to a category based on its relation type, and BLEU-1 through BLEU-4 were computed separately for each group.

---

## Results

**Per category (the headline finding):**

| Category           | BLEU-1 | BLEU-2 | BLEU-3 | BLEU-4 |
| ------------------ | ------ | ------ | ------ | ------ |
| social-interaction | 0.763  | 0.605  | 0.498  | 0.412  |
| physical-entity    | 0.716  | 0.582  | 0.492  | 0.418  |
| event-centred      | 0.708  | 0.598  | 0.523  | 0.462  |

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
