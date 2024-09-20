import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import logging

# Enable logging for easier debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with actual channel IDs or usernames
CHANNELS = ['@Channel1', '@Channel2', '@Channel3']

# Load the token and admin chat ID from environment variables
TOKEN = os.getenv('7969357167:AAGpyhh1uSXRFMHiugNJTp91YjT7y6riv4M')
admin_chat_id = os.getenv('5878904182')  # Replace with the admin's chat ID

# User data store (simulated database for demo purposes)
user_data_store = {}

# Start command to welcome the user and provide options
def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_data_store[user_id] = {
        "balance": 5000.0,
        "referrals": [],
        "joined": False  # To track if the user has joined all channels
    }

    # Create a keyboard with options
    keyboard = [
        [InlineKeyboardButton("Referral Link", callback_data="referral"),
         InlineKeyboardButton("Balance", callback_data="balance")],
        [InlineKeyboardButton("Bonus", callback_data="bonus")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Welcome message
    update.message.reply_text("Welcome to the VEGIton Airdrop Bot! To proceed, you must join the following channels:")
    
    # Task to join the channels
    task_message = f"1. {CHANNELS[0]}\n2. {CHANNELS[1]}\n3. {CHANNELS[2]}\nOnce you've joined, click 'Check'."
    
    # Send task message
    update.message.reply_text(task_message, reply_markup=reply_markup)
    
    # Add a button to check if the user has joined the channels
    check_keyboard = [[InlineKeyboardButton("Check", callback_data="check_joined")]]
    check_reply_markup = InlineKeyboardMarkup(check_keyboard)
    
    update.message.reply_text("Click 'Check' once you've joined all channels.", reply_markup=check_reply_markup)

# Callback to check if the user has joined the required channels
def check_joined(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    
    # Store unjoined channels
    not_joined_channels = []
    
    # Check if the user has joined each required channel
    for channel in CHANNELS:
        try:
            chat_member = context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            
            # If the user is not a member of the channel
            if chat_member.status not in ['member', 'administrator', 'creator']:
                not_joined_channels.append(channel)
        
        except Exception as e:
            logger.error(f"Error checking channel membership for user {user_id}: {e}")
            query.message.reply_text("An error occurred while checking your membership. Please try again.")
            return

    # If the user hasn't joined all required channels
    if not_joined_channels:
        query.message.reply_text(f"❌ You haven't joined the following channels:\n{', '.join(not_joined_channels)}\nPlease join them and try again.")
    else:
        query.message.reply_text(f"✅ Thank you for joining all the channels! You are now eligible to participate.")
        user_data_store[user_id]['joined'] = True
    
    query.answer()

# Handlers for other callbacks (e.g., referral, balance, bonus)
def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "referral":
        query.message.reply_text(f"Your referral link is: t.me/TestVegi?start={user_id}")
    
    elif query.data == "balance":
        balance = user_data_store[user_id]['balance']
        query.message.reply_text(f"Your current balance is: {balance} tokens")
    
    elif query.data == "bonus":
        query.message.reply_text("You can earn bonus VEGIton_point by referring others!")
    
    query.answer()

# Main function to set up the bot
def main():
    # Initialize the updater and dispatcher
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add command handler for /start
    dp.add_handler(CommandHandler("start", start))

    # Add callback handler for checking joined channels and other callbacks
    dp.add_handler(CallbackQueryHandler(check_joined, pattern="check_joined"))
    dp.add_handler(CallbackQueryHandler(handle_callback, pattern="referral|balance|bonus"))

    # Start polling
    updater.start_polling()

    # Run the bot until Ctrl-C is pressed
    updater.idle()

# Command to handle the referral link generation
def referral(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    # Create and store referral link based on user_id
    referral_link = f"https://t.me/YourBotUsername?start={user_id}"

    # Initialize user data if they are new
    if user_id not in user_data_store:
        user_data_store[user_id] = {"balance": 0, "referrals": []}

    # Send the referral link to the user
    query.message.reply_text(f"Your referral link: {referral_link}")
    query.answer()

# Command to handle new users joining through the referral link
def start(update: Update, context: CallbackContext):
    # Get user who started the bot (new user)
    new_user_id = update.message.from_user.id

    # Get the argument passed in the referral link (referrer user_id)
    if context.args:
        referrer_id = context.args[0]  # This is the user_id of the person who referred the new user

        # Check if referrer exists in the user data store
        if int(referrer_id) in user_data_store:
            # Add 5 points to the referrer's balance
            user_data_store[int(referrer_id)]["balance"] += 500

            # Optionally, store the referral
            user_data_store[int(referrer_id)]["referrals"].append(new_user_id)

            # Notify the referrer about the successful referral
            context.bot.send_message(chat_id=int(referrer_id), 
                                     text=f"🎉 You earned 500 points for referring a new user! Your current balance is: {user_data_store[int(referrer_id)]['balance']} VEGIton_points.")

    # Initialize new user in the database
    if new_user_id not in user_data_store:
        user_data_store[new_user_id] = {"balance": 0, "referrals": []}

    # Send welcome message to the new user
    update.message.reply_text("Welcome to the VEGIton_Airdrop Bot! You've successfully started using the bot.")

# Check user balance
def balance(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    balance = user_data_store[user_id].get("balance", 0)
    
    query.message.reply_text(f"Your balance is: {balance} VEGIton_points")
    query.answer()

# Give bonus for users
def bonus(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    
    if not user_data_store[user_id]["joined"]:
        query.message.reply_text("You need to join our channels to claim bonus.")
    else:
        user_data_store[user_id]["balance"] += 1500
        query.message.reply_text(f"🎁 Bonus claimed! New balance: {user_data_store[user_id]['balance']} tokens.")
    
    query.answer()

# Admin Command to view user details
def admin_view_users(update: Update, context: CallbackContext):
    if update.message.chat_id == int(admin_chat_id):
        user_list = ""
        for user_id, data in user_data_store.items():
            user_list += f"User ID: {user_id}, Balance: {data['balance']}, Referrals: {len(data['referrals'])}\n"
        update.message.reply_text(user_list if user_list else "No users found.")
    else:
        update.message.reply_text("You are not authorized to perform this action.")

# Main function
def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin_view", admin_view_users))  # Only admin can use this
    dp.add_handler(CallbackQueryHandler(referral, pattern="referral"))
    dp.add_handler(CallbackQueryHandler(balance, pattern="balance"))
    dp.add_handler(CallbackQueryHandler(bonus, pattern="bonus"))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
