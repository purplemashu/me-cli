# MYnyak Engsel

![banner](bnr.png)

CLI client for a certain Indonesian mobile internet service provider, now with support for both Termux and VPS, and a bot integration entry point.

# How to get API Key
Chat telegram bot [@fykxt_bot](https://t.me/fykxt_bot) with message `/viewkey`. Copy the API key.

# How to Run (Termux & VPS)
The setup script is designed to work on both Termux and Debian-based Linux systems (like Ubuntu on a VPS).

1. **Clone this repo**
   ```
   git clone https://github.com/purplemashu/me-cli
   ```

2. **Open the folder**
   ```
   cd me-cli
   ```

3. **Run the setup script**
   This will automatically detect your environment and install the necessary dependencies.
   ```
   bash setup.sh
   ```

4. **Run the application**
   Use the `run.sh` script to choose how you want to start the application.
   ```
   bash run.sh
   ```
   You will be presented with a menu to either:
   - **Start the CLI:** The interactive command-line interface.
   - **Start the Bot:** A sample entry point showing how to use the core functions in a bot.

   When you run the CLI for the first time, you will be prompted to log in and input your API key.

# Bot Integration
This project has been refactored to separate the core logic from the user interface. This means you can easily integrate its features into your own bots (e.g., Telegram, Discord).

The `bot.py` file serves as an example and an entry point for this purpose. You can import the functions from `bot.py` into your bot's code to perform actions like:
- Listing accounts (`bot_list_accounts`)
- Getting balance (`bot_get_balance`)
- Listing user's packages (`bot_list_my_packages`)
- And more.

Check the `bot.py` file for examples of how to use these functions.

# Info

## PS for Certain Indonesian mobile internet service provider

Instead of just delisting the package from the app, ensure the user cannot purchase it.
What's the point of strong client side security when the server don't enforce it?

## Contact

contact@mashu.lol