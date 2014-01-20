import unittest
from copy import deepcopy
import numpy as np
import pandas as pd

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
        import numpy as np
        import pandas as pd
        np.random.seed(seed)
        data = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
        return data

    def estimate(self, data, method='Nelder-Mead'):
        # estimate
        return data

def gather(pipeline, exp_dict):
    del exp_dict['estimator']
    yield pd.DataFrame(exp_dict)
    raise StopIteration

class Test(unittest.TestCase):
    def runTest(self):
        pass

    def test_pipeline(self):
        evals = 5
        n = 3
	pipeline = [(generators.estimator, {'estimators': [TestEstimator]}),
                    (generators.param_wise_equal_spacing, {'evals': evals}),
                    (generators.replicator, {'n': n}),
                    (gather, {}),
                   ]

        experiment = {'estimator': TestEstimator,
                      'gen_data_params': {'size': 100, 'seed': 123},
                      'estimate_params': {'method': 'Nelder-Mead'}
                      }

        param_names = TestEstimator.param_ranges.keys()
        result = run_pipeline(pipeline, experiment)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.keys()[0], 'TestEstimator')
        self.assertEqual(set(result['TestEstimator'].keys()), set(param_names))
        for param_name in param_names:
            self.assertEqual(set(result['TestEstimator'][param_name].keys()),
                             set(np.linspace(TestEstimator.param_ranges[param_name][0],
                                             TestEstimator.param_ranges[param_name][1],
                                             evals)))

            for exp_val, eval_dict in result['TestEstimator'][param_name].iteritems():
                self.assertEqual(len(eval_dict.keys()), n)
                for df in eval_dict.itervalues():
                    self.assertEqual(exp_val, df.ix['params', 'gen_data_params'][param_name])
