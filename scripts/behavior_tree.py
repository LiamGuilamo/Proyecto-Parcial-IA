#Behavior desde cero
from constants import BT_SUCCESS, BT_FAILURE, BT_RUNNING

class BTNode:
    """Nodo base del Arbol de Comportamiento"""

    def tick(self, agent):
        """ejecuta el nodo."""
        raise NotImplementedError
    
class BTAction(BTNode):
    """Nodo de accion - ejecuta una accion"""

    def __init__(self, action_func):
        self.action_func = action_func

    def tick(self, agent):
        try:
            result = self.action_func(agent)
            return result if result in [BT_SUCCESS, BT_FAILURE, BT_RUNNING] else BT_SUCCESS
        except:
            return BT_FAILURE
        
class BTCondition(BTNode):
    """Nodo de condicion"""

    def __init__(self, conditio_func):
        self.condition_func = conditio_func

    def tick(self, agent):
        try:
            if self.condition_func(agent):
                return BT_SUCCESS
            else:
                return BT_FAILURE
        except:
            return BT_FAILURE
        
class BTSequence(BTNode):
    """nodo de secuencia"""

    def __init__(self, children=None):
        self.children = children or []

    def add_child(self, child):
        self.children.append(child)

    def tick(self, agent):
        for child in self.children:
            result = child.tick(agent)
            if result != BT_SUCCESS:
                return result
        return BT_SUCCESS
    
class BTSelector(BTNode):
    """nodo selector"""

    def __init__(self, children=None):
        self.children = children or []

    def add_child(self,child):
        self.children.append(child)

    def tick(self, agent):
        for child in self.children:
            result = child.tick(agent)
            if result == BT_SUCCESS:
                return BT_SUCCESS
            elif result == BT_RUNNING:
                return BT_RUNNING
        return BT_FAILURE
    
class BTPriority(BTSelector):
    """Nodo prioritario"""
    pass

class BTParallel(BTNode):
    """Nodo paralelo"""

    def __init__(self, children=None):
        self.children = children or []

    def add_child(self, child):
        self.children.append(child)

    def tick(self, agent):
        success_count = 0
        for child in self.children:
            result = child.tick(agent)
            if result == BT_SUCCESS:
                success_count += 1
        
        if success_count == len(self.children):
            return BT_SUCCESS
        return BT_FAILURE
    
class BTDecorator(BTNode):
    """decorar"""
    def __init__(self, child):
        self.child = child

    def tick(self, agent):
        return self.child.tick(agent)

class BTNegation(BTDecorator):
    """Negacion"""

    def tick(self, agent):
        result = self.child.tick(agent)
        if result == BT_SUCCESS:
            return BT_FAILURE
        elif result == BT_FAILURE:
            return BT_RUNNING
        else:
            return BT_RUNNING
        
class BTRepeat(BTDecorator):
    """repeticion"""

    def __init__(self, child, times=1):
        super().__init__(child)
        self.times = times
        self.count = 0

    def tick(self, agent):
        if self.count >= self.times:
            self.count = 0
            return BT_SUCCESS
        
        result = self.child.tick(agent)
        if result == BT_SUCCESS:
            self.count += 1
            if self.count >= self.times:
                self.count = 0
                return BT_SUCCESS
            return BT_RUNNING
        return result
    
class BehaviorTree:
    """Arbol de Comportamiento"""

    def __init__(self,root):
        self.root = root

    def tick(self, agent):
        """ejecuta un tick arbol"""
        return self.root.tick(agent)
    
#acciones enemigos 
def action_move_towards_player(agent):
    """moverse hacia el jugador"""
    if hasattr(agent, 'move_towards_player'):
        agent.move_towards_player()
        return BT_SUCCESS
    return BT_FAILURE

def action_shoot_at_player(agent):
    """disparar al jugador"""
    if hasattr(agent, 'shoot_at_player'):
        agent.shoot_at_player()
        return BT_SUCCESS
    return BT_FAILURE

def action_patrol(agent):
    """accion:perseguir"""
    if hasattr(agent, 'patrol'):
        agent.patrol()
        return BT_SUCCESS
    return BT_FAILURE

def condition_can_see_player(agent):
    """condicion: poder ver al jugador"""
    if hasattr(agent, 'can_see_player'):
        return agent.can_see_player()
    return False

def condition_is_player_close(agent):
    """condicion: el jugador esta cerca"""
    if hasattr(agent, 'is_player_close'):
        return agent.is_player_close()
    return False    

def condition_can_shoot(agent):
    """condicion: puede disparar?"""
    if hasattr(agent, 'can_shoot'):
        return agent.can_shoot()
    return False
        
        


            