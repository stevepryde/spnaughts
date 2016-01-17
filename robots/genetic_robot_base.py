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
