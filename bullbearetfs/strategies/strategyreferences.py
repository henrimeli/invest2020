import logging
from bullbearetfs.strategies.strategybase import EggheadBaseStrategy
from bullbearetfs.strategies.strategybase import WORKFLOW_ENTRIES, PAIRS_ENTRIES
from bullbearetfs.strategies.babadjou import BabadjouStrategy
from bullbearetfs.strategies.batcham import BatchamStrategy

"""

  
"""

logger = logging.getLogger(__name__)

class BabadjouStrategyReference(BabadjouStrategy):
  """
   A BabadjouStrategyReference Class represents an instance of classes that implement the Babadjou Investment Strategy.
 
   List all the Methods here:
  """
  def __init__(self,robot):
    super().__init__(robot,name='Babadjou Reference')

  def __str__(self):
    return "{} Strategy Reference Implementation".format(self.name) 




class BatchamStrategyReference(EggheadBaseStrategy):
  """
   A BatchamStrategyReference Class represents an instance of classes that implement the Batcham Investment Strategy.
 
   List all the Methods here:
  """
  def __init__(self,robot):
    super().__init__(robot,name='Batcham',workflow=WORKFLOW_ENTRIES[1],pair=PAIRS_ENTRIES[0])


  def sell(self):
    pass 

  def buy(self):
    pass 


class BalachiStrategyReference(EggheadBaseStrategy):
  """
   A BalachiStrategyReference Class represents an instance of classes that implement the Balachi Investment Strategy.
 
   List all the Methods here:
  """
  def __init__(self,robot):
    super().__init__(robot,name='Balachi',workflow=WORKFLOW_ENTRIES[1],pair=PAIRS_ENTRIES[0])


class BangangStrategyReference(EggheadBaseStrategy):
  """
   A BangangStrategyReference Class represents an instance of classes that implement the Bangang Investment Strategy.
 
   List all the Methods here:
  """
  def __init__(self,robot):
    super().__init__(robot,name='Bangang',workflow=WORKFLOW_ENTRIES[1],pair=PAIRS_ENTRIES[0])


