import numpy as np
class Objective(object):
    def __init__(self, C_D_ref = 0.011562, C_L_ref = 0.87633, A_ref=0.077862,
                 penalization_lift=1e4, penalization_area=1e3):

        self.C_D_ref = C_D_ref
        self.C_L_ref = C_L_ref
        self.A_ref = A_ref
        self.penalization_lift = penalization_lift
        self.penalization_area = penalization_area

    def __call__(self, x):
        C_D = x[1]
        C_L = x[0]
        A = x[2]
        return C_D/self.C_D_ref + \
            self.penalization_lift * np.maximum(0, 0.999 - C_L/self.C_L_ref) + \
            self.penalization_area * np.maximum(0, self.A_ref-A)

    def grad(self, x):
        C_D = x[1]
        C_L = x[0]
        A = x[2]
        return np.array([1.0/self.C_D_ref,
                         (0.999 - C_L/self.C_L_ref > 0) * self.penalization_lift * max(0, 0.999 - C_L/self.C_L_ref),
                         (self.A_ref-A > 0) * self.penalization_area * max(0, self.A_ref-A)])

