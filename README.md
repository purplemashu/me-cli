# MYnyak Engsel

![banner](bnr.png)

CLI client for a certain Indonesian mobile internet service provider.

# How to get API Key
Chat telegram bot [@fykxt_bot](https://t.me/fykxt_bot) with message `/viewkey`. Copy the API key.

# How to Run

## CLI Mode
To run the application in command-line interface mode, simply run:
```bash
python main.py
```

## Telegram Bot Mode
1. **Clone the repository:**
   ```bash
   git clone https://github.com/purplemashu/me-cli
   cd me-cli
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory and add the following variables. You can get the `API_KEY` from the [@fykxt_bot](https://t.me/fykxt_bot) on Telegram.
   ```
   BASE_API_URL=your_base_api_url
   BASE_CIAM_URL=your_base_ciam_url
   BASIC_AUTH=your_basic_auth
   AX_DEVICE_ID=your_ax_device_id
   AX_FP=your_ax_fp
   UA=your_user_agent
   API_KEY=your_api_key
   AES_KEY_ASCII=your_aes_key_ascii
   TELEGRAM_TOKEN=your_telegram_bot_token
   ```

4. **Run the bot:**
   ```bash
   python main.py bot
   ```

### Bot Usage
The bot uses an interactive menu. Simply send `/start` to begin and follow the on-screen buttons.

**Available Commands:**
- `/start`: Shows the main menu.
- `/login`: Starts the login process.
- `/buy <package_option_code>`: Buys a specific package.

# Info

## PS for Certain Indonesian mobile internet service provider

Instead of just delisting the package from the app, ensure the user cannot purchase it.
What's the point of strong client side security when the server don't enforce it?

## Contact

contact@mashu.lol
