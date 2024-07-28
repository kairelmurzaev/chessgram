import os
from telegram.ext import Updater, CommandHandler
import logging
import chess
from collections import defaultdict

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Get the bot token from environment variables
TOKEN = os.getenv('7475295731:AAER-oBJiOvYEqc_6MLcfWS_sIIKZqyQiHE')

# Initialize the bot and dispatcher
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Store game states in a dictionary
games = {}

# Store ratings in a dictionary (default rating is 1200)
ratings = defaultdict(lambda: 1200)

def start(update, context):
    update.message.reply_text('Hi! I am your Chess bot. Use /play to start a game.')

def start_game(update, context):
    chat_id = update.message.chat_id
    if chat_id in games:
        update.message.reply_text('A game is already in progress.')
        return
    
    board = chess.Board()
    games[chat_id] = board
    update.message.reply_text('Game started! Your move: /move <from> <to>')

def move(update, context):
    chat_id = update.message.chat_id
    if chat_id not in games:
        update.message.reply_text('No game in progress. Start a new game with /play.')
        return
    
    board = games[chat_id]
    move = ' '.join(context.args)
    try:
        board.push_san(move)
        update.message.reply_text(f'Move accepted: {move}')
        
        if board.is_game_over():
            update.message.reply_text(f'Game over! Result: {board.result()}')
            del games[chat_id]
        else:
            update.message.reply_text('Your turn!')
    except ValueError:
        update.message.reply_text('Invalid move. Try again.')

def get_rating(update, context):
    user = update.message.from_user
    rating = ratings[user.id]
    update.message.reply_text(f'Your rating: {rating}')

def update_ratings(winner_id, loser_id):
    winner_rating = ratings[winner_id]
    loser_rating = ratings[loser_id]
    
    k = 30  # Adjust based on your rating system
    expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    expected_loser = 1 - expected_winner
    
    ratings[winner_id] += k * (1 - expected_winner)
    ratings[loser_id] += k * (0 - expected_loser)

def main():
    # Add command handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('play', start_game))
    dispatcher.add_handler(CommandHandler('move', move))
    dispatcher.add_handler(CommandHandler('rating', get_rating))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
