# src/education/content.py
educational_content = {
    "education_basic_concepts_introduction": {
        "title": "Introduction to Blockchain",
        "text": "A blockchain is a shared, immutable ledger that facilitates the process of recording transactions and tracking assets in a business network.",
        "links": [("Learn more about Blockchain", "https://www.ibm.com/topics/blockchain")]
    },
    "education_basic_concepts_cryptocurrencies": {
        "title": "Understanding Cryptocurrencies",
        "text": "A cryptocurrency is a digital or virtual currency secured by cryptography, which makes it nearly impossible to counterfeit or double-spend. Many cryptocurrencies are decentralized networks based on blockchain technology.",
        "links": [("Learn more about Cryptocurrencies", "https://www.investopedia.com/terms/c/cryptocurrency.asp")]
    },
    "education_basic_concepts_wallets": {
        "title": "Understanding Crypto Wallets",
        "text": "A cryptocurrency wallet is a device, physical medium, program or a service which stores the public and/or private keys for cryptocurrency transactions.",
        "links": [("Learn more about Crypto Wallets", "https://www.investopedia.com/terms/c/cryptocurrency-wallet.asp")]
    },
    "education_basic_concepts_exchanges": {
        "title": "Understanding Crypto Exchanges",
        "text": "A cryptocurrency exchange, or a digital currency exchange, is a business that allows customers to trade cryptocurrencies or digital currencies for other assets, such as conventional fiat money or other digital currencies.",
        "links": [("Learn more about Crypto Exchanges", "https://www.investopedia.com/terms/c/cryptocurrencyexchange.asp")]
    },
     "education_technical_analysis_moving_averages": {
        "title": "Moving Averages (MA)",
        "text": "Moving averages smooth out price data to make it easier to identify the trend. There are different types of MA such as the SMA, EMA, etc"
    },
    "education_technical_analysis_rsi_indicator": {
        "title": "Relative Strength Index (RSI)",
        "text": "The Relative Strength Index (RSI) is a momentum indicator that measures the magnitude of recent price changes to evaluate overbought or oversold conditions in the price of a stock or other asset.",
         "links": [("Learn more about RSI", "https://www.investopedia.com/terms/r/rsi.asp")]
    },
    "education_technical_analysis_macd_indicator": {
        "title": "Moving Average Convergence Divergence (MACD)",
        "text": "The Moving Average Convergence Divergence (MACD) is a trend-following momentum indicator that shows the relationship between two moving averages of a security’s price.",
        "links": [("Learn more about MACD", "https://www.investopedia.com/terms/m/macd.asp")]
    },
    "education_technical_analysis_bollinger_bands": {
        "title": "Bollinger Bands",
         "text": "Bollinger Bands are volatility bands placed above and below a moving average. Volatility is based on standard deviation, which changes as volatility increases and decreases. "
    },
     "education_technical_analysis_support_resistance":{
        "title":"Support and Resistance",
        "text": "Support and resistance levels are key areas where price movements are expected to slow or reverse. Support refers to the price level where buying pressure is expected to prevent a price decline, while resistance refers to the price level where selling pressure is expected to prevent a price increase."
     },
    "education_trading_strategies_day_trading":{
        "title": "Day Trading",
        "text":"Day trading is a type of trading in which you buy and sell positions within the same day to profit from small price movements."
    },
      "education_trading_strategies_swing_trading":{
        "title":"Swing Trading",
        "text":"Swing trading is a strategy that involves holding assets for a few days or weeks to capture profits from expected price swings."
    },
    "education_defi_nfts_what_is_defi": {
          "title":"What is DeFi?",
          "text": "DeFi, or Decentralized Finance, uses blockchain technology to offer financial services without centralized intermediaries like banks and financial institutions."
        },
    "education_defi_nfts_what_is_nft":{
        "title":"What are NFTs?",
        "text": "A non-fungible token (NFT) is a unique digital asset representing a wide range of tangible and intangible items, such as artworks, collectibles, and in-game items."
    },
   "education_security_scams": {
        "title":"Common Crypto Scams",
        "text":"There are many crypto scams such as phishing, ponzi schemes and pump and dumps. Always do your own research before you invest."
     }
}


def get_module_by_key(key):
    """
    Get the module by its key
    Args:
         key: a key
    Returns:
         dict: the module info
    """
    if key in educational_content:
       return educational_content[key]
    else:
       return None