"""Replay acquisition exactly, run repository boundaries, supplement audit costs."""
import argparse
import platform
import subprocess
import sys
import time
import numpy as np
import torch
import phase6_edit as study
import phase6_energy as energy


def run(out):
    out = study.fresh(out)
    start = time.perf_counter()
    energy.train(out / 'acquisition-replay')
    original = study.load(study.PHASE / 'runs/acquisition/model.json')
    replay = study.load(out / 'acquisition-replay/model.json')
    assert study.load(out / 'acquisition-replay/examples.json') == study.load(study.PHASE / 'runs/acquisition/examples.json')
    fits = [(original, replay)] + [(a['fit'], b['fit']) for a, b in zip(original['leave_one_task_out'], replay['leave_one_task_out'])]
    for a, b in fits:
        np.testing.assert_array_equal(a['weights'], b['weights'])
        assert a['trace'] == b['trace']
        assert a['pair_ranking_accuracy'] == b['pair_ranking_accuracy']
    command = [sys.executable, '-m', 'unittest', 'discover', '-s', 'scripts', '-p', 'test_*.py', '-v']
    test_start = time.perf_counter()
    tests = subprocess.run(command, cwd=study.ROOT, capture_output=True, text=True)
    study.dump(out / 'repository-tests.json', dict(command=command, returncode=tests.returncode,
        stdout=tests.stdout, stderr=tests.stderr, seconds=time.perf_counter()-test_start))
    assert tests.returncode == 0
    audit = study.load(study.PHASE / 'runs/audit/audit.json')
    replays = study.load(study.PHASE / 'runs/audit/replayed-tests.json')
    diagnosis = study.load(study.PHASE / 'runs/semantic-diagnosis/summary.json')
    study.dump(out / 'verification.json', dict(timestamp=study.stamp(), script_sha256=study.sha(__file__),
        python=platform.python_version(), torch=torch.__version__, numpy=np.__version__,
        exact_example_replay=True, bit_identical_fits=len(fits), repository_tests_pass=True,
        seconds=time.perf_counter()-start, reader_calls=0,
        supplementary_costs=dict(audit_pytest_invocations=audit['audit_pytest_invocations'],
            audit_pytest_seconds=sum(r[k]['seconds'] for r in replays for k in ['public', 'heldout']),
            semantic_diagnosis=diagnosis,
            verification_fit_seconds=sum(b['seconds'] for _, b in fits),
            verification_example_seconds=replay['example_construction_seconds']),
        timing_gaps=['Six outer transfer records() scans and one interface-validation scan were executed but their timers discarded; each scans eight source files. Inner attempt scans are timed separately.',
            'Do not interpret saved representation/selection times as exhaustive wall-clock costs. Copying, hashing, prompt serialization and authoring overhead are incomplete.'],
        chronology_correction='Transfer task definitions were authored in phase6_transfer.py after acquisition and before freeze. They were serialized/executed only after freeze. Frozen wording saying generated after freeze is too strong. No task definitions are inputs to acquisition; this is not investigator-blinded transfer.'))
    print({'exact_fits': len(fits), 'tests_returncode': tests.returncode})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--out', required=True)
    run(parser.parse_args().out)
