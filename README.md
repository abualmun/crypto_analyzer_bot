
# Crypto Analyzer Bot

A comprehensive Telegram bot for cryptocurrency analysis, technical indicators, market data tracking, and educational resources. The bot provides real-time analysis, interactive charts, and multi-language support for cryptocurrency traders and enthusiasts.

---

## Features

### Technical Analysis
- Real-time price analysis and market data
- Technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Support and resistance level detection
- Volume analysis and custom chart generation
- Price trend analysis and momentum indicators

### Market Data Tracking
- Historical OHLCV (Open, High, Low, Close, Volume) data
- Multiple timeframe support (1d, 1w, 1m, 3m)
- Real-time price updates and market statistics
- Volume profile and market depth analysis

### News Analysis
- Integration with CryptoCompare News API
- Sentiment analysis for news and social media

### Educational Resources
- Cryptocurrency learning materials
- Trading strategy guides
- Technical analysis explanations
- Market terminology definitions

### Multi-language Support
- English and Arabic language support
- Extensible language system
- Custom message formatting for each language

---

## Technology Stack

### Backend
- Python 3.10+
- Postgres for database management
- TA-Lib for technical analysis
- `pandas` and `numpy` for data processing

### APIs and Services
- Telegram Bot API
- CoinGecko API for market data
- CryptoCompare API for news

### Data Visualization
- `mplfinance` for candlestick charts
- `Plotly` for interactive charts
- `datapane` for report generation
- Custom SVG generation

### Database
- SQLite for local storage
- Support for multiple database types through SQLAlchemy

---

## Setup Instructions

### ðŸ³ Installation with Docker (Recommended)

This method is the easiest way to run the bot with all dependencies set up in containers.

#### Steps

1. **Install Docker Desktop**  
   ðŸ‘‰ [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

2. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/crypto_analyzer_bot.git
   cd crypto_analyzer_bot
   ```

3. **Open Docker Terminal**  
   Navigate to the project directory and build the Docker image:
   ```bash
   docker build -t telegram .
   ```

4. **Install the official Postgres image**  
   From Docker Desktop, search for **postgres** and pull the image.

5. **Go to the "Images" tab in Docker Desktop**  
   Locate the `postgres` image.

6. **Run the Postgres container**
   ```bash
   docker run -d --name crypto_analytics_db      -e POSTGRES_USER=postgres      -e POSTGRES_PASSWORD=123123      -e POSTGRES_DB=crypto_analytics      -p 5432:5432      -v postgres_data:/var/lib/postgresql/data      postgres
   ```

7. **Run the Telegram bot container**
   Replace the tokens with your actual API credentials:
   ```bash
   docker run -d --name telegram_container      --network crypto_network      -e TELEGRAM_BOT_TOKEN=replace_your_telegram_token      -e CRYPTO_NEWS_TOKEN=replace_your_crypto_news_token      -e GOOGLE_API_KEY=replace_your_google_api_key      -e POSTGRES_USER=postgres      -e POSTGRES_PASSWORD=123123      -e POSTGRES_HOST=crypto_analytics_db      -e POSTGRES_PORT=5432      -e POSTGRES_DB=crypto_analytics      -p 3000:3000 telegram
   ```

---

### ðŸ§° Prerequisites (For Manual Setup)
- Python 3.10 or higher
- pip package manager
- TA-Lib installation (system dependent)

---

### ðŸ”§ Manual Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/crypto_analyzer_bot.git
   cd crypto_analyzer_bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install TA-Lib**:

   **Windows:**
   ```bash
   pip install TA_Lib-0.4.28-cp310-cp310-win_amd64.whl
   ```

   **Linux/Mac:**
   ```bash
   sudo apt-get install ta-lib       # Ubuntu/Debian
   brew install ta-lib               # MacOS
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and tokens
   ```

---

### ðŸ” API Keys Required

- Telegram Bot Token  
- CoinGecko API Key  
- CryptoCompare API Key  
- Reddit API Credentials  
- Twitter/X API Credentials  

---

## ðŸ“¦ Usage Examples

### Basic Commands

```bash
# Start the bot
python main.py

# Run tests
python -m pytest tests/
```

### Telegram Commands

- `/start` â€” Start the bot and show main menu  
- `/analyze [symbol]` â€” Full technical analysis  
- `/quick [symbol]` â€” Quick market overview  
- `/chart [symbol] [type]` â€” Generate specific chart  
- `/news [symbol]` â€” Get latest news and sentiment  

### Analysis Examples

```bash
/quick btc
/analyze eth 1w
/chart btc macd 1d
```

---

## ðŸ“ Project Structure

```
crypto_analyzer_bot/
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ analysis/         # Technical analysis modules
â”‚   â”œâ”€â”€ bot/              # Telegram bot handlers
â”‚   â”œâ”€â”€ data/             # Data fetching and processing
â”‚   â”œâ”€â”€ languages/        # Language files
â”‚   â”œâ”€â”€ services/         # API services
â”‚   â””â”€â”€ utils/            # Utility functions
â”œâ”€â”€ tests/                # Test files
â”œâ”€â”€ docs/                 # Documentation
â”œâ”€â”€ scripts/              # Deployment scripts
â””â”€â”€ main.py               # Entry point
```

---

## ðŸ§  System Flow and Architecture

### Overall Architecture

```
User (Telegram) -> Bot Handlers -> Analysis System -> Data Services -> External APIs
                                                  -> Database
                                                  -> Formatters -> User
```

### Component Flows

#### User Interaction Flow

```
User -> Telegram Bot
     -> Message Handler
     -> Command Router
     -> Specific Handler (Analysis/Chart/News)
     -> Response Formatter
     -> User
```

#### Analysis Flow

```
Analysis Request -> Data Fetcher
                -> Technical Analyzer
                -> Indicator Calculator
                -> Pattern Recognition
                -> Summary Generator
                -> Chart Generator
                -> Formatted Response
```

#### Data Processing Flow

```
Raw Data -> Data Processor
         -> OHLCV Converter
         -> Technical Indicators
         -> Pattern Detection
         -> Support/Resistance
         -> Market Summary
```

#### Chart Generation Flow

```
Chart Request -> Data Validator
             -> Style Generator
             -> Chart Type Router
             -> Specific Chart Builder
             -> PDF/HTML Generator
             -> Document Sender
```

---

## ðŸ”„ Component Interactions

### Message Processing

- Command parsing and validation  
- Handler routing  
- Output formatting and delivery

### Technical Analysis

- Fetch and preprocess market data  
- Indicator calculation (MACD, RSI, etc.)  
- Pattern recognition  
- Chart rendering  

### News Analysis

- News API integration  
- Sentiment scoring  
- Summary generation  

---

## ðŸ› ï¸ Data Management

- Database schema and migrations  
- Caching layer for performance  
- API rate limit management  

---

## ðŸ‘¥ State Management

- User session tracking  
- Preference storage (e.g., language)  
- Cache and timeout handling  

---

## ðŸ›¡ï¸ Security Measures

- Input sanitization  
- API key protection  
- Safe error handling  

---

## ðŸš€ Performance Optimization

- Asynchronous processing  
- Data caching  
- Efficient queries and batching  

---

## âœ… Testing Process

- Unit and integration tests  
- Performance testing  
- CI/CD integration for deployment

---

This documentation outlines the core features, installation, and architecture of the Crypto Analyzer Bot. For further contributions, issues, or enhancements, please refer to the `docs/` directory or open a GitHub issue.