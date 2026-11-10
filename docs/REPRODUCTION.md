# Reproduction check (2026-11-10)

The analysis command ran from a fresh copy containing only exported files in a fresh Python 3.11.2 environment, with numpy 2.2.6, scipy 1.15.3 and langdetect 1.0.9 (six 1.17.0). Package installation used `python -m pip install -r analysis/requirements.txt`; analysis used `python -B analysis/run_all.py`. The successful analysis run took about 21 seconds on the checking machine; runtime is hardware-dependent.

A Python audit hook in the fresh environment rejected access to the original work tree for every analysis subprocess; an explicit forbidden-read control was rejected. The clean copy contained no private datasets or replies. This verifies this Python pipeline's independence from those files, not a general operating-system security boundary. The first attempt placed native dependencies on a no-execute temporary filesystem and failed to load NumPy. The successful attempt used a new environment on an executable filesystem; no mount or serving-system settings changed.

Expected differences were declared before this run: neutral field names, omitted platform details, runtime-version metadata, and added relative-time keys. After only those declared exclusions, the fresh headline aggregate and preserved legacy alternate aggregate have **zero scientific numeric differences** from the source. All main table numeric cells agree. The ten regenerated outputs are byte-identical to the checked export at the same dependency versions; hashes are below. The D15 count-only sensitivity is additive and regenerated from its published 20-row count input. It is not new judging.

This is an aggregate-arithmetic reproduction from exported scores and derived inputs. It does not independently reproduce live collection, original private task execution, reply scoring, judge labels, original telemetry, or the legacy alternate-environment generation.

| generated file | SHA-256 |
|---|---|
| `refusal_truncation_sensitivity.md` | `99f9300b51141f4a547bd69a3ae893a29e1d422703781b514b980d688889417c` |
| `results.json` | `91e0328ea9fac9fbae52ca2f10d1dcd0203a312702891c4b42ec903dbc48007a` |
| `extra_results.json` | `1376cbf94c8a9d7412c5192fb24f189c91b753634630c391097611e5d40ddcdf` |
| `extra_tables.md` | `b7a32755343b9f0ec061c02f989dee55b3c398b3910aa98f4df0d1f7605761de` |
| `extra_results_altenv.json` | `d5ea0ba4a832afc82afac84ff9558bb004c72119c66e823b5d2216d99b5239a9` |
| `extra_tables_altenv.md` | `dee3cabb9261ff5c7d40be646a54bc995d0df9b1f17f5aad0d927c982ea0c052` |
| `extra_results_unseeded.json` | `7caa2a382021c3854e3520937c0cb6e233efd46f3970dd663ca174213c17ce62` |
| `extra_tables_unseeded.md` | `dc82dce7c4e8d5c279045acb9c698bb558752e065e03c03cb72c9da87433a2a9` |
| `extra_refusal_classifiers.md` | `94a22c1de76f64b3e9a5d803cf0166cbce8e457346338790c946f29e6a423b47` |
| `validation_summary.json` | `fd97be774163d816eb7bda1f636d73b947bcf7ffe488371158a68e93c7f9f1cd` |
