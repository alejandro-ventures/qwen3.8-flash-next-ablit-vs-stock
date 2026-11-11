"""Generate standalone study figures from published aggregate/label inputs.
No model calls, bootstrap re-estimation or raw response text is used.
Run: python figures/generate_figures.py
"""
from pathlib import Path
import csv, hashlib, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'figures'
D = json.loads((ROOT / 'analysis/extra_results.json').read_text(encoding='utf-8'))
PAPER, INK, STOCK, COPPER, MUTED, LINE, EXP = '#f4f3ee', '#15171a', '#3b3f45', '#8c4a11', '#5f646b', '#d9d7ce', '#6c7464'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'figure.facecolor':PAPER,'axes.facecolor':PAPER,'text.color':INK,'axes.labelcolor':INK,'xtick.color':MUTED,'ytick.color':INK,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','svg.hashsalt':'qwen-study-standalone-figures','savefig.facecolor':PAPER})
TRACES, OUTPUTS = {}, {}

def save(fig, name, caption, trace):
    fig.text(.035,.025,caption,fontsize=8.3,color=MUTED,va='bottom',wrap=True)
    for ext in ('png','svg'):
        p=OUT/(name+'.'+ext)
        if ext=='svg':fig.savefig(p,metadata={'Date':None})
        else:fig.savefig(p,dpi=180)
        OUTPUTS[p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
    TRACES[name]=trace
    plt.close(fig)

def box(ax,x,y,w,h,title,detail,color=STOCK):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012',ec=LINE,fc='#fbfaf6',lw=1.2))
    ax.text(x+w/2,y+h*.65,title,ha='center',va='center',weight='bold',color=color,fontsize=11)
    ax.text(x+w/2,y+h*.30,detail,ha='center',va='center',color=MUTED,fontsize=9)

fig,ax=plt.subplots(figsize=(11,4.1));fig.subplots_adjust(left=.025,right=.975,top=.84,bottom=.20);ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
fig.suptitle('Figure 1. Compare the same tasks in stock and overlay configurations',x=.035,ha='left',fontsize=14,weight='bold')
box(ax,.02,.36,.20,.26,'Same test items','Matched within item')
box(ax,.38,.63,.23,.24,'A · Stock','ABLIT=0',STOCK);box(ax,.38,.12,.23,.24,'B · Overlay','ABLIT=1',COPPER)
box(ax,.77,.36,.20,.26,'Recorded outcomes','Scores, labels and speed')
for x1,y1,x2,y2 in [(.24,.50,.35,.75),(.24,.47,.35,.24),(.63,.75,.74,.51),(.63,.24,.74,.46)]:ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops={'arrowstyle':'->','color':MUTED,'lw':1.4})
save(fig,'01_comparison','Conceptual study workflow; not a model-architecture diagram. Fewer refusal labels do not establish useful task completion.',{'type':'conceptual diagram','source':'PROTOCOL.md and study report'})

fig,ax=plt.subplots(figsize=(11,3.4));fig.subplots_adjust(left=.025,right=.975,top=.82,bottom=.28);ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
fig.suptitle('Figure 2. Restarted collection order: A–B–B–A',x=.035,ha='left',fontsize=14,weight='bold')
for i,(session,detail,color) in enumerate([('A1','Stock',STOCK),('B1','Original overlay',COPPER),('B2','Original overlay',COPPER),('A2','Stock',STOCK)]):
    x=.025+i*.245;box(ax,x,.28,.20,.48,session,detail,color)
    if i<3:ax.annotate('',xy=(x+.235,.52),xytext=(x+.21,.52),arrowprops={'arrowstyle':'->','color':MUTED,'lw':1.3})
save(fig,'02_collection_order','A0 was an earlier-image diagnostic. C1 followed A2 with a different overlay and is exploratory. ABBA does not eliminate time effects.',{'primary_order':['A1','B1','B2','A2'],'diagnostic':'A0','exploratory_after_primary':'C1'})

fig,ax=plt.subplots(figsize=(10.5,5.1));fig.subplots_adjust(left=.19,right=.80,top=.84,bottom=.25)
r=D['capability']['B_vs_A'];names=['mmlu_pro','math500','code','ifeval','mgsm','bfcl','composite'];labels=['MMLU-Pro','MATH-500','Code','IFEval','MGSM','BFCL tool calls','Composite']
for i,k in enumerate(names):
    v=r['composite'] if k=='composite' else r['per_set'][k];x=100*v['d'];lo,hi=np.array(v['ci95'])*100;c=COPPER if k=='composite' else STOCK
    ax.errorbar(x,i,xerr=[[x-lo],[hi-x]],fmt='D' if k=='composite' else 'o',color=c,capsize=3,lw=1.5)
    ax.text(1.03,i,f'{x:+.2f} [{lo:+.2f}, {hi:+.2f}]',transform=ax.get_yaxis_transform(),va='center',fontsize=9)
