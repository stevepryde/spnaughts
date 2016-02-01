################################################################################
# SP Naughts - Simple naughts and crosses game including a collection of AI bots
# Copyright (C) 2015, 2016 Steve Pryde
#
# This file is part of SP Naughts.
#
# SP Naughts is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SP Naughts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SP Naughts.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
# geneticrunner.py
#
# Handle the running of a genetic bot.

import os
import datetime
import random
import multiprocessing
from game.runners.gamerunnerbase import GAMERUNNERBASE
import game.robotmanager
from game.log import *

MAX_SCORE = 7.0

class BatchWorker(multiprocessing.Process):
  def __init__(self, batchqueue):
    super(BatchWorker, self).__init__()
    self.batchqueue = batchqueue
    self.manager = multiprocessing.Manager()
    self.scores = self.manager.dict()
    return

  def get_scores(self):
    return self.scores

  def run(self):
    try:
      while (True):
        batch = self.batchqueue.get()

        # The game runner signals the end of the queue by enqueuing 'None'.
        if (batch is None):
          break

        info     = batch.get_batch_info()
        sample   = info['sample']
        gen      = info['generation']
        log_path = info['log_path']
        bot_index = info['index']

        batchscores = batch.run_batch()
        if (batchscores is not None):
          self.scores[sample] = batchscores

        if (batch.config['loggames']):
          # Write batch log to a file.
          gen_path        = os.path.join(log_path, "Gen{}".format(gen))
          sample_log_path = os.path.join(gen_path, "sample_{}_batch_log.log".
                                         format(sample))

          try:
            os.makedirs(gen_path, exist_ok=True)
            batch.write_to_file(sample_log_path)
          except OSError as e:
            log_error("Error creating batch log path '{}': {}".
                      format(gen_path, str(e)))

        print("Completed batch for sample {:5d} :: score = {:.3f}".
              format(sample, batchscores[bot_index]))

        self.batchqueue.task_done()
    except KeyboardInterrupt:
      log_info("Cancelled")

    return


