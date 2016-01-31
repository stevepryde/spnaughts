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

        print("Completed batch for sample {}".format(sample))
        self.batchqueue.task_done()
    except KeyboardInterrupt:
      log_info("Cancelled")

    return


class GENETICRUNNER(GAMERUNNERBASE):
  def __init__(self):
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

  def run(self, config, robots):
    # Set up log.
    log_base_dir = config['log_base_dir']

    robot_name0   = robots[0].name
    robot_name1   = robots[1].name

    ts            = str(datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S%f'))
    game_log_path = os.path.join(log_base_dir, "genetic_" + robot_name0 +
                                 "_" + robot_name1 + "_" + ts)

    if (os.path.exists(game_log_path)):
      log_critical("Path '{}' already exists!".format(game_log_path))
      return

    try:
      os.mkdir(game_log_path)
    except Exception as e:
      log_critical("Error creating log directory '{}': {}".
                   format(game_log_path, str(e)))
      return

    self.run_log_file = os.path.join(game_log_path, "genetic_run_log.log")

    # Set up the genetic robot pool.
    genetic_robot_pool = []
    genetic_index = 0
    if (not robots[0].genetic):
      genetic_index = 1

    # Add the first robot.
    master_robots = [robots[genetic_index]]

    genetic_robot_pool = list(master_robots)

    num_genetic_robots = 0
    for robot_obj in robots:
      if (robot_obj.genetic):
        num_genetic_robots += 1
        genetic_robot_name = robot_obj.name

    # In genetic mode, one and only one of the robots must be a genetic robot
    if (num_genetic_robots < 1):
      log_critical("One of the robots must be a genetic robot if " +
                     "--genetic is supplied")
      return
    elif (num_genetic_robots > 1):
      log_critical("Only one of the robots can be genetic if " +
                     "--genetic is supplied")
      return

    assert(genetic_robot_name != None)

    manager = game.robotmanager.ROBOTMANAGER()

    # Remember we've already added the first sample.
    # The first set of samples are all purely random.
    for s in range(1, config['num_samples']):
      robot_obj = manager.get_robot_object(genetic_robot_name)
      if (not robot_obj):
        log_critical("Error instantiating robot '{}'".format(robot_name))
        return

      # Name it using the generation and sample number. This is generation 0.
      robot_obj.set_name(genetic_robot_name + '-0-' + str(s))
      robot_obj.create(config)
      genetic_robot_pool.append(robot_obj)

    log_trace("Genetic robot pool has been set up")

    gen_pool_index = 0
    highest_score = -100
    baseline_score = -100
    for gen in range(config['num_generations']):
      self.log_genetic("Generation '{}':".format(str(gen)))

      batchqueue = multiprocessing.JoinableQueue()
      threads = []
      for wt in range(self.num_threads):
        thr = BatchWorker(batchqueue)
        thr.start()
        threads.append(thr)

      for s in range(len(genetic_robot_pool)):
        robot_list = []
        for index in [0, 1]:
          if (index == genetic_index):
            robot_list.append(genetic_robot_pool[s])
          else:
            robot_list.append(robots[index])

        batch = game.batch.BATCH(config, robot_list)
        batch.set_label("Gen {} - Sample {}".format(gen, s))
        batch.set_batch_info({'generation':gen,
                              'sample':s,
                              'log_path':game_log_path})
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
        _score     = score_list[genetic_index]

        # Set the score in the robot object.
        genetic_robot_pool[s].set_score(_score)
        bot_scores[s] = _score

      # Now sort the dict keys by value.
      sorted_bot_indexes = sorted(bot_scores, key=bot_scores.get,
                                  reverse=True)

      keep = 1
      if ('keep_samples' in config):
        keep = int(config['keep_samples'])
        if (keep > len(sorted_bot_indexes)):
          keep = len(sorted_bot_indexes)

      i = 0
      master_robots = []
      for n in range(keep):
        master_robots.append(genetic_robot_pool[sorted_bot_indexes[i]])
        i += 1

      highest_score = master_robots[0].get_score()

      self.log_genetic("Highest score was '{}'".format(str(highest_score)))

      winning_recipe = master_robots[0].get_recipe()

      # Should log this robot's blueprint.
      self.log_run("Generation '{}': Winning robot recipe is '{}'".
                   format(gen, winning_recipe))

      if (highest_score >= MAX_SCORE):
        self.log_genetic("Reached highest score: {}".format(highest_score))
        self.log_run("Reached highest score: {}".format(highest_score))
        return

      # Add the master robots to the list - they may well be better than their
      # derivatives.
      #
      # TODO: do we want num_samples * keep_samples? Or just num_samples overall?
      genetic_robot_pool = []
      for bot in master_robots:
        genetic_robot_pool.append(bot)
        master_recipe = bot.get_recipe()

        for s in range(1, config['num_samples']):
          robot_obj = manager.get_robot_object(genetic_robot_name)
          if (not robot_obj):
            log_critical("Error instantiating robot '{}'".format(robot_name))
            return

          # Name it using the generation and sample number.
          robot_obj.set_name(genetic_robot_name + '-' + str(gen + 1) + '-' + str(s))

          # Mutate the recipe
          num_mutations = random.randint(1, 50)
          mutated_recipe = master_recipe
          for n in range(num_mutations):
            mutated_recipe = robot_obj.mutate_recipe(mutated_recipe)

          robot_obj.create_from_recipe(mutated_recipe)
          genetic_robot_pool.append(robot_obj)

    return