ax.axvline(0,color=LINE);ax.plot([-1.5,-1.5],[5.65,6.35],color=MUTED,ls='--',lw=1);ax.set(yticks=range(7),yticklabels=labels,xlim=(-14.5,5),xlabel='Overlay B minus stock A (percentage points)');ax.invert_yaxis()
fig.suptitle('Figure 3. Capability differences and 95% item-sampling intervals',x=.035,ha='left',fontsize=14,weight='bold')
save(fig,'03_capability','Primary composite: −2.92 pp [−4.08, −1.77] under D8-amended eligibility. Original-rule BFCL-related gates remain inconclusive.\nDashed line: −1.5 pp criterion for the composite only. Intervals omit restart, scoring, judge and contamination uncertainty.',r)

fig,axes=plt.subplots(1,2,figsize=(11,4.8));fig.subplots_adjust(left=.19,right=.97,top=.80,bottom=.28,wspace=.40)
keys=['judge REFUSED (frozen primary)','judge REFUSED+PARTIAL (pre-specified)','regex refusal phrase','judge REFUSED+OFFTOPIC (exploratory)'];labels=['REFUSED','REFUSED + PARTIAL','Regex phrase','REFUSED + OFFTOPIC']
for ax,st,title,xlim in zip(axes,['refusal_harmful','refusal_benign'],['Harmful prompts · n=291','Benign prompts · n=350'],[(-105,7),(-19,3)]):
    for i,k in enumerate(keys):
        v=D['refusal'][st][k]['B_vs_A'];x=v['d']*100;lo,hi=np.array(v['ci95'])*100
        ax.errorbar(x,i,xerr=[[x-lo],[hi-x]],fmt=['o','s','^','D'][i],color=COPPER,capsize=3)
    ax.axvline(0,color=LINE);ax.set(xlim=xlim,yticks=range(4),yticklabels=labels if ax is axes[0] else ['']*4,xlabel='B minus A (percentage points)',title=title);ax.invert_yaxis()
fig.suptitle('Figure 4. Refusal-label changes depend on the classifier',x=.035,ha='left',fontsize=14,weight='bold')
save(fig,'04_refusal','Non-thinking outcomes, 95% paired prompt-bootstrap intervals; panels use different scales. Automated labels are not verified usefulness.\nSelected post-hoc judge audit: four-class κ=0.34. Historical truncation handling is retained and separately audited (D15).',{st:D['refusal'][st] for st in ('refusal_harmful','refusal_benign')})

fig,(ax,b)=plt.subplots(1,2,figsize=(11,4.7),gridspec_kw={'width_ratios':[1.2,1]});fig.subplots_adjust(left=.16,right=.96,top=.81,bottom=.29,wspace=.36)
conds=['prose_1','prose_5','code_1','code_5'];labels=['Prose · 1 stream','Prose · 5 streams','Code · 1 stream','Code · 5 streams']
for i,k in enumerate(conds):
    v=D['H3'][k];x=v['B_over_A'];lo,hi=v['ci90_D2'];ax.errorbar(x,i,xerr=[[x-lo],[hi-x]],fmt='o',color=COPPER,capsize=3);ax.text(x,i-.18,f'{x:.3f}',ha='center',fontsize=9)
    for sess,off,c,m in [('A1',-.14,STOCK,'o'),('A2',-.04,STOCK,'s'),('B1',.04,COPPER,'o'),('B2',.14,COPPER,'s')]:b.scatter(D['speed_raw'][sess][k],np.repeat(i+off,3),c=c,marker=m,s=24,alpha=.7)
ax.axvspan(.95,1.05,color='#e6e3da');ax.axvline(1,color=LINE);ax.set(xlim=(.78,1.55),yticks=range(4),yticklabels=labels,xlabel='B/A throughput ratio · 90% interval');ax.invert_yaxis()
b.set(yticks=range(4),yticklabels=['']*4,xlim=(0,210),xlabel='Batch median total tokens/s');b.invert_yaxis()
fig.suptitle('Figure 5. Speed direction differs between two fixed prompts',x=.035,ha='left',fontsize=14,weight='bold')
save(fig,'05_speed','Graphite: stock; copper: overlay. Circles/squares: first/second sessions; three dependent batch medians per session.\nShading: 0.95–1.05 equivalence band. These intervals do not estimate restart variability or a general speed effect.',{'H3':D['H3'],'speed_raw':D['speed_raw']})

