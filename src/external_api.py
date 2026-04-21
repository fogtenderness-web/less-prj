import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.exchangeratesapi.io/v1/latest"

def convert_currency(amount: float, from_currency: str, to_currency: str = "RUB") -> float:
    if from_currency == to_currency:
        return amount
    if not API_KEY:
        raise ValueError("API key not found. Set API_KEY in .env")

    params = {"access_key": API_KEY, "base": from_currency, "symbols": to_currency}
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get("success"):
            raise ValueError(f"API error: {data.get('error', {}).get('info', 'Unknown')}")
        rate = data.get("rates", {}).get(to_currency)
        if rate is None:
            raise ValueError(f"Rate for {to_currency} not found")
        return amount * rate
    except (requests.RequestException, ConnectionError) as e:
        raise ConnectionError(f"Failed to fetch exchange rate: {e}")