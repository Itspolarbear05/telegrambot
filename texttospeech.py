import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from gtts import gTTS

CHUNK_SIZE = 1024

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())  # Add this line

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send me text, and I will convert it to audio!')

def process_text(update: Update, context: CallbackContext) -> None:
    try:
        # Get the text from the user's message
        text = update.message.text

        # Send a waiting message to the user
        wait_message = update.message.reply_text("Please wait while I generate the audio...")

        # Use gTTS to generate audio from text
        tts = gTTS(text=text, lang='en')
        tts.save('output.mp3')

        # Send the audio file to the user
        update.message.reply_audio(audio=open('output.mp3', 'rb'))

    except Exception as e:
        logger.error(f"Error processing text: {e}")
        update.message.reply_text("An error occurred while processing the text. Please try again.")

    finally:
        # Clean up temporary files
        if 'output.mp3' in locals():
            context.job_queue.run_once(remove_temp_file, 60, context=update.message.chat_id)

        # Delete the waiting message
        wait_message.delete()

def remove_temp_file(context: CallbackContext) -> None:
    try:
        os.remove('output.mp3')
        logger.info("Temporary audio file removed.")
    except Exception as e:
        logger.error(f"Error removing temporary audio file: {e}")

def welcome(update: Update, context: CallbackContext) -> None:
    for new_user in update.message.new_chat_members:
        # Send a welcome message and a "start" button
        welcome_message = f"Welcome {new_user.mention_html()}!\n\nSend me text, and I will convert it to audio!"
        keyboard = [[InlineKeyboardButton("Start", callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_html(welcome_message, reply_markup=reply_markup)

def main():
    # Replace 'YOUR_BOT_TOKEN' with the actual token from BotFather
    updater = Updater(token='6942529674:AAEQCYrrDE5emw-GJsjzP8ZhnSHexvSH5w0', use_context=True)

    dp = updater.dispatcher

    # CommandHandler to handle the /start command
    dp.add_handler(CommandHandler("start", start))

    # MessageHandler to handle text messages only after the user has started the bot
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, process_text))

    # Welcome message handler
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
