param_recovery
==============

Suite to test whether your model can recover parameters. Experimental.

This solves a problem I've been having for a while. The beginnings of
a parallizable and flexible framework to test whether your model can
recover known parameters. Recovery studies on simulated data for which
you know the parameters is critical.

This framework follows a functional design where you can build
recovery pipelines.

```python
from param_recovery import generators
from param_recovery import run_pipeline

class TestEstimator(object):
    param_ranges = {'test1': (0, .5),
                    'test2': (0, 2),
                    'test3': (0, 2),
                    'test4': (0, 2),
                    'test5': (-5, 5),
                    }

    def gen_data(self, params=None, seed=123, size=50):
    	# code to generate a data set given parameters
        return data

    def estimate(self, data, method='Nelder-Mead'):
        # Estimate your model and return fitted parameters
        return params

pipeline = [(generators.estimator, {'estimators': [TestEstimator]}), # run one estimator
            (generators.single_param_eval, {'evals': 20}), # Evaluate every parameter over a range spanning 20 values
            (generators.replicate, {'n': 10}), # Run every recovery 10 times with different seeds
            (call_exp, {'view': None}), # Actually run the recovery, view can be an IPython parallel view
           ]

experiment = {'estimator': [TestEstimator],
              'gen_data_params': {'size': 100, 'seed': 123},
              'estimate_params': {'method': 'Nelder-Mead'}
              }

results = run_pipeline(pipeline, experiment)
# results will be a multi-index dataframe with every
# estimator, parameter setting, replication. You can
# easily analyze this to see whether the correct
# parameters where recovered.
```
