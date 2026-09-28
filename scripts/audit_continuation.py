"""Audit frozen methods, source separation, replay and complete reader evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from phase2_assets import dump
from phase2_reader import parse,grade

ROOT=Path(__file__).resolve().parents[1]


def read(name):return json.loads((ROOT/name).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def clusters(labels):
    groups=[]
    for label in labels:
        components=set(label['component_ids']);ids={label['id']}
        matches=[g for g in groups if g[0]&components]
        for group in matches:
            components|=group[0];ids|=group[1];groups.remove(group)
        groups.append((components,ids))
    return [sorted(g[1]) for g in groups]


def paired(a,b,groups):
    ids=sorted(set(a)&set(b))
    deltas={i:float(a[i])-float(b[i]) for i in ids}
    use=[[i for i in group if i in deltas] for group in groups]
    use=[g for g in use if g]
    rng=np.random.default_rng(881)
    values=[]
    for _ in range(5000):
        draw=[use[i] for i in rng.integers(0,len(use),len(use))]
        values.append(sum(deltas[i] for g in draw for i in g)/sum(map(len,draw)))
    return dict(n=len(ids),clusters=len(use),wins=sum(d>0 for d in deltas.values()),
                losses=sum(d<0 for d in deltas.values()),ties=sum(d==0 for d in deltas.values()),
                mean_difference=float(np.mean(list(deltas.values()))),
                cluster_bootstrap_percentile_95=list(map(float,np.quantile(values,[.025,.975]))),
                interpretation='Descriptive cluster resampling of this cohort; no population or multiplicity-adjusted claim')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--require-reader',action='store_true');args=parser.parse_args()
    if args.out.exists():raise RuntimeError('Audit output exists')
    freeze=read('phase2/freeze.json')
    checks={p:sha(ROOT/p)==digest for p,digest in freeze['files'].items()}
    old=read('phase2/runs/semantic-pairwise/checkpoint.json')
    rebuilt=read('.cache/phase2/verification-training/checkpoint.json')
    checks['semantic_training_checkpoint_exact_replay']=old==rebuilt
    outcomes=read('phase2/runs/confirmation-selection/outcomes.json')
    replay=read('.cache/phase2/verification-selection/outcomes.json')
    stable=lambda rows:[{k:v for k,v in row.items() if k!='seconds'} for row in rows]
    checks['confirmation_selection_exact_replay']=stable(outcomes)==stable(replay)
    scaling=read('phase3/runs/scaling/outcomes.json')
    scaling_replay=read('.cache/phase3-replay/outcomes.json')
    exclude={'wall_seconds','cpu_seconds','feature_seconds','coefficient_forward_seconds'}
    stable_scaling=lambda rows:[{k:v for k,v in r.items() if k not in exclude} for r in rows]
    checks['scaling_non_timing_exact_replay']=stable_scaling(scaling)==stable_scaling(scaling_replay)
    labels={split:read(f'.cache/phase2/partitions/{split}-labels.json') for split in ['train','development','confirmation']}
    components={split:{c for row in rows for c in row['component_ids']} for split,rows in labels.items()}
    checks['component_disjoint_splits']=all(not components[a]&components[b] for a,b in
                     [('train','development'),('train','confirmation'),('development','confirmation')])
    examples={split:read(f'.cache/phase2/partitions/{split}-inputs.json') for split in labels}
    paragraphs={split:{hashlib.sha256((p['title']+'\n'+p['text']).encode()).hexdigest()
                      for row in rows for p in row['paragraphs']} for split,rows in examples.items()}
    overlap={a+'__'+b:len(paragraphs[a]&paragraphs[b]) for a,b in
             [('train','development'),('train','confirmation'),('development','confirmation')]}
    eligible_paragraphs={split:{hashlib.sha256((p['title']+'\n'+p['text']).encode()).hexdigest()
                      for row in rows if len(row['paragraphs'])==20 for p in row['paragraphs']} for split,rows in examples.items()}
    eligible_overlap={a+'__'+b:len(eligible_paragraphs[a]&eligible_paragraphs[b]) for a,b in
             [('train','development'),('train','confirmation'),('development','confirmation')]}
    groups=clusters(labels['confirmation'])
    sel={arm:{r['id']:r['complete'] for r in outcomes if r['arm']==arm} for arm in {r['arm'] for r in outcomes}}
    recon=[json.loads(line) for line in (ROOT/'.cache/reconnaissance/MuSiQue/raw-dev-first3.jsonl').read_text().splitlines()]
    prior_ids={r['id'] for r in recon}
    prior_components={str(d['id']) for r in recon for d in r['decomposed_instances']}
    previously_exposed={r['id'] for r in labels['confirmation'] if set(r['component_ids'])&prior_components}
    strict={arm:{i:v for i,v in values.items() if i not in previously_exposed} for arm,values in sel.items()}
    result=dict(checks=checks,source_paragraph_overlap=overlap,eligible_source_paragraph_overlap=eligible_overlap,
           overlap_note='Original overlap field includes all reserved rows; eligible field excludes non-20 pools.',confirmation_component_clusters=groups,
           support_comparison={arm:paired(sel['exact'],sel[arm],groups) for arm in ['ordinary_1.0','learned_unary','relaxed','relaxed_swap']},
           reconnaissance_exposure=dict(exact_question_overlap=sorted(prior_ids&set(sel['exact'])),
                component_related_questions=sorted(previously_exposed),
                note='Prior reconnaissance was not excluded by the original partitioner. Retain the frozen cohort and disclose this pre-exposure.'),
           strict_exposure_sensitivity={arm:paired(strict['exact'],strict[arm],groups) for arm in ['ordinary_1.0','learned_unary']},
           reproduction_costs=dict(training=read('.cache/phase2/verification-training/costs.json'),
                 selection=read('.cache/phase2/verification-selection/summary.json'),
                 selection_representation=read('.cache/phase2/verification-selection/representation.json'),
                 scaling=read('.cache/phase3-replay/summary.json'),
                 scaling_shared_representation={key:sum(r[key] for r in scaling_replay if r['method']=='exact')
                      for key in ['feature_seconds','coefficient_forward_seconds']}))
    readerpath=ROOT/'phase2/runs/confirmation-reader/costs.json'
    if args.require_reader:assert readerpath.exists(),'Reader not complete'
    if readerpath.exists():
        reader=read('phase2/runs/confirmation-reader/outcomes.json')
        by_label={l['id']:l for l in labels['confirmation']}
        grade_checks=[];fallback_checks=[];finished={};tokens={};length_stops=0;cached_tokens=0
        for path in sorted((ROOT/'phase2/runs/confirmation-reader').glob('*-response.json')):
            response=json.loads(path.read_text())
            key=path.name.removesuffix('-response.json');finished[key]=response
            request=read(f'phase2/runs/confirmation-reader/{key}-request.json')
            checks[f'payload_hash_{key}']=hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()==key
            length_stops+=response['response'].get('choices',[{}])[0].get('finish_reason')=='length'
            usage=response['response'].get('usage',{});tokens[key]=usage
            cached_tokens+=usage.get('prompt_tokens_details',{}).get('cached_tokens',0)
        for row in reader:
            answer=parse(finished[row['request_hash']]['response'])
            scored=grade(answer,by_label[row['id']],row['selected'])
            grade_checks.append(all(row[k]==v for k,v in scored.items()))
            full=next(r for r in reader if r['id']==row['id'] and r['arm']=='all')
            fallback=not answer['answer'].strip() or not set(answer['citations']).issubset(row['selected']) or bool(answer.get('parse_error'))
            final=parse(finished[full['request_hash']]['response']) if fallback else answer
            fallback_checks.append(row['after_fallback']==grade(final,by_label[row['id']],full['selected'] if fallback else row['selected']))
        checks['all_raw_reader_grades_reproduce']=all(grade_checks)
        checks['all_recorded_reader_answers_reproduce']=all(parse(finished[r['request_hash']]['response'])==r['answer'] for r in reader)
        checks['all_fallback_grades_reproduce']=all(fallback_checks)
        checks['all_eight_arms_have_24_outcomes']=len(reader)==192 and all(sum(r['arm']==arm for r in reader)==24 for arm in {r['arm'] for r in reader})
        checks['reader_code_matches_freeze']=read('phase2/runs/confirmation-reader/costs.json')['script_sha256']==freeze['files']['scripts/phase2_reader.py']
        original_costs=read('phase2/runs/confirmation-reader/costs.json')
        checks['physical_reader_request_count']=original_costs['requests']==len(finished)
        for field in ['prompt_tokens','completion_tokens']:
            checks['physical_reader_'+field]=original_costs[field]==sum(v['response'].get('usage',{}).get(field,0) for v in finished.values())
        checks['exact_and_relaxed_reader_contexts_identical']=all(
            next(r['selected'] for r in reader if r['id']==row['id'] and r['arm']=='relaxed_swap')==row['selected']
            for row in reader if row['arm']=='exact')
        readerstats={arm:{r['id']:r['complete'] for r in reader if r['arm']==arm} for arm in {r['arm'] for r in reader}}
        result['reader_comparison']={arm:paired(readerstats['exact'],readerstats[arm],groups) for arm in ['ordinary_1.0','learned_unary','all']}
        result['reader_previously_exposed_ids']=sorted(previously_exposed & set(readerstats['exact']))
        result['reader_details']=dict(unique_responses=len(finished),length_stops=length_stops,
              returned_model_identities=sorted({str(v['response'].get('model')) for v in finished.values()}),
              reported_cached_prompt_tokens=cached_tokens,actual_cases=len({r['id'] for r in reader}),
              complete_support_not_sufficient_for_reader=sum(r['retrieved_complete'] and not r['complete'] for r in reader if r['arm']=='exact'),
              exact_correct_answer_missing_support=sum(r['answer_em'] and not r['complete'] for r in reader if r['arm']=='exact'))
        result['reader_failure_attribution']={arm:dict(
            length_stops=sum(finished[r['request_hash']]['response'].get('choices',[{}])[0].get('finish_reason')=='length' for r in reader if r['arm']==arm),
            parse_failures=sum(bool(r['answer'].get('parse_error')) for r in reader if r['arm']==arm),
            selection_missing_support=sum(not r['retrieved_complete'] for r in reader if r['arm']==arm),
            selected_all_support_but_answer_em_failure=sum(r['retrieved_complete'] and not r['answer_em'] for r in reader if r['arm']==arm),
            selected_all_support_correct_answer_but_citation_failure=sum(r['retrieved_complete'] and r['answer_em'] and not r['complete'] for r in reader if r['arm']==arm),
            complete=sum(r['complete'] for r in reader if r['arm']==arm)) for arm in ['all','ordinary_1.0','learned_unary','exact','relaxed_swap','oracle_support']}
        for arm,counts in result['reader_failure_attribution'].items():
            group=[r for r in reader if r['arm']==arm]
            counts['candidate_pool_complete']=sum(set(by_label[r['id']]['supports']).issubset(
                {p['idx'] for e in examples['confirmation'] if e['id']==r['id'] for p in e['paragraphs']}) for r in group)
        budgetdir=ROOT/'phase2/runs/reader-budget-diagnostic'
        if (budgetdir/'costs.json').exists():
            repaired=read('phase2/runs/reader-budget-diagnostic/outcomes.json')
            eligibility=read('phase2/runs/reader-budget-diagnostic/eligibility.json')['requests']
            checks['budget_all_and_only_public_length_stops']=eligibility==sorted(k for k,v in finished.items() if v['response'].get('choices',[{}])[0].get('finish_reason')=='length')
            effective=dict(finished);actual_keys=[];prefixes=[]
            for path in budgetdir.glob('*-request.json'):
                payload=json.loads(path.read_text());newkey=path.name.removesuffix('-request.json')
                checks[f'budget_payload_hash_{newkey}']=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()==newkey
                checks[f'budget_cap_{newkey}']=payload['max_tokens']==4096
                payload['max_tokens']=1024;oldkey=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
                actual_keys.append(oldkey)
                effective[oldkey]=json.loads((budgetdir/f'{newkey}-response.json').read_text())
                oldtext=finished[oldkey]['response'].get('choices',[{}])[0].get('message',{}).get('content','')
                newtext=effective[oldkey]['response'].get('choices',[{}])[0].get('message',{}).get('content','')
                prefix=next((i for i,(a,b) in enumerate(zip(oldtext,newtext)) if a!=b),min(len(oldtext),len(newtext)))
                prefixes.append(dict(original_request=oldkey,old_chars=len(oldtext),new_chars=len(newtext),
                    common_prefix_chars=prefix,exact_extension=newtext.startswith(oldtext)))
            checks['budget_requests_only_change_cap']=sorted(actual_keys)==eligibility
            valid=[];fallback_valid=[]
            for row in repaired:
                answer=parse(effective[row['request_hash']]['response'])
                valid.append(all(row[k]==v for k,v in grade(answer,by_label[row['id']],row['selected']).items()))
                full=next(r for r in repaired if r['id']==row['id'] and r['arm']=='all')
                fallback=not answer['answer'].strip() or not set(answer['citations']).issubset(row['selected']) or bool(answer.get('parse_error'))
                final=parse(effective[full['request_hash']]['response']) if fallback else answer
                fallback_valid.append(row['after_fallback']==grade(final,by_label[row['id']],full['selected'] if fallback else row['selected']))
            checks['budget_raw_grades_reproduce']=all(valid)
            checks['budget_recorded_answers_reproduce']=all(parse(effective[r['request_hash']]['response'])==r['answer'] for r in repaired)
            checks['budget_fallback_grades_reproduce']=all(fallback_valid)
            checks['budget_selected_evidence_unchanged']=all(row['selected']==next(r['selected'] for r in reader if r['id']==row['id'] and r['arm']==row['arm']) for row in repaired)
            budgetstats={arm:{r['id']:r['complete'] for r in repaired if r['arm']==arm} for arm in {r['arm'] for r in repaired}}
            result['budget_reader_comparison']={arm:paired(budgetstats['exact'],budgetstats[arm],groups) for arm in ['ordinary_1.0','learned_unary','all']}
            result['budget_prefix_diagnostics']=dict(exact_extensions=sum(r['exact_extension'] for r in prefixes),requests=len(prefixes),details=prefixes,
                note='A retry may change output before the old cap despite requested seed/temperature. Such cases are not pure continuation of a fixed token sequence.')
            checks['budget_returned_model_identity_unchanged']={effective[k]['response'].get('model') for k in eligibility}=={finished[k]['response'].get('model') for k in eligibility}
    result['all_checks_passed']=all(checks.values())
    dump(args.out,result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['checks','reproduction_costs','confirmation_component_clusters']},indent=2))
    assert result['all_checks_passed'],[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
