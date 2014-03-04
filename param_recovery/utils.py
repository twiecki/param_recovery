import os
import pandas as pd
from copy import copy, deepcopy
from collections import deque
from IPython.parallel.client.asyncresult import AsyncResult

import param_recovery

def make_hash(o):
    """
    Makes a hash from a dictionary, list, tuple or set to any level, that contains
    only other hashable types (including any lists, tuples, sets, and
    dictionaries).
    """
    import hashlib
    import cPickle
    from copy import deepcopy
    try:
        return hashlib.md5(cPickle.dumps(o)).hexdigest()
    except (TypeError, cPickle.PicklingError):
        oo = deepcopy(o)
        oo['estimator'] = oo['estimator'].__name__
        return hashlib.md5(cPickle.dumps(oo)).hexdigest()


def concat_dicts(d, names=()):
    name = names.pop(0) if len(names) != 0 else None

    if isinstance(d, (pd.DataFrame, pd.Series)):
        return d # End recursion
    elif isinstance(d, AsyncResult):
        return d.get()
    else:
        sublevel_d = {}
        for k, v in d.iteritems():
            sublevel_d[k] = concat_dicts(v, names=copy(names))
        return pd.concat(sublevel_d, names=[name])


def run_pipeline(pipeline, exp_dict):
    pipeline = deque(pipeline)
    gen, kwargs = pipeline.popleft()
    return concat_dicts(gen(deepcopy(pipeline), exp_dict, **kwargs).next())
