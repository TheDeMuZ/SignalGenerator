class Params():
    def __init__(self, A_re = None, A_im = None, t1 = 0.0, d = 0.0, T = None, kw = None, ts = None, p = None, f = 0.0):
        if A_re and A_im:
            self.A = complex(A_re, A_im)
        
        self.t1 = t1
        self.d = d
        self.T = T
        self.kw = kw
        self.ts = ts
        self.p = p
        self.f = f