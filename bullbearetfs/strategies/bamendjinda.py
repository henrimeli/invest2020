
from bullbearetfs.strategy.strategybase import EggheadBaseStrategy

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

logger = logging.getLogger(__name__)

class BamendjindaStrategy(EggheadBaseStrategy):

  def __init__(self,robot):
    self.robot = robot
