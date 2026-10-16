# Smart Agribusiness Management System

A beginner-friendly student project for tracking agricultural products, available stock, and sales records.

## Features
- Add farm products with category, quantity, and unit price.
- View product inventory and total stock units.
- Record sales and automatically reduce available stock.
- View recent sales and total recorded sales value.
- Basic validation to prevent negative quantities and sales above available stock.
- Stores data locally in SQLite.

## Technology
- Python
- Flask
- SQLite
- HTML and CSS
- Git and GitHub for version control

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment (recommended).
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   python app.py
   ```
6. Open `http://127.0.0.1:5000` in your browser.

The SQLite database file is created automatically when the app starts.

## Important
This is a starter implementation for learning and internship practice. Test the application, understand the code, add screenshots and tests, and document any changes you make before submitting it as your own work. Do not claim that features were tested unless you have tested them yourself.
