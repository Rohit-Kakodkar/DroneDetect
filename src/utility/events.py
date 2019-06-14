import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import math

class recovery_event():
    """
        Recovery event class to simulate data
        generate_altitude : simulates a inverted gaussian curve
    """

    def __init__(self, mu, variance, drop, ts, speed):
        self.mu = mu
        self.variance = variance
        self.sigma = math.sqrt(variance)
        self.x = ts*speed
        self.drop = drop

    def generate_altitude(self):
        """
            return barometer reading from recovery event
        """
        return -self.drop * stats.norm.pdf(self.x, self.mu, self.sigma)
