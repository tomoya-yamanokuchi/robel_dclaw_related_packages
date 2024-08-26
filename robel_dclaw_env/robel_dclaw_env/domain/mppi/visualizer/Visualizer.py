import os
import time
from .TrajectoryVisualization import TrajectoryVisualization
from .VlaveTrajectoryVisualization import VlaveTrajectoryVisualization



class Visualizer:
    def __init__(self,
            dim_path,
            dim_action,
            planning_horizon,
            lower_bound_simulated_path,
            upper_bound_simulated_path,
            lower_bound_sampling,
            upper_bound_sampling,
            lower_bound_cusum_action,
            upper_bound_cusum_action,
            lower_bound_action,
            upper_bound_action,
            save_dir,
            figsize = (7, 4)
            ):

        self.vis_simulated_path = VlaveTrajectoryVisualization(
            dim              = dim_path,
            planning_horizon = planning_horizon,
            figsize          = figsize,
            save_dir         = os.path.join(save_dir, "simulated_path"),
            ylim             = (lower_bound_simulated_path, upper_bound_simulated_path),
            color_sample     = "plum",
            color_elite      = "purple",
        )

        self.vis_samples = TrajectoryVisualization(
            dim          = dim_action,
            figsize      = figsize,
            save_dir     = os.path.join(save_dir, "samples"),
            ylim         = (lower_bound_sampling, upper_bound_sampling),
            color_sample = "lightskyblue",
            color_elite  = "royalblue",
        )

        self.vis_filtered_sample = TrajectoryVisualization(
            dim          = dim_action,
            figsize      = figsize,
            save_dir     = os.path.join(save_dir, "filtered_samples"),
            ylim         = (lower_bound_sampling, upper_bound_sampling),
            color_sample = "lightskyblue",
            color_elite  = "royalblue",
        )


        self.vis_cusum_actions = TrajectoryVisualization(
            dim          = dim_action,
            figsize      = figsize,
            save_dir     = os.path.join(save_dir, "cusum_actions"),
            ylim         = (lower_bound_cusum_action, upper_bound_cusum_action),
            color_sample = "yellowgreen",
            color_elite  = "darkgreen",
        )

        self.vis_actions = TrajectoryVisualization(
            dim          = dim_action,
            figsize      = figsize,
            save_dir     = os.path.join(save_dir, "actions"),
            ylim         = (lower_bound_action, upper_bound_action),
            color_sample = "lightpink",
            color_elite  = "crimson",
        )


    def __is_target_trajectory(self, simulated_paths, target):
        if len(target.shape) != 3  : return False
        _, step_path  , dim_path   = simulated_paths.shape
        _, step_target, dim_target = target.shape
        if step_path != step_target: return False
        if  dim_path != dim_target : return False
        return True


    def simulated_paths(self, forward_results, target, num_sample_i, step):
        self.vis_simulated_path.clear()
        # import ipdb; ipdb.set_trace()
        self.vis_simulated_path.plot_samples(forward_results['object_state_trajectory'], step)
        # self.vis_simulated_path.plot_elites(forward_results['object_state_trajectory'][index_elite], iter_outer_loop)
        self.vis_simulated_path.plot_target(target, step)
        self.vis_simulated_path.save_plot(
            fname = self._fname("simulated_paths", step, num_sample_i),
            title = self._title("simulated_paths", step, num_sample_i),
        )


    def samples(self, samples, step, num_sample_i):
        self.vis_samples.clear()
        self.vis_samples.plot_samples(samples)
        # self.vis_samples.plot_elites(elites)
        self.vis_samples.save_plot(
            fname = self._fname("samples", step, num_sample_i),
            title = self._title("samples", step, num_sample_i),
        )


    def filtered_samples(self, samples, step, num_sample_i):
        self.vis_filtered_sample.clear()
        self.vis_filtered_sample.plot_samples(samples)
        # self.vis_samples.plot_elites(elites)
        self.vis_filtered_sample.save_plot(
            fname = self._fname("filtered_samples", step, num_sample_i),
            title = self._title("filtered_samples", step, num_sample_i),
        )


    def cumsum_actions(self, cumsum_actions, step, num_sample_i):
        self.vis_cusum_actions.clear()
        self.vis_cusum_actions.plot_samples(cumsum_actions)
        # self.vis_cusum_actions.plot_elites(elites)
        self.vis_cusum_actions.save_plot(
            fname = self._fname("cumsum_actions", step, num_sample_i),
            title = self._title("cumsum_actions", step, num_sample_i),
        )


    def actions(self, actions, step, num_sample_i):
        self.vis_actions.clear()
        self.vis_actions.plot_samples(actions)
        # self.vis_actions.plot_elites(elites)
        self.vis_actions.save_plot(
            fname = self._fname("actions", step, num_sample_i),
            title = self._title("actions", step, num_sample_i),
        )


    def _fname(self, dataname, step, num_sample_i):
        return "{}_step{}_sample{}".format(dataname, step, num_sample_i)


    def _title(self, dataname, step, num_sample_i):
        return "{}_step{}_sample{}".format(dataname, step, num_sample_i)
