#Nombre: Liam Enmanuel Lopez Guilamo
#Matricula:22-SISN-2-065
# Implementación de Behavior Tree desde cero
from constants import BT_SUCCESS, BT_FAILURE, BT_RUNNING

class BTNode:
    """Nodo base del Árbol de Comportamiento"""
    
    def tick(self, agent):
        """Ejecuta el nodo. Retorna SUCCESS, FAILURE o RUNNING"""
        raise NotImplementedError

class BTAction(BTNode):
    """Nodo de acción - ejecuta una acción específica"""
    
    def __init__(self, action_func):
        self.action_func = action_func
    
    def tick(self, agent):
        try:
            result = self.action_func(agent)
            return result if result in [BT_SUCCESS, BT_FAILURE, BT_RUNNING] else BT_SUCCESS
        except:
            return BT_FAILURE

class BTCondition(BTNode):
    """Nodo de condición - verifica una condición"""
    
    def __init__(self, condition_func):
        self.condition_func = condition_func
    
    def tick(self, agent):
        try:
            if self.condition_func(agent):
                return BT_SUCCESS
            else:
                return BT_FAILURE
        except:
            return BT_FAILURE

class BTSequence(BTNode):
    """Nodo de secuencia - ejecuta hijos en orden, todos deben tener éxito"""
    
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
    """Nodo selector - ejecuta hijos en orden, se detiene en el primero que tenga éxito"""
    
    def __init__(self, children=None):
        self.children = children or []
    
    def add_child(self, child):
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
    """Nodo prioritario - igual a selector pero enfatiza prioridades"""
    pass

class BTParallel(BTNode):
    """Nodo paralelo - ejecuta todos los hijos, retorna éxito si todos lo hacen"""
    
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
    """Decorador - modifica el comportamiento de un hijo"""
    
    def __init__(self, child):
        self.child = child
    
    def tick(self, agent):
        return self.child.tick(agent)

class BTNegation(BTDecorator):
    """Negación - invierte el resultado del hijo"""
    
    def tick(self, agent):
        result = self.child.tick(agent)
        if result == BT_SUCCESS:
            return BT_FAILURE
        elif result == BT_FAILURE:
            return BT_SUCCESS
        else:
            return BT_RUNNING

class BTRepeat(BTDecorator):
    """Repetición - repite el hijo N veces"""
    
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
    """Árbol de Comportamiento - gestor principal"""
    
    def __init__(self, root):
        self.root = root
    
    def tick(self, agent):
        """Ejecuta un tick del árbol"""
        return self.root.tick(agent)

# Acciones comunes para enemigos
def action_move_towards_player(agent):
    """Acción: moverse hacia el jugador"""
    if hasattr(agent, 'move_towards_player'):
        agent.move_towards_player()
        return BT_SUCCESS
    return BT_FAILURE

def action_shoot_at_player(agent):
    """Acción: disparar al jugador"""
    if hasattr(agent, 'shoot_at_player'):
        agent.shoot_at_player()
        return BT_SUCCESS
    return BT_FAILURE

def action_patrol(agent):
    
    if hasattr(agent, 'patrol'):
        agent.patrol()
        return BT_SUCCESS
    return BT_FAILURE

def condition_can_see_player(agent):
    """Condición: ¿puede ver al jugador?"""
    if hasattr(agent, 'can_see_player'):
        return agent.can_see_player()
    return False

def condition_is_player_close(agent):
    """Condición: ¿está el jugador cerca?"""
    if hasattr(agent, 'is_player_close'):
        return agent.is_player_close()
    return False

def condition_can_shoot(agent):
    """Condición: ¿puede disparar?"""
    if hasattr(agent, 'can_shoot'):
        return agent.can_shoot()
    return False
