import numpy as np
from scipy.stats import norm
import math

def calculate_log_returns(open_price, close_price):
    """
    Calculate log returns given the opening and closing prices.
    """
    if open_price > 0 and close_price > 0:
        return np.log(close_price / open_price)
    return None

def calculate_greeks(spot, strike, time, rate, volatility):
    """
    Calculate Greeks for options using the Black-Scholes model.
    
    Args:
        spot (float): Spot price of the underlying asset.
        strike (float): Strike price of the option.
        time (float): Time to expiration in years.
        rate (float): Risk-free interest rate.
        volatility (float): Implied volatility of the underlying asset.

    Returns:
        tuple: Delta, Gamma, Theta, Vega
    """
    try:
        # Calculate d1 and d2 for Black-Scholes formula
        d1 = (math.log(spot / strike) + (rate + 0.5 * volatility ** 2) * time) / (volatility * math.sqrt(time))
        d2 = d1 - volatility * math.sqrt(time)

        # Calculate Greeks
        delta = norm.cdf(d1)  # Sensitivity of option price to spot price
        gamma = norm.pdf(d1) / (spot * volatility * math.sqrt(time))  # Sensitivity of delta to spot price
        theta = -(spot * norm.pdf(d1) * volatility) / (2 * math.sqrt(time))  # Time decay of the option price
        vega = spot * norm.pdf(d1) * math.sqrt(time)  # Sensitivity of option price to volatility

        return delta, gamma, theta, vega
    except Exception as e:
        print(f"Error calculating Greeks: {e}")
        return None, None, None, None
    