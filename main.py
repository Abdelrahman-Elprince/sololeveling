import sqlite3
import os
from functions.database import Database
from functions.player import Player
from functions.stats import Stats

def initialize_game():
    # Create functions directory if it doesn't exist
    if not os.path.exists('functions'):
        os.makedirs('functions')
    
    # Initialize database
    db = Database('liferpg.db')
    
    # Check if player exists
    player_data = db.get_player()
    
    if not player_data:
        # First time player - prompt for name
        print("Welcome to LifeRPG!")
        player_name = input("Please enter your player name: ").strip()
        
        # Create new player
        player = Player(player_name)
        db.create_player(player_name)
        # Initialize player stats and quests
        stats = Stats(player_name, db)
        stats.initialize_stats()
        db.assign_daily_quests(player_name)
        print(f"Welcome {player_name}! Your adventure begins!")
    else:
        print(f"Welcome back {player_data[1]}!")
        player = Player(player_data[1])
        player.status = 'live'
        # Reset daily quests if needed
        db.reset_daily_quests(player_data[1])
    
    return player, db

def main():
    player, db = initialize_game()
    stats = Stats(player.name, db)
    print(f"Player Status: {player.status}")
    stats.display_stats()
    
    # Quest loop
    while True:
        quests = db.get_available_quests(player.name)
        if not quests:
            print("\nNo quests available!")
            break
        
        print("\nAvailable Quests:")
        for i, quest in enumerate(quests, 1):
            quest_type = quest[6]
            extra_info = ''
            if quest_type == 'routine':
                extra_info = f" ({quest[7]})"
            elif quest_type == 'challenge':
                extra_info = f" (Time Limit: {quest[7]}, Streak: {quest[8]})"
            print(f"{i}. {quest[1]} ({quest[4]} EXP, {quest[5]} Coins){extra_info}")
        
        choice = input(f"Choose a quest (1-{len(quests)} or {len(quests)+1} to Exit): ").strip()
        try:
            choice = int(choice)
            if choice == len(quests) + 1:
                break
            if 1 <= choice <= len(quests):
                quest = quests[choice - 1]
                quest_id, name, description, child_skill_id, exp_reward, coin_reward, quest_type = quest[:7]
                stats.complete_quest(quest_id, quest_type, child_skill_id, exp_reward, coin_reward)
                print(f"\nCompleted quest: {name}")
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Invalid input. Enter a number.")
        
        stats.display_stats()

if __name__ == "__main__":
    main()