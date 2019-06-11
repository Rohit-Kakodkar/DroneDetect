import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import math

class recovery_event():

    def __init__(self, mu, variance, drop, ts, speed):
        self.mu = mu
        self.variance = variance
        self.sigma = math.sqrt(variance)
        self.x = ts*speed
        self.drop = drop

    def generate_altitude(self):
        return -self.drop * stats.norm.pdf(self.x, self.mu, self.sigma)
