import os
from copy import deepcopy
import numpy as np
import pandas as pd

from .utils import concat_dicts, make_hash

def gen_estimators(pipeline, exp_dict, estimators=None):
    exp = {}
    gen, kwargs = pipeline.popleft()
    for estimator in estimators:
        name = estimator.__name__
        exp[name] = deepcopy(exp_dict)
        exp[name]['estimator'] = estimator

        for e in gen(deepcopy(pipeline), exp[name], **kwargs):
            exp[name] = e

    yield exp


def gen_repl(pipeline, exp_dict, n=10):
    exp = {}
    gen, kwargs = pipeline.popleft()

    for repl in range(n):
        exp[repl] = deepcopy(exp_dict)
        exp[repl]['gen_data_params']['seed'] += repl
        for e in gen(deepcopy(pipeline), exp[repl], **kwargs):
            exp[repl] = e

    yield exp


def gen_params(pipeline, exp_dict, evals=5):
    gen, kwargs = pipeline.popleft()
    exp = {}
    est = exp_dict['estimator']
    param_ranges = est.param_ranges
    base_params = {k: (v[1] - v[0])/2. for k, v in param_ranges.iteritems()}
    for param_name, param_range in param_ranges.iteritems():
        params = deepcopy(base_params)
        exp[param_name] = {}
        for val in np.linspace(param_range[0], param_range[1], evals):
            exp[param_name][val] = deepcopy(exp_dict)
            params[param_name] = val
            exp[param_name][val]['gen_data_params']['params'] = params

            for e in gen(deepcopy(pipeline), exp[param_name][val], **kwargs):
                exp[param_name][val] = e

        yield exp


def call_exp(pipeline, exp_dict, view=None, **kwargs):
    if view is None:
        recovered = run_exp(exp_dict, **kwargs)
    else:
        recovered = view.apply_async(run_exp, exp_dict, **kwargs)

    yield recovered
    raise StopIteration


def run_exp(exp_dict, folder='sims', action='collect'):
    import os
    import pandas as pd
    import numpy as np

    h = make_hash(exp_dict)

    fname = os.path.join(folder, '%s.dat' % str(h))
    if os.path.isfile(fname) and (action != 'rerun'):
        if action == 'collect':
            stats = pd.read_pickle(fname)
            print "Loading job %s" % h
            run_estimation=False
            if len(stats) == 0:
                return stats
        elif action == 'run':
            stats = pd.load(fname)
            print "Skipping job %s" % h
            return stats
        elif action == 'delete':
            os.remove(fname)
            return pd.DataFrame()
        else:
            raise ValueError('Unknown action')
    else:
        #create a file that holds the results and to make sure that no other worker would start
        #working on this job
        pd.DataFrame().to_pickle(fname)

        est = exp_dict['estimator']()
        data = est.gen_data(**exp_dict['gen_data_params'])

        try:
            recovered = est.estimate(data, **exp_dict['estimate_params'])
            recovered.to_pickle(fname)
        except:
            return np.nan

        return recovered
