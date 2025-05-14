import os   # operating system module
import re   # regular expression module
from dotenv import load_dotenv   # load environment variables from .env file
from telegram import Update   # Telegram API modules
from telegram.ext import Application, CommandHandler, MessageHandler,ContextTypes, filters    # Telegram bot modules
from langchain_groq import ChatGroq  # Langchain module for groq
from langchain_core.prompts import ChatPromptTemplate  # Langchain module for chat prompts
from langchain_core.output_parsers import StrOutputParser  # Langchain module for output parsing

load_dotenv()  # Load environment variables from .env file

# Set environment variables for Langchain API
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_TRACING_V2"] = "true" # Set to "true" to enable tracing of execution on Langsmith portal
groq_api_key = os.getenv("GROQ_API_KEY")  # Get Groq API key from environment variable  

def setup_llm_chain(topic="technology"):
    """
    Set up the LLM chain with the given topic.
    """
    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a joking AI. Give me only one funny joke on the given topic"),
            ("user", f"generate a joke on the topic: {topic}") 
        ]
    )

    # Initialize the LLM with Groq API key
    llm = ChatGroq(
        model = "Gemma2-9b-It",
        groq_api_key = groq_api_key
    )

    return prompt | llm | StrOutputParser()  # Create a chain with the prompt and output parser

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /start command.
    """
    await update.message.reply_text("Hi! Mention me with a topic like '@Binary_Joke_Chatbot python' to get a joke")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /help command.
    """
    await update.message.reply_text("Mention me with a topic like '@Binary_Joke_Chatbot python' to get some funny joke")     

async def generate_joke(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    """
    Handle the message containing the topic for the joke.
    """
    await update.message.reply_text(f"Generating a joke about {topic}...")  # Send a message indicating that the joke is being generated
    joke = setup_llm_chain(topic).invoke({}).strip()  # Generate the joke using the LLM chain 
    await update.message.reply_text(joke)  # Send the generated joke back to the user   

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming messages.
    """
    msg = update.message.text  # Get the text of the incoming message
    bot_username = context.bot.username  # Get the bot's username   
    if f'@{bot_username}' in msg:
        match = re.search(f'@{bot_username}\\s+(.*)',msg)  # Search for the topic in the message
        if match and match.group(1).strip():
            await generate_joke(update, context, match.group(1).strip())  # If a topic is found, generate a joke    
        else:
            await update.message.reply_text("Please specify a topic after mentioning me.")

def main():
    """
    Main function to run the Telegram bot.
    """
    token = os.getenv("TELEGRAM_API_KEY")  # Get the Telegram bot token from environment variable   
    app= Application.builder().token(token).build()  # Create a new Telegram bot application
    app.add_handler(CommandHandler("start", start))  # Add command handler for /start command   
    app.add_handler(CommandHandler("help", help_command))  # Add command handler for /help command  
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Add message handler for text messages   
    app.run_polling(allowed_updates=Update.ALL_TYPES)     # Start polling for updates from Telegram

if __name__ == "__main__":
    main()  # Run the main function to start the bot    



