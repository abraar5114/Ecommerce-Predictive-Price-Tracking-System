# =============================================
# ECOMMERCE PREDICTIVE PRICE TRACKING SYSTEM
# Machine Learning Model File
# =============================================

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from database import get_price_history
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# --- Predict Future Price ---
def predict_price(product_id):
    try:
        # Get price history from database
        history = get_price_history(product_id)

        if len(history) < 2:
            return None, "Not enough data to predict yet. Need at least 2 price records."

        # Prepare data
        prices = [float(h[0]) for h in history]
        days = list(range(len(prices)))

        # Convert to numpy arrays
        X = np.array(days).reshape(-1, 1)
        y = np.array(prices)

        # Train Linear Regression Model
        model = LinearRegression()
        model.fit(X, y)

        # Predict next 7 days
        future_days = np.array(range(len(prices), len(prices) + 7)).reshape(-1, 1)
        future_prices = model.predict(future_days)

        # Get trend
        slope = model.coef_[0]

        if slope < 0:
            suggestion = "📉 Price is DROPPING — Wait a few days to get better price!"
        elif slope > 0:
            suggestion = "📈 Price is RISING — Buy Now before price goes higher!"
        else:
            suggestion = "➡️ Price is STABLE — Buy anytime!"

        return {
            "current_price": prices[-1],
            "predicted_price_7days": round(future_prices[-1], 2),
            "highest_price": round(max(prices), 2),
            "lowest_price": round(min(prices), 2),
            "average_price": round(sum(prices) / len(prices), 2),
            "suggestion": suggestion,
            "slope": slope
        }, None

    except Exception as e:
        return None, str(e)

# --- Generate Price Chart ---
def generate_chart(product_id, product_name):
    try:
        history = get_price_history(product_id)

        if len(history) < 2:
            return None

        prices = [float(h[0]) for h in history]
        dates = [h[1] for h in history]
        days = list(range(len(prices)))

        # Train model for trend line
        X = np.array(days).reshape(-1, 1)
        y = np.array(prices)
        model = LinearRegression()
        model.fit(X, y)
        trend_line = model.predict(X)

        # Plot chart
        plt.figure(figsize=(10, 5))
        plt.plot(dates, prices, marker='o', color='blue', label='Actual Price')
        plt.plot(dates, trend_line, color='red', linestyle='--', label='Trend Line')
        plt.title(f'Price History - {product_name}')
        plt.xlabel('Date')
        plt.ylabel('Price (₹)')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

        # Save chart
        chart_path = f"static/charts/chart_{product_id}.png"
        os.makedirs("static/charts", exist_ok=True)
        plt.savefig(chart_path)
        plt.close()

        return chart_path

    except Exception as e:
        print(f"Chart generation error: {e}")
        return None
    