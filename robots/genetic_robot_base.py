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
# genetic_robot_base.py
#
# Base class for genetic robots, so that we know which methods need to be
# implemented.

from robots.robot_base import Robot

class GeneticRobot(Robot):
  def __init__(self):
    super(GeneticRobot, self).__init__()

    self.genetic = True
    return

  def create(self, config):
    return

  def get_recipe(self):
    return

  def create_from_recipe(self, recipe):
    return

  def mutate_recipe(self, recipe):
    return

  def get_mutated_recipe(self, num_mutations):
    recipe = self.get_recipe()
    for n in range(num_mutations):
      recipe = self.mutate_recipe(recipe)
    return recipe
