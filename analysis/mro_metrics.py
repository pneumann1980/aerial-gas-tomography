import numpy as np
import math

def normalize_distribution(dist):
    # Normalize the distribution to ensure it sums up to 1
    return dist / np.sum(dist)

def calculateJensenShannonDivergence(P, Q):
    # ensure that P and Q have the same shape
    if P.shape != Q.shape:
        raise ValueError("P and Q should have the same shape")

    # Normalize the probability distributions
    P_normalized = normalize_distribution(P)
    Q_normalized = normalize_distribution(Q)

    # Calculate the mixture distribution M
    M = 0.5 * (P_normalized + Q_normalized)

    # Calculate the KL divergence from P to M
    KL_PM = np.sum(P_normalized * np.log(P_normalized / M))

    # Calculate the KL divergence from Q to M
    KL_QM = np.sum(Q_normalized * np.log(Q_normalized / M))

    # Calculate the Jensen-Shannon divergence
    JSD = 0.5 * (KL_PM + KL_QM)

    return JSD

    return JSD