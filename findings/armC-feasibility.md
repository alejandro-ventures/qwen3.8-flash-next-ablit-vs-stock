# Arm C: offline feasibility check (before any arm C data)

Question: can the newer overlay sidecar `fp4-local/house-answer-qsa-gdn-mxfp8.safetensors` (overlay repository `main` f0192705c8ab34f1140f7be8dbe556cdfe49b2e0) be served
through the recipe's `ABLIT` loader, and does it need a new kernel format?

Method: the safetensors header of the sidecar was read by an HTTP range request; the header of the stock FP4-Local checkpoint (revision b9ce18a6) was compared with it. Nothing was served.

| item | value |
|---|---|
| tensors in the sidecar | 96 = 12 `self_attn.o_proj` + 36 `linear_attn.out_proj` (gated-delta-net layers), each a weight plus a scale |
| weight dtype and shape | F8_E4M3, [2560, 6144] |
| scale dtype and shape | U8, [2560, 192] |
| names found in the stock index | 96 of 96 (all in shard `tensors/model-00001-of-00021.safetensors`) |
| dtype and shape equal to the stock entries | 96 of 96 |

Consequence: the GDN `out_proj` tensors already use the same MXFP8 (group size 32) format in the stock checkpoint, so no new kernel path is needed.

Loader: `scripts/ablit_view.py` in the recipe hard-codes the 24 `o_proj` names (12 layers x weight and scale) and refuses other sidecars. Using the newer sidecar
through it needs the allowed-name list widened to 96 names and the count check changed from 24 to 96; `armC/ablit_view_house_answer.diff` is that change.

Caveats stated by the overlay author (quoted from the overlay's README as we read it before the study): the `o_proj`-only sidecar pinned by the recipe topic-switches mainly with
thinking on; the newer default sidecar was validated by the author with a thinking budget of 96 and `reasoning_effort: low`. The study did not use a thinking budget.
