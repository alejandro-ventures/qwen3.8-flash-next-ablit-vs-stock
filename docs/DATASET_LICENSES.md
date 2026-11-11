# Dataset licences at the pinned revisions

Checked 2026-11-10 by fetching the pinned dataset cards or repository LICENSE files. A dataset-card declaration is recorded as such; it is not a full upstream chain-of-title audit. Dataset text is withheld. Public revision hashes are in items/REVISIONS.json.

| dataset | licence declaration at pin | evidence |
|---|---|---|
| TIGER-Lab/MMLU-Pro | license: mit | [pinned source](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro/raw/b189ec765aa7ed75c8acfea42df31fdae71f97be/README.md) |
| HuggingFaceH4/MATH-500 | No licence declaration in the pinned dataset card. | [pinned source](https://huggingface.co/datasets/HuggingFaceH4/MATH-500/raw/6e4ed1a2a79af7d8630a6b768ec859cb5af4d3be/README.md) |
| google/IFEval | license: apache-2.0 | [pinned source](https://huggingface.co/datasets/google/IFEval/raw/966cd89545d6b6acfd7638bc708b98261ca58e84/README.md) |
| juletxara/mgsm | CC BY-SA 4.0; applicable derived portions retain share-alike terms | [pinned source](https://huggingface.co/datasets/juletxara/mgsm/raw/b2f13d426afe3be8d69a7e739b36724db8b66bbc/README.md) |
| evalplus/humanevalplus | license: apache-2.0 | [pinned source](https://huggingface.co/datasets/evalplus/humanevalplus/raw/d32357cf319e50e9c8d8dab5ea876c72b0fd321b/README.md) |
| evalplus/mbppplus | license: apache-2.0 | [pinned source](https://huggingface.co/datasets/evalplus/mbppplus/raw/b2d74c91837c3f2a20c1299ae98133cbe7cfa077/README.md) |
| gorilla-llm/Berkeley-Function-Calling-Leaderboard | license: apache-2.0 | [pinned source](https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard/raw/61fc0608cfd831fcfbbaa676ebdfef0ed963eeda/README.md) |
| JailbreakBench/JBB-Behaviors | license: "mit" | [pinned source](https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors/raw/886acc352a31533ffbcf4ef22c744658688086fc/README.md) |
| centerforaisafety/HarmBench | MIT License | [pinned source](https://raw.githubusercontent.com/centerforaisafety/HarmBench/8e1604d1171fe8a48d8febecd22f600e462bdcdd/LICENSE) |
| paul-rottger/xstest | Attribution 4.0 International | [pinned source](https://raw.githubusercontent.com/paul-rottger/xstest/d7bb5bd738c1fcbc36edd83d5e7d1b71a3e2d84d/LICENSE) |

MATH-500: the pinned card has no licence declaration but links the PRM800K math splits. Source-chain checks on 2026-11-10 found MIT at [PRM800K's pinned licence](https://github.com/openai/prm800k/blob/7ecc794703b2877f63226f2477a49b34f9b25163/LICENSE) and [the underlying MATH repository licence](https://github.com/hendrycks/math/blob/985bdc1696e88e8643f081a0ff4719da39f2ae2a/LICENSE). These checks document available source terms, not a full third-party chain-of-title determination. This export contains IDs and scores, not dataset text; its original-work licence does not relicense upstream material.
MGSM attribution: the Multilingual Grade School Math Benchmark authors, through the pinned juletxara/mgsm dataset card; selected English, German and Spanish test items, converted to ID/score records. The original text is withheld. Apply CC BY-SA 4.0 to MGSM-derived portions where required.
The local long-context generator is original study code (MIT); the synthetic stand-ins are CC BY 4.0. The public refusal ID lists derive from JBB-Behaviors, HarmBench and XSTest as listed above.

No model weights, sidecars, direction files or access credentials are distributed. Official sources checked on 2026-11-10: the base model uses [Qwen Community License 1.0 at the checked revision](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/blob/812d96e10a0dd82b69d749e68693698cf6c36daa/LICENSE), not MIT or Apache-2.0. The [pinned NVIDIA checkpoint card](https://huggingface.co/nvidia/Qwen3.8-Flash-Next-FP4-Local/blob/b9ce18a6887e18c089fdea8509a33e63429a3300/README.md) identifies both the NVIDIA Open Model Agreement and Qwen terms; the agreement linked there was read (version 2026-03-09). Upstream use and redistribution conditions remain applicable where relevant; the report's licence does not grant rights to those models. Verifying these sources is distinct from scientific validation or a blanket legal clearance.
