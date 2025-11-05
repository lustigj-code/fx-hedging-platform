"""
Mathematical utilities for option pricing.
"""
from scipy.stats import norm
import numpy as np


def cumulative_normal(x: float) -> float:
    """
    Cumulative standard normal distribution N(x).

    Args:
        x: Input value

    Returns:
        Probability that a standard normal random variable is <= x
    """
    return norm.cdf(x)


def probability_density_normal(x: float) -> float:
    """
    Probability density function of standard normal distribution.

    Args:
        x: Input value

    Returns:
        PDF value at x
    """
    return norm.pdf(x)


def generate_gbm_paths(
    S0: float,
    mu: float,
    sigma: float,
    T: float,
    n_simulations: int = 10000,
    seed: int = None,
) -> np.ndarray:
    """
    Generate paths using Geometric Brownian Motion.

    S_T = S_0 * exp((mu - sigma^2/2)*T + sigma*sqrt(T)*Z)

    where Z ~ N(0,1)

    Args:
        S0: Initial spot rate
        mu: Drift rate (typically r_domestic - r_foreign under risk-neutral pricing)
        sigma: Volatility
        T: Time to maturity in years
        n_simulations: Number of Monte Carlo paths
        seed: Random seed for reproducibility

    Returns:
        Array of simulated terminal spot rates
    """
    if seed is not None:
        np.random.seed(seed)

    Z = np.random.standard_normal(n_simulations)
    drift = (mu - 0.5 * sigma**2) * T
    diffusion = sigma * np.sqrt(T) * Z

    S_T = S0 * np.exp(drift + diffusion)

    return S_T
