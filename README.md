# Crypto Analyzer Bot

A comprehensive Telegram bot for cryptocurrency analysis, technical indicators, market data tracking, and educational resources. The bot provides real-time analysis, interactive charts, and multi-language support for cryptocurrency traders and enthusiasts.

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
- Reddit crypto subreddit monitoring
- Twitter/X cryptocurrency mentions analysis
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

## Technology Stack

### Backend
- Python 3.10+
- SQLAlchemy for database management
- TA-Lib for technical analysis
- pandas and numpy for data processing

### APIs and Services
- Telegram Bot API
- CoinGecko API for market data
- CryptoCompare API for news
- Reddit API for social sentiment
- Twitter/X API for social monitoring

### Data Visualization
- mplfinance for candlestick charts
- Plotly for interactive charts
- datapane for report generation
- Custom SVG generation

### Database
- SQLite for local storage
- Support for multiple database types through SQLAlchemy

## Setup Instructions

### Prerequisites
1. Python 3.10 or higher
2. pip package manager
3. TA-Lib installation (system dependent)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crypto_analyzer_bot.git
cd crypto_analyzer_bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install TA-Lib:
- Windows: Use the provided wheel files:
  ```bash
  pip install TA_Lib-0.4.28-cp310-cp310-win_amd64.whl
  ```
- Linux/Mac:
  ```bash
  sudo apt-get install ta-lib  # Ubuntu/Debian
  brew install ta-lib         # MacOS
  ```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and tokens
```

### API Keys Required
- Telegram Bot Token
- CoinGecko API Key
- CryptoCompare API Key
- Reddit API Credentials
- Twitter/X API Credentials

## Usage Examples

### Basic Commands
```python
# Start the bot
python main.py

# Run tests
python -m pytest tests/
```

### Telegram Commands
```
/start - Start the bot and show main menu
/analyze [symbol] - Full technical analysis
/quick [symbol] - Quick market overview
/chart [symbol] [type] - Generate specific chart
/news [symbol] - Get latest news and sentiment
```

### Analysis Examples
```python
# Quick analysis
/quick btc

# Full analysis with timeframe
/analyze eth 1w

# Custom chart
/chart btc macd 1d
```

## Project Structure
```
crypto_analyzer_bot/
├── src/
│   ├── analysis/         # Technical analysis modules
│   ├── bot/             # Telegram bot handlers
│   ├── data/            # Data fetching and processing
│   ├── languages/       # Language files
│   ├── services/        # API services
│   └── utils/           # Utility functions
├── tests/               # Test files
├── docs/               # Documentation
├── scripts/            # Deployment scripts
└── main.py            # Entry point
```

## System Flow and Architecture

### Overall Architecture
```
User (Telegram) -> Bot Handlers -> Analysis System -> Data Services -> External APIs
                                                  -> Database
                                                  -> Formatters -> User
```

### Main Components Flow

1. **User Interaction Flow**
   ```
   User -> Telegram Bot
        -> Message Handler
        -> Command Router
        -> Specific Handler (Analysis/Chart/News)
        -> Response Formatter
        -> User
   ```

2. **Analysis Flow**
   ```
   Analysis Request -> Data Fetcher
                   -> Technical Analyzer
                   -> Indicator Calculator
                   -> Pattern Recognition
                   -> Summary Generator
                   -> Chart Generator
                   -> Formatted Response
   ```

3. **Data Processing Flow**
   ```
   Raw Data -> Data Processor
            -> OHLCV Converter
            -> Technical Indicators
            -> Pattern Detection
            -> Support/Resistance
            -> Market Summary
   ```

4. **Chart Generation Flow**
   ```
   Chart Request -> Data Validator
                -> Style Generator
                -> Chart Type Router
                -> Specific Chart Builder
                -> PDF/HTML Generator
                -> Document Sender
   ```

### Detailed Component Interactions

1. **Message Processing**
   - User sends command to bot
   - Message handler identifies command type
   - Routes to appropriate handler
   - Handler validates input
   - Processes request
   - Formats and returns response

2. **Technical Analysis**
   - Fetches market data from CoinGecko
   - Processes OHLCV data
   - Calculates technical indicators
   - Identifies patterns
   - Generates comprehensive analysis
   - Creates visualization charts

3. **News Analysis**
   - Fetches news from multiple sources
   - Processes text content
   - Performs sentiment analysis
   - Aggregates results
   - Formats news summary

4. **Data Management**
   - Validates incoming data
   - Caches frequently accessed data
   - Manages database connections
   - Handles API rate limiting
   - Provides data to analysis modules

### State Management

1. **User States**
   - Tracks current user activity
   - Manages analysis sessions
   - Handles language preferences
   - Maintains user settings

2. **Cache Management**
   - Implements data caching
   - Manages cache invalidation
   - Optimizes API calls
   - Reduces response time

3. **Error Handling**
   - Validates user input
   - Handles API errors
   - Manages network issues
   - Provides user feedback

### Language System

1. **Message Flow**
   ```
   User Input -> Language Detector
              -> Message Selector
              -> Template Processor
              -> Formatted Output
   ```

2. **Translation Process**
   - Detects user language
   - Loads appropriate messages
   - Processes templates
   - Formats response

### Security Measures

1. **Data Protection**
   - API key management
   - Rate limiting
   - Input validation
   - Error handling

2. **User Protection**
   - Command validation
   - Input sanitization
   - Response filtering
   - Error messaging

### Performance Optimization

1. **Data Caching**
   - Markets data
   - Technical analysis
   - News content
   - User preferences

2. **Response Optimization**
   - Async processing
   - Batch operations
   - Efficient querying
   - Resource management

### Testing Process

1. **Testing Flow**
   ```
   Code Changes -> Unit Tests
                -> Integration Tests
                -> System Tests
                -> Performance Tests
                -> Deployment
   ```

2. **Continuous Integration**
   - Automated testing
   - Code quality checks
   - Performance monitoring
   - Deployment verification

This flow documentation provides a comprehensive overview of how different components interact within the system. Each component is designed to be modular and maintainable, allowing for easy updates and extensions to the system's functionality.
