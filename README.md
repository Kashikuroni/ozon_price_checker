# Ozon Price Check — TUI

A tiny terminal UI to quickly inspect a product’s financial summary from OZON.

## Prerequisites

- **uv** (Python package/dependency manager)

## Setup
# 1) Install uv (if you don’t have it yet)
https://docs.astral.sh/uv/getting-started/installation/
```bash
# Clone the repository
git clone git@github.com:Kashikuroni/ozon_price_checker.git
cd ozon_price_checker

# Install dependencies
uv sync
```

## Run

```bash
# Start the app
uv run src/main.py
```

On first launch, you’ll be prompted to enter:

- **Client-id**
- **Api-key** (both provided by OZON)

## How to use

1. Enter the **product SKU**.
2. Enter its **purchase price**.
3. Press **F5** — you’ll get a financial summary for the product.

**Shortcuts**

- **F5** — fetch & update data
- **ESC** — clear input fields

Then repeat:

- Re-enter SKU and price → press **F5** → get new data. Continue in a loop.
