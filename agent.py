class Agent:
        def __init__(self, position, affinity, exhaustion=0, state="searching", t_spent=0, t_since=0, pending_kill=None, kills=0):
                self.position = position
                self.affinity = affinity
                self.exhaustion = exhaustion
                self.state = state
                self.t_spent = t_spent
                self.t_since = t_since
                self.pending_kill = pending_kill
                self.kills = kills