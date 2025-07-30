⏺ OZON Price Check TUI - Installation and Usage Guide

Prerequisites

- Python 3.13 or higher
- https://docs.astral.sh/uv/ package manager

Installation

1. Install uv (if not already installed)

# macOS and Linux

curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows

powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Via pip

pip install uv

2. Clone and Install the Application

# Navigate to the project directory

cd /path/to/ozon-price-check

# Install the application and dependencies

uv sync

# Install in development mode (if you want to modify the code)

uv pip install -e .

3. Alternative: Install from Package

# If you want to install as a standalone package

uv pip install .

Configuration

1. Get OZON API Credentials

Before using the application, you need OZON Seller API credentials:

1. Log into your OZON Seller account
2. Go to Settings > API Keys
3. Generate a new API key
4. Note your Client ID and API Key

5. First Run - Onboarding

When you first run the application, it will automatically prompt you to enter your credentials:

# Run the application

uv run ozon-price

# or

uv run price-check

The onboarding screen will ask for:

- Client ID: Your OZON Client ID (numeric)
- API Key: Your OZON API Key (string)
- Base URL: API endpoint (defaults to https://api-seller.ozon.ru)

Credentials are securely stored in your system keyring.

Usage

Starting the Application

# Method 1: Using the installed script

uv run ozon-price

# Method 2: Alternative script name

uv run price-check

# Method 3: Run as module

uv run python -m ozon_price_check.main

TUI Interface Overview

The application has a two-panel layout:

Left Panel (Input):

- SKU input field
- Price input field (optional)
- Help text with keyboard shortcuts

Right Panel (Information):

- Product information sections
- Error messages
- Profit calculations (when price is provided)

Basic Usage

1. Enter SKU: Type the product SKU/offer ID in the first field
2. Enter Price (optional): Your purchase price for profit calculation


    - Supports both comma (123,45) and dot (123.45) decimal separators

3. Fetch Data: Press F5 to retrieve product information

Keyboard Shortcuts

| Key    | Action                                  |
| ------ | --------------------------------------- |
| F5     | Fetch product data                      |
| Tab    | Switch between input fields             |
| F6     | Focus swap between SKU and price fields |
| Esc    | Clear input fields                      |
| Ctrl+L | Clear product information panel         |
| Ctrl+C | Exit application                        |

Example Workflow

1. Start the application:
   uv run ozon-price
2. Enter a product SKU (e.g., "ABC123")
3. (Optional) Enter your purchase price (e.g., "150,50" or "150.50")
4. Press F5 to fetch data
5. Review the displayed information:


    - Profit Calculation: Shows profit, margin, commissions
    - Product Details: Basic product information
    - Pricing: Current prices, minimum prices
    - Commissions: Detailed commission breakdown
    - Marketing Actions: Active promotions and discounts

Information Sections

When data is successfully fetched, you'll see several sections:

1. Profit Calculations (if price entered)

- Current Price Profit: Based on marketing seller price
- Minimum Price Profit: Based on minimum allowed price
- Shows total commissions, profit amount, and profit margin percentage

2. Basic Product Information

- Product ID, offer ID, SKU
- Product status and visibility
- Stock information

3. Pricing Information

- Current prices (marketing, minimum, etc.)
- Price recommendations
- Auto-calculated pricing

4. Commission Details

- FBS/FBO commission rates
- Fixed and percentage-based fees
- Total commission calculations

5. Marketing Actions

- Active promotions
- Discount periods
- Special offers

6. Price Indexes

- Competitive pricing data
- External marketplace comparisons
- OZON-specific pricing insights

Troubleshooting

Common Issues

1. "No Client ID or API Key"


    - Run the onboarding process again
    - Verify credentials in OZON Seller dashboard

2. "No product found for SKU"


    - Check SKU spelling
    - Ensure product exists in your OZON catalog
    - Verify product visibility settings

3. Price format errors


    - Use either comma (123,45) or dot (123.50) format
    - Don't mix separators in the same number

4. API connection issues


    - Check internet connection
    - Verify API credentials are still valid
    - Check OZON API status

Re-running Onboarding

To update your credentials:

# Delete stored credentials and restart

uv run python -c "import keyring; keyring.delete_password('price-check', 'OZON_API_KEY'); keyring.delete_password('price-check', 'OZON_CLIENT_ID')"
uv run ozon-price

Logs and Debugging

The application creates log files in the project directory:

- debug.log: Detailed debugging information
- error.log: Error messages and stack traces

Development

Running in Development Mode

# Install in development mode

uv pip install -e .

# Run with Python directly

uv run python ozon_price_check/main.py

# Run tests (if available)

uv run pytest

Project Structure

ozon_price_check/
├── **init**.py
├── main.py # TUI application entry point
├── core_client.py # HTTP client for API requests
├── client.py # OZON API client wrapper
├── credentials.py # Credential management
├── schemas.py # Pydantic data models
├── constants.py # API endpoints and constants
├── onboarding.py # Initial setup screen
├── services/
│ └── products.py # Product data processing
├── i18n/
│ └── ru_labels.py # Russian language labels
└── types.py # Type definitions

This TUI application provides a fast, efficient way to check OZON product information and calculate profit margins directly from your terminal.
