class leadlagcompensator:
    def __init__(self, K=0.001, T1=0.01, T2=0.05, Ts=0.01):
        self.K = K
        self.T1 = T1
        self.T2 = T2
        self.Ts = Ts

        self.prev_x = 0
        self.prev_y = 0

        self.A = (2*T2 - Ts) / (2*T2 + Ts)
        self.B = K * (2*T1 + Ts) / (2*T2 + Ts)
        self.C = -K * (2*T1 - Ts) / (2*T2 + Ts)

    def compute(self, x):
        y = self.A * self.prev_y + self.B * x + self.C * self.prev_x

        self.prev_x = x
        self.prev_y = y


        return y
    
    def reset(self):
        self.prev_x = 0
        self.prev_y = 0