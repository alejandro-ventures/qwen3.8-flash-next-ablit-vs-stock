"""Count-only all-truncation sensitivity for the primary A/B refusal sets.

Uses published labels and aggregate finish/label intersections. No reply text,
new judging, per-item reclassification, paired interval or model call is used.
"""
from pathlib import Path
import collections,csv,json

AN=Path(__file__).resolve().parent
records=json.loads((AN/'inputs/refusal_truncation_counts.json').read_text(encoding='utf-8'))
labels=collections.defaultdict(list)
for row in csv.DictReader((AN/'inputs/refusal_labels.csv').open(encoding='utf-8')):
    labels[(row['session'],row['set'])].append(row['judge_label'])

def unclassified(label):
    return label in {'UNCLASSIFIED','ERROR'} or label.startswith('UNPARSED')

def union_count(refused,unclassified_count,length_count,length_already_in_union):
    """Union size; length-finished R/U labels must not be counted twice."""
    return refused+unclassified_count+length_count-length_already_in_union

# The overlap case is essential even though primary length-finished labels are COMPLIED.
assert union_count(0,0,13,0)==13
assert union_count(5,2,4,3)==8

session_rows=[]
for st in ('refusal_harmful','refusal_benign'):
    for session in ('A1','A2','B1','B2'):
        r=next(x for x in records if x['session']==session and x['set']==st)
        labs=labels[(session,st)];n=r['n'];assert len(labs)==n
        counts=collections.Counter(labs);refused=counts['REFUSED'];u=sum(v for k,v in counts.items() if unclassified(k))
        assert u==r['actual_unclassified']
        lengths=r['labels_of_length_finishes'];assert sum(lengths.values())==r['length_finishes']
        assert set(lengths) <= {'COMPLIED','OFFTOPIC'}, 'Frozen primary-set label assumption changed'
        overlap_u=sum(v for k,v in lengths.items() if unclassified(k))
        overlap=overlap_u+lengths.get('REFUSED',0)
        strict_u=u+r['length_finishes']-overlap_u
        assert strict_u==r['unclassified_if_all_length']
        combined=union_count(refused,u,r['length_finishes'],overlap)
        assert 0<=combined<=n
        session_rows.append({'session':session,'set':st,'n':n,'historical_refused':refused,'historical_unclassified':u,'length_finishes':r['length_finishes'],'length_already_refused_or_unclassified':overlap,'strict_unclassified':strict_u,'refused_or_strict_unclassified':combined,'rate':combined/n})
arm_rows=[]
for st in ('refusal_harmful','refusal_benign'):
    rate=lambda sessions:sum(r['rate'] for r in session_rows if r['set']==st and r['session'] in sessions)/len(sessions)
    a,b=rate(('A1','A2')),rate(('B1','B2'))
    arm_rows.append({'set':st,'n_prompts_per_session':next(r['n'] for r in session_rows if r['set']==st),'A':a,'B':b,'B_minus_A':b-a})
result={'scope':'Primary non-thinking A/B sets only; count-only REFUSED-or-strict-UNCLASSIFIED sensitivity.','method':'Historical R/U union plus all length finishes, subtracting overlap with labels already in the union. Arm rate is the mean of its two session rates.','limits':'No raw replies or per-item finish flags; no re-judging or paired interval. This does not replace frozen primary outcomes. C1 and thinking-on missingness are covered separately in the D15 count audit.','sessions':session_rows,'arms':arm_rows}
(AN/'strict_unclassified_sensitivity.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
md=['# Strict all-truncation counting sensitivity (v1.0.1)','',result['scope'],'',result['method'],'',result['limits'],'','Repeated sessions reuse the same prompts and are not independent observations. These point rates are descriptive arithmetic; no confidence interval is estimated.','','| set | prompts/session | Stock A % | Overlay B % | B-A (pp) |','|---|---:|---:|---:|---:|']
for r in arm_rows:md.append(f"| {r['set']} | {r['n_prompts_per_session']} | {100*r['A']:.2f} | {100*r['B']:.2f} | {100*r['B_minus_A']:+.2f} |")
md+=['','## Session counts','','| session | set | n | historical REFUSED | historical UNCLASSIFIED | length finishes | already in union | strict union count |','|---|---|---:|---:|---:|---:|---:|---:|']
for r in session_rows:md.append(f"| {r['session']} | {r['set']} | {r['n']} | {r['historical_refused']} | {r['historical_unclassified']} | {r['length_finishes']} | {r['length_already_refused_or_unclassified']} | {r['refused_or_strict_unclassified']} |")
md+=['','In these primary sets no length-finished reply carried REFUSED, PARTIAL or UNCLASSIFIED. Therefore the historical REFUSED and REFUSED+PARTIAL rates do not move; the sensitivity that counts unclassified responses as refused does. See the [erratum](../ERRATA.md) for label mapping and [D15-D17](../DEVIATIONS.md) for protocol clarifications.','']
(AN/'strict_unclassified_sensitivity.md').write_text('\n'.join(md),encoding='utf-8')
print('Generated count-only strict-unclassified summary; frozen outcomes unchanged.')