fig,ax=plt.subplots(figsize=(11,4.9));fig.subplots_adjust(left=.33,right=.77,top=.82,bottom=.28)
rows=[('Primary B − A · 6 sets',D['capability']['B_vs_A']['composite'],COPPER,'D'),('D8 A/B flags · 5 sets',D['d8_sensitivity']['A_B_sessions_only_exclusion']['composite'],STOCK,'o'),('D8 flags incl. C1 · 4 sets',D['d8_sensitivity']['all_sessions_incl_C1_exclusion']['composite'],STOCK,'s'),('Exploratory C − A',D['capability']['C_vs_A']['composite'],EXP,'^'),('Exploratory C − B',D['capability']['C_vs_B']['composite'],EXP,'^')]
for i,(label,v,c,m) in enumerate(rows):
    x=v['d']*100;lo,hi=np.array(v['ci95'])*100;ax.errorbar(x,i,xerr=[[x-lo],[hi-x]],fmt=m,color=c,capsize=3)
    ax.text(1.03,i,f'{x:+.2f} [{lo:+.2f}, {hi:+.2f}]',transform=ax.get_yaxis_transform(),va='center',fontsize=9)
ax.axvline(0,color=LINE);ax.plot([-1.5,-1.5],[-.4,2.4],color=MUTED,ls='--',lw=1);ax.set(yticks=range(5),yticklabels=[r[0] for r in rows],xlim=(-4.7,2),xlabel='Difference (percentage points)');ax.invert_yaxis()
fig.suptitle('Figure 6. Changed-set sensitivities do not establish the same margin result',x=.035,ha='left',fontsize=13,weight='bold')
save(fig,'06_sensitivity','Both D8 sensitivities omit BFCL, the largest decline, and use different weights (1/5 or 1/4). Their intervals cross −1.5 pp.\nDashed line is the formal primary margin, only a reference for D8. C1 is one later session with a different overlay.',{'rows':[{'label':label,**v} for label,v,_,_ in rows]})

labels=['REFUSED','PARTIAL','COMPLIED','OFFTOPIC'];matrix=np.zeros((4,4),dtype=int)
for row in csv.DictReader((ROOT/'analysis/inputs/adjudication_pairs.csv').open(encoding='utf-8-sig')):matrix[labels.index(row['judge_label']),labels.index(row['second_model_label'])]+=1
fig,ax=plt.subplots(figsize=(8.5,5.8));fig.subplots_adjust(left=.22,right=.88,top=.83,bottom=.29);ax.imshow(matrix,cmap=matplotlib.colors.LinearSegmentedColormap.from_list('copper',[PAPER,'#c98a4b',COPPER]),vmin=0,vmax=25)
for i in range(4):
    for j in range(4):ax.text(j,i,str(matrix[i,j]),ha='center',va='center',fontsize=13,color=PAPER if matrix[i,j]>15 else INK)
ax.set(xticks=range(4),xticklabels=labels,yticks=range(4),yticklabels=labels,xlabel='Second model label',ylabel='Frozen study judge label');ax.tick_params(axis='x',rotation=20)
fig.suptitle('Figure 7. Selected-sample judge agreement (60 responses)',x=.035,ha='left',fontsize=14,weight='bold')
save(fig,'07_judge_agreement','Agreement is not accuracy. Sample: 47 judge/regex agreements and 13 disagreements; responses truncated to 600 characters.\nFour-class κ=0.34; refused-versus-other κ=0.44; complied-versus-other κ=0.50. Neither model is ground truth.',{'labels':labels,'matrix':matrix.tolist(),'n':int(matrix.sum())})

(OUT/'plot_data.json').write_text(json.dumps(TRACES,indent=2)+'\n',encoding='utf-8')
inputs=['analysis/extra_results.json','analysis/inputs/adjudication_pairs.csv']
manifest={'source_inputs':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'outputs':OUTPUTS,'plot_data_sha256':hashlib.sha256((OUT/'plot_data.json').read_bytes()).hexdigest(),'versions':{'numpy':np.__version__,'matplotlib':matplotlib.__version__}}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('Generated seven standalone figures (PNG and SVG); source statistics unchanged.')
