# robotmanager.py
#
# Manage creation of robots.

import importlib

# Path to robots.
ROBOT_BASE_PATH = 'robots'

# Robots may store data in ROBOT_TEMP_PATH/<robotname>/.
# This directory will be created by this module if necessary, the first time
# it is requested by the robot.
ROBOT_TEMP_PATH = 'tempdata'

class ROBOTMANAGER(object):
  def __init__(self):
    return

  def get_robot_object(self, robot_module_name):
    # Load test module.
    try:
      module = importlib.import_module("%s.%s.%s" %
                                       (ROBOT_BASE_PATH, robot_module_name,
                                        robot_module_name))
    except ImportError as e:
      log_critical("Failed to import robot module '%s.%s': %s" %
                   (ROBOT_BASE_PATH, robot_module, e))
      log_critical(traceback.format_exc())
      return

    # It is expected that the class name will be the same as the module name,
    # but all uppercase.
    classname  = robot_module_name.upper()
    class_type = getattr(module, classname)
    robot_obj  = class_type()
    robot_obj.set_temp_path_base(ROBOT_TEMP_PATH)

    return robot_obj

  def create_robots(self, config):
    # Create robots.
    robots = []
    genetic_robot_name = None
    for robot_name in (config['robot1'], config['robot2']):
      robot_obj = self.get_robot_object(robot_name)
      if (not robot_obj):
        log_critical("Error instantiating robot '{}'".format(robot_name))
        quit()

      robot_obj.set_name(robot_name)
      robot_obj.create(config)
      robots.append(robot_obj)

    return robots
