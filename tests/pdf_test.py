import fitz  # PyMuPDF
import os

text = """📊 Analysis for BTC
════════════════════════════════
💰 Current Price: $106,729.00
📈 24h Change: 🔻 0.00%
💎 24h High: $107,076.00
💫 24h Low: $106,357.00
📊 24h Volume: $106,974,131,697

📈 Trend Analysis
────────────────────────────────
Error formatting trend data: unsupported format string passed to numpy.ndarray.__format__

🔄 Momentum Analysis
────────────────────────────────
- RSI: 69.83 ➖ Neutral
- Stochastic: K(83.9) D(82.3)
- Williams %R: -17.5
- Money Flow Index: 74.3
- CCI: 105.5

📊 Volume Analysis
────────────────────────────────
- Current Volume: 106.97B
- Average Volume: 76.78B
- OBV: 1212.34B
- VWAP: $97,954.59
- CMF: 39650909827.471

📉 Volatility Analysis
────────────────────────────────
- Bollinger Bands:
  - Upper: $107,927.87
  - Middle: $103,836.10
  - Lower: $99,744.33
  - Width: 7.88%
- ATR: $1,256.06 (1.2%)
- Historical Volatility: 16.4%"""

filename = 'outputs/test.pdf'

def text_to_pdf(text, filename):
    # Ensure the output directory exists

    # Create a new PDF with Reportlab
    doc = fitz.open()
    page = doc.new_page()
    
    # Insert the text
    page.insert_text((50, 50), text, fontsize=11)
    
    # Save the PDF
    doc.save(filename)
    doc.close()

# Call the function
text_to_pdf(text=text, filename=filename)