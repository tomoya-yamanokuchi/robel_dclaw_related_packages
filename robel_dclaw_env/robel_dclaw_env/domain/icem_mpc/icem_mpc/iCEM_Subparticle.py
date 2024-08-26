import os
import copy
import time
import numpy as np
from typing import Any
import sys; import pathlib; p = pathlib.Path(); sys.path.append(str(p.cwd()))
from robel_dclaw_env.domain.forward_model_multiprocessing.ForwardModelMultiprocessing import ForwardModelMultiprocessing
from .population.PopulationSampingDistribution import PopulationSampingDistribution
from .population.PopulationSizeScheduler import PopulationSizeScheduler
from .population.PopulationSampler import PopulationSampler
from .population.EliteSetQueue import EliteSetQueue
from .SampleAugmenter import SampleAugmenter
from .visualization.VisualizationCollection import VisualizationCollection
from .CostHistory import CostHistory



class iCEM_Subparticle:
    def __init__(self,
            forward_model                : Any,
            forward_model_progress_check : Any,
            cost_function                : Any,
            repository                   : Any,
            config,
        ):
        self.forward_model                = forward_model
        self.forward_model_progress_check = forward_model_progress_check
        self.cost_function                = cost_function
        self.config                       = config

        self.population_sampling_dist     = PopulationSampingDistribution(config)
        self.population_size_scheduler    = PopulationSizeScheduler(config)
        self.population_sampler           = PopulationSampler(config)
        self.sample_augmentor             = SampleAugmenter(config, self._sample)
        self.elite_set_queue              = EliteSetQueue(config)

        self.time_now       = str(time.time())
        self.vis_collection = VisualizationCollection()
        self.vis_collection.append("cost",                        repository)
        self.vis_collection.append("subparticle_simulated_paths", repository)
        self.vis_collection.append("sample",                      repository)
        self.vis_collection.append("total_subparticle_sample",    repository)
        # self.vis_collection.append("unit_subparticle_sample",     repository)

        self.cost_history    = CostHistory()
        self.iter_outer_loop = None


    def reset(self):
        if self.iter_outer_loop is None:
            self.iter_outer_loop = 0
        else: self.iter_outer_loop += 1
        self.population_sampling_dist.reset_init_distribution(self.iter_outer_loop)
        self.total_sample_size_in_optimze = 0
        self.total_proc_time_in_optimze   = 0


    def print_info(self, iter_inner_loop, num_sample):
        if self.config.verbose:
            print("[iCEM] iter_outer={} | iter_inner={}/{} | decayed_sample_size={: 4}".format(
                self.iter_outer_loop, iter_inner_loop, self.config.num_cem_iter-1, num_sample), end=' | ')


    def _sample(self, num_sample):
        return self.population_sampler.sample(
            mean                   = self.population_sampling_dist.mean,
            std                    = self.population_sampling_dist.std,
            num_sample             = num_sample,
            colored_noise_exponent = self.config.colored_noise_exponent,
        )


    def optimize(self, constant_setting, target):
        for i in range(self.config.num_cem_iter):
            time_start               = time.time()
            num_sample_i             = self.population_size_scheduler.decay(i); self.print_info(i, num_sample_i)
            samples                  = self._sample(num_sample_i)
            samples                  = self.sample_augmentor.add_minmaxmean_action_sample(samples)
            samples                  = self.sample_augmentor.add_fraction_of_elite_set(samples, self.elite_set_queue, i)
            samples                  = self.sample_augmentor.add_mean_action_at_last_iteration(samples, self.population_sampling_dist.mean, i)
            num_samples              = samples.shape[0]
            self.total_sample_size_in_optimze += num_samples
            if self.config.verbose: print("total_sample_size={: 4}".format(num_samples), end=' | ')
            # ----------------------------
            subparticle_group_list   = self._extend_as_subparticle(samples, i)
            perturbated_samples      = np.concatenate(subparticle_group_list)
            forward_results          = self._forward(constant_setting, perturbated_samples)
            cost                     = self.get_cost(forward_results, target, num_samples)
            assert cost.shape == (num_samples,), print("{} != {}".format(cost.shape, (num_samples,)))
            # ----------------------------
            index_elite              = self._get_index_elite(cost)
            best_elite_sample        = samples[index_elite[:1]]
            forward_results_progress = self._forward_progress_check(constant_setting, best_elite_sample, i, target)
            cost_elite               = self.get_cost(forward_results_progress, target, 1)
            elites                   = copy.deepcopy(samples[index_elite])
            self.elite_set_queue.append(elites)
            self.population_sampling_dist.update_distribution(elites)
            self.cost_history.append(cost)
            # ---- visualize ----
            if self.config.save_visualization_dir is None: continue
            self.vis_collection.plot("cost"  ,                      cost, i, self.iter_outer_loop, num_samples)
            self.vis_collection.plot("subparticle_simulated_paths", forward_results, index_elite, target, i, self.iter_outer_loop, num_samples)
            self.vis_collection.plot("sample",                      samples, samples[index_elite], i, self.iter_outer_loop, num_samples)
            # self.vis_collection.plot("total_subparticle_sample",    subparticle_group_list, index_elite, i, self.iter_outer_loop, perturbated_samples.shape[0])
            # ---- time count ----
            # import ipdb; ipdb.set_trace()
            self.update_total_process_time(time_start)
        if self.config.verbose: self._print_optimize_info()
        return {
            "cost"              : cost,
            "state"             : forward_results_progress["state"],
            # "best_elite_action" : forward_results_progress["task_space_ctrl"],
            "best_elite_ctrl_t" : forward_results_progress["ctrl_t"],
            "best_elite_sample" : best_elite_sample[0, 0],
        }


    def _extend_as_subparticle(self, samples, iter_inner_loop):
        noise = np.random.randn(self.config.num_subparticle, self.config.planning_horizon, self.config.dim_action) * self.config.std_subparticle
        num_samples = samples.shape[0]
        subparticle_group_list = []
        for i in range(num_samples):
            perturbated_samples = self.population_sampler.clip(samples[i][np.newaxis, :, :] + noise)
            subparticle_group_list.append(perturbated_samples)
            # self.vis_collection.plot("unit_subparticle_sample", perturbated_samples, i, iter_inner_loop, self.iter_outer_loop, self.config.num_subparticle)
        return subparticle_group_list


    def _get_index_elite(self, cost):
        index_elite = np.argsort(np.array(cost))[:self.config.num_elite]
        if self.config.verbose: print("min cost={:.3f} (submean={:.3f})".format(
            cost[index_elite][0], (cost[index_elite][0] / self.config.num_subparticle)), end=' | ')
        return index_elite


    def get_cost(self, forward_results, target, num_samples):
        cost = self.cost_function(forward_results=forward_results, target=target, num_divide=num_samples)
        # cost_naive        = self.cost_function(forward_results=forward_results, target=target)
        # cost_subparticles = np.array_split(cost_naive, indices_or_sections=num_samples, axis=0)
        # cost_subparticles = np.stack(cost_subparticles, axis=0)
        # cost              = np.sum(cost_subparticles, axis=-1)
        assert cost.shape == (num_samples,), print("{} != {}".format(cost.shape, (num_samples,)))
        if (self.config.verbose) and (num_samples==1): print("cost_elite={: .3f}".format(float(cost)), end=" | ")
        return cost


    def _forward(self, constant_setting, actions):
        if self.config.debug: actions = actions[:1]
        multiproc = ForwardModelMultiprocessing(verbose=False)
        results, proc_time = multiproc.run(
            rollout_function = self.forward_model,
            constant_setting = constant_setting,
            ctrl             = actions,
        )
        if self.config.verbose_additional: print("time={:.3f}".format(proc_time), end=' | ')
        return results


    def _forward_progress_check(self, constant_setting, best_elite_action, iter_inner_loop, target):
        assert best_elite_action.shape[0] == 1
        multiproc = ForwardModelMultiprocessing(verbose=False, result_aggregation=False)
        results, proc_time = multiproc.run(
            rollout_function = self.forward_model_progress_check,
            constant_setting = {
                **constant_setting,
                **{
                    "iter_outer_loop" : self.iter_outer_loop,
                    "iter_inner_loop" : iter_inner_loop,
                    "save_fig_dir"    : os.path.join(self.config.save_visualization_dir, self.time_now),
                    "dataset_name"    : self.time_now,
                    "target"          : target,
                },
            },
            ctrl = best_elite_action,
        )
        return results


    def update_total_process_time(self, time_start):
        elapsed_time = time.time() - time_start
        self.total_proc_time_in_optimze += elapsed_time
        if self.config.verbose:
            if self.config.is_verbose_newline: print("time={:.3f}".format(elapsed_time))
            else: print("time={:.3f}".format(elapsed_time), end=' | ')


    def _print_optimize_info(self):
        print("\n")
        print("------------------------------------------------")
        print("    total_sample_size_in_optimze : {}           ".format(self.total_sample_size_in_optimze))
        print("    total_proc_time_in_optimze   : {:.2f} [sec]".format(self.total_proc_time_in_optimze))
        print("------------------------------------------------")
