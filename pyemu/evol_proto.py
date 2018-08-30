import os
import numpy as np
import pandas as pd

import pyemu
from pyemu.smoother import EnsembleMethod


class ParetoObjFunc(object):
    def __init__(self, pst, obj_function_dict, logger):

        self.logger = logger
        self.pst = pst
        self.max_distance = 1.0e+30
        obs = pst.observation_data
        pi = pst.prior_information
        self.obs_dict, self.pi_dict = {}, {}
        for name,direction in obj_function_dict.items():

            if name in obs.obsnme:
                if direction.lower().startswith("max"):
                    self.obs_dict[name] = "max"
                elif direction.lower().startswith("min"):
                    self.obs_dict[name] = "min"
                else:
                    self.logger.lraise("unrecognized direction for obs obj func {0}:'{1}'".\
                                       format(name,direction))
            elif  name in pi.pilbl:
                if direction.lower().startswith("max"):
                    self.pi_dict[name] = "max"
                elif direction.lower().startswith("min"):
                    self.pi_dict[name] = "min"
                else:
                    self.logger.lraise("unrecognized direction for pi obj func {0}:'{1}'".\
                                       format(name,direction))
            else:
                self.logger.lraise("objective function not found:{0}".format(name))

        def is_less_const(oname):
            constraint_tags = ["l_","less"]
            return True in [True for c in constraint_tags if oname.startswith(c)]

        def is_greater_const(oname):
            constraint_tags = ["g_","greater"]
            return True in [True for c in constraint_tags if oname.startswith(c)]

        self.less_obs = obs.loc[obs.obgnme.apply(lambda x: is_less_const(x)),"obsnme"]
        self.greater_obs = obs.loc[obs.obgnme.apply(lambda x: is_greater_const(x)), "obsnme"]
        self.less_pi = pi.loc[pi.obgnme.apply(lambda x: is_less_const(x)), "pilbl"]
        self.greater_pi = pi.loc[pi.obgnme.apply(lambda x: is_greater_const(x)), "pilbl"]

        self.logger.statement("{0} obs objective functions registered".\
                              format(len(self.obs_dict)))
        for name,direction in self.obs_dict.items():
            self.logger.statement("obs obj function: {0}, direction: {1}".\
                                  format(name,direction))

        self.logger.statement("{0} pi objective functions registered". \
                              format(len(self.pi_dict)))
        for name, direction in self.pi_dict.items():
            self.logger.statement("pi obj function: {0}, direction: {1}". \
                                  format(name, direction))

    def is_feasible(self, obs_df, par_df):
        """identify which candidate solutions in obs_df and par_df (rows)
        are feasible with respect obs constraints (obs_df) and prior
        information constraints (par_df)

        Parameters
        ----------
        obs_df : pandas.DataFrame
            a dataframe with columns of obs names and rows of realizations
        par_df : pandas.DataFrame
            a dataframe with columns of par names and rows of realizations

        Returns
        -------
        is_feasible : pandas.DataFrame
            dataframe with obs_df.index, par_df.index and bool series

        """
        pass

    def is_dominated(self, obs_df):
        """identify which candidate solutions are pareto dominated

        Parameters
        ----------
        obs_df : pandas.DataFrame
            dataframe with columns of observation names and rows of realizations

        Returns
        -------
        is_dominated : pandas.DataFrame
            dataframe with index of obs_df and bool series
        """
        pass

    def crowd_distance(self,obs_df):
        """determine the crowding distance for each candidate solution

        Parameters
        ----------
        obs_df : pandas.DataFrame
            dataframe with columns of observation names and rows of realizations

        Returns
        -------
        crowd_distance : pandas.DataFrame
            dataframe with index of obs_df and value of crowd distance
        """

        # initialize the distance container
        crowd_distance = pd.DataFrame(data=0.0,index=obs_df.index,columns=["crowd_distance"])

        for name,direction in self.obs_dict.items():
            # make a copy - wasteful, but easier
            obj_df = obs_df.loc[:,name].copy()

            # sort so that largest values are first
            obj_df.sort_values(ascending=False,inplace=True)

            # set the ends so they are always retained
            crowd_distance.loc[obj_df.index[0]] += self.max_distance
            crowd_distance.loc[obj_df.index[-1]] += self.max_distance

            # process the vector
            i = 1
            for idx in obj_df.index[1:-1]:
                crowd_distance.loc[idx] += obj_df.iloc[i-1] - obj_df.iloc[i+1]
                i += 1

        return crowd_distance





class EvolAlg(EnsembleMethod):
    def __init__(self, pst, parcov = None, obscov = None, num_slaves = 0, use_approx_prior = True,
                 submit_file = None, verbose = False, port = 4004, slave_dir = "template"):
        super(EvolAlg, self).__init__(pst=pst, parcov=parcov, obscov=obscov, num_slaves=num_slaves,
                                      submit_file=submit_file, verbose=verbose, port=port,
                                      slave_dir=slave_dir)


    def initialize(self,obj_function_names):

        self.obj_func = ParetoObjFunc(self.pst,obj_function_names, self.logger)
        pass

    def update(self):
        pass











