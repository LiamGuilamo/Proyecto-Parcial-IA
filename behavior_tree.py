#Behavior desde cero
from constants import BT_SUCCESS, BT_FAILURE, BT_RUNNING

class BTNode:
    """Nodo base del Arbol de Comportamiento"""

    def tick(self, agent):
        """ejecuta el nodo."""