class GENETICRUNNER(GAMERUNNERBASE):
  def __init__(self):
    self.config = None
    self.robots = None
    self.genetic_robot_index = 0
    self.standard_mutations = 50

    self.num_threads = multiprocessing.cpu_count() - 2
    if (self.num_threads < 1):
      self.num_threads = 1

    log_info("Using {} threads...".format(self.num_threads))
    self.run_log_file = None
    return

  def log_genetic(self, message):
    print(message)
    return

  def log_run(self, message):
    if (self.run_log_file):
      try:
        with open(self.run_log_file, 'a') as logfile:
          logfile.write(message + "\n")
      except Exception as e:
        log_critical("Error writing to run log file '{}': {}".
                     format(self.run_log_file, str(e)))

    return

  def setup(self, config, robots):
    self.config = config
    self.robots = robots
    self.genetic_index = 0
    self.standard_mutations = 50

    # Determine which robot is genetic.
    if (not robots[0].genetic):
      self.genetic_index = 1
    elif (robots[1].genetic):
      # Both robots are genetic - this is not allowed.
      log_critical("GENETICRUNNER: Both robots are genetic. Only first bot " +
                     "will use the genetic algorithm")
      self.genetic_index = 0

    # Store the name of the genetic robot. This is used to generate new ones.
    self.genetic_name = self.robots[self.genetic_index].name

    # Set up logging.
    log_base_dir = self.config['log_base_dir']

    ts            = str(datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S%f'))
    self.game_log_path = os.path.join(log_base_dir,
                                      "genetic_{}_{}_{}".
                                      format(self.robots[0].name,
                                             self.robots[1].name,
                                             ts))

    if (os.path.exists(self.game_log_path)):
      log_critical("Path '{}' already exists!".format(self.game_log_path))
      return

    try:
      os.mkdir(self.game_log_path)
    except Exception as e:
      log_critical("Error creating log directory '{}': {}".
                   format(self.game_log_path, str(e)))
      return

    self.run_log_file = os.path.join(self.game_log_path, "genetic_run_log.log")

    return

  def generate_samples(self, input_samples, generation):
    self.genetic_pool = []

    manager = game.robotmanager.ROBOTMANAGER()

    if (input_samples != None and len(input_samples) > 0):
      self.genetic_pool.extend(input_samples)

      for sample in input_samples:
        sample_recipe = sample.get_recipe()

        # Experimental:
        # If the sample had fewer mutations than the current standard,
        # lower the standard number, and vice versa.
        sample_mutations = sample.get_metadata('mutations')
        if (sample_mutations == None):
          sample_mutations = self.standard_mutations

        self.standard_mutations += \
          int((sample_mutations - self.standard_mutations) * 0.3)

        if (self.standard_mutations < 1):
          self.standard_mutations = 1

        mutation_range = int(self.standard_mutations * 0.5)
        min_mutations  = self.standard_mutations - int(mutation_range / 2.0)

        if (min_mutations < 1):
          min_mutations = 1

        if (mutation_range < 2):
          mutation_range = 2

        for s in range(1, self.config['num_samples']):
          robot_obj = manager.get_robot_object(self.genetic_name)

          if (not robot_obj):
            log_critical("Error instantiating robot '{}'".format(robot_name))
            return

          # Name it using the generation and sample number.
          robot_obj.set_name("{}-{}-{}".
                             format(self.genetic_name, generation, s))

          # Mutate the recipe.
          num_mutations = random.randint(min_mutations,
                                         min_mutations + mutation_range)

          mutated_recipe = sample_recipe
          for n in range(num_mutations):
            mutated_recipe = robot_obj.mutate_recipe(mutated_recipe)

          robot_obj.create_from_recipe(mutated_recipe)
          robot_obj.set_metadata('mutations', num_mutations)
          self.genetic_pool.append(robot_obj)

    else:
      # Start from scratch, just create random robots.
      # NOTE: The original robot is discarded (for convenience).
      for s in range(1, self.config['num_samples'] + 1):
        robot_obj = manager.get_robot_object(self.genetic_name)

        if (not robot_obj):
          log_critical("Error instantiating robot '{}'".format(robot_name))
          return

        # Name it using the generation and sample number. This is generation 0.
        robot_obj.set_name("{}-{}-{}".
                           format(self.genetic_name, generation, s))

        robot_obj.create(self.config)
        self.genetic_pool.append(robot_obj)

    return

  def select_samples(self, sorted_pool):
    # TODO: allow custom selector, to test various selection criteria.

    keep = 1
    if ('keep_samples' in self.config):
      keep = int(self.config['keep_samples'])
      if (keep > len(sorted_pool)):
        keep = len(sorted_pool)

    # Get samples.
    # For now, just get the top n scoring samples.
    selected_samples = sorted_pool[:keep]

    return selected_samples

  def run(self, config, robots):
    self.setup(config, robots)

    if (not robots[self.genetic_index].genetic):
      log_critical("GENETICRUNNER: Neither robot is a genetic robot!")
      return

    selected_samples = []

    for gen in range(config['num_generations']):
      self.log_genetic("--------------------------")
      self.log_genetic("Generation '{}':".format(str(gen)))

      # Set up the genetic robot pool.
      self.generate_samples(selected_samples, gen)

      # Set up the batch queue and worker threads.
      batchqueue = multiprocessing.JoinableQueue()
      threads = []
      for wt in range(self.num_threads):
        thr = BatchWorker(batchqueue)
        thr.start()
        threads.append(thr)

      for s in range(len(self.genetic_pool)):
        robot_list = []
        for index in [0, 1]:
          if (index == self.genetic_index):
            robot_list.append(self.genetic_pool[s])
          else:
            robot_list.append(self.robots[index])

        batch = game.batch.BATCH(self.config, robot_list)
        batch.set_label("Gen {} - Sample {}".format(gen, s))
        batch.set_batch_info({'generation':gen,
                              'sample':s,
                              'log_path':self.game_log_path,
                              'index':self.genetic_index})
        batchqueue.put(batch)

      # Wait for all batches to process...
      batchqueue.join()

      # Tell the threads to stop.
      for wt in range(self.num_threads):
        batchqueue.put(None)

      # Join threads and process scores.
      scores = {}
      for thr in threads:
        thr.join()
        scores.update(thr.get_scores())

      # First get a dict of just the score we want.
      bot_scores = {}
      for s in scores.keys():
        score_list = scores[s]
        _score     = score_list[self.genetic_index]

        # Set the score in the robot object.
        self.genetic_pool[s].set_score(_score)
        bot_scores[s] = _score

      # Sort the pool based on score, in descending order.
      sorted_pool = sorted(self.genetic_pool, key=lambda bot: bot.get_score(),
                           reverse=True)

      selected_samples = self.select_samples(sorted_pool)

      selected_scores  = []
      selected_recipes = []
      for sample in selected_samples:
        score = sample.get_score()
        selected_scores.append("{:.3f}".format(score))
        selected_recipes.append("[{:.3f}]: '{}'".format(score,
                                                        sample.get_recipe()))

      self.log_genetic("Generation {} highest scores: [{}]".
                       format(gen, ', '.join(selected_scores)))

      # Also log recipes of winning robots:
      self.log_run("Generation '{}': Winning robot recipes:\n{}".
                   format(gen, "\n".join(selected_recipes)))

    return
