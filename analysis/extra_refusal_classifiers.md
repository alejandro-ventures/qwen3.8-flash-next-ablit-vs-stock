# Refusal rates by classifier (harmful = 291 prompts, benign = 350; mean over the arm's sessions)

| set | classifier | A % | B % | C % |
|---|---|---|---|---|
| refusal_harmful | judge REFUSED | 49.1 | 0.0 | 0.0 |
| refusal_harmful | judge REFUSED+PARTIAL | 97.6 | 1.0 | 0.3 |
| refusal_harmful | regex refusal phrase (first 400 chars) | 68.4 | 0.0 | 0.0 |
| refusal_benign | judge REFUSED | 3.1 | 0.0 | 0.0 |
| refusal_benign | judge REFUSED+PARTIAL | 10.3 | 0.3 | 0.3 |
| refusal_benign | regex refusal phrase (first 400 chars) | 12.9 | 0.0 | 0.0 |
| refusal_harmful_t | judge REFUSED | 83.0 | 0.0 | 0.0 |
| refusal_harmful_t | judge REFUSED+PARTIAL | 96.0 | 2.0 | 1.0 |
| refusal_harmful_t | regex refusal phrase (first 400 chars) | 83.0 | 0.0 | 0.0 |
| refusal_benign_t | judge REFUSED | 11.0 | 0.0 | 0.0 |
| refusal_benign_t | judge REFUSED+PARTIAL | 22.0 | 0.0 | 0.0 |
| refusal_benign_t | regex refusal phrase (first 400 chars) | 16.0 | 0.0 | 0.0 |

# Second-model-adjudicated blinded subset (reference; 15 harmful + 15 benign per arm session, A1 and B1 only; n is small, counts not rates)

| session | set | n | 2nd model REFUSED | 2nd model PARTIAL | 2nd model COMPLIED | 2nd model OFFTOPIC | judge REFUSED | judge PARTIAL | judge COMPLIED | judge OFFTOPIC |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | refusal_harmful | 15 | 15 | 0 | 0 | 0 | 6 | 8 | 1 | 0 |
| A1 | refusal_benign | 15 | 2 | 3 | 10 | 0 | 0 | 2 | 13 | 0 |
| B1 | refusal_harmful | 15 | 0 | 4 | 3 | 8 | 0 | 0 | 14 | 1 |
| B1 | refusal_benign | 15 | 0 | 0 | 12 | 3 | 0 | 0 | 13 | 2 |