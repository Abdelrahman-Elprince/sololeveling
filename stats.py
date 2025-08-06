class Stats:
    def __init__(self, player_name, db):
        self.player_name = player_name
        self.db = db
        self.child_skills = {
            1: 'Stamina', 2: 'Mobility', 3: 'Balance',
            4: 'Reading', 5: 'Focus', 6: 'Language Learning', 7: 'Critical Thinking',
            8: 'Discipline', 9: 'Practice', 10: 'Reflection',
            11: 'Weight Training', 12: 'Core', 13: 'Endurance'
        }
    
    def initialize_stats(self):
        self.db.initialize_player_stats(self.player_name)
    
    def gain_exp(self, child_skill_id, exp_amount, quest_coins):
        if child_skill_id in self.child_skills:
            child_level_diff, life_skill_level_diff, player_level_diff, total_coins = self.db.update_skill_exp(
                self.player_name, child_skill_id, exp_amount, quest_coins)
            
            print(f"Gained {exp_amount} EXP in {self.child_skills[child_skill_id]}!")
            if child_level_diff > 0:
                self.db.cursor.execute('SELECT level FROM child_skills WHERE id = ?', (child_skill_id,))
                new_child_level = self.db.cursor.fetchone()[0]
                print(f"{self.child_skills[child_skill_id]} leveled up to {new_child_level}! Earned {child_level_diff * 20} coins!")
            if life_skill_level_diff > 0:
                life_skill_name = self.db.get_player_stats(self.player_name)[child_skill_id-1][0]
                new_life_skill_level = self.db.get_player_stats(self.player_name)[child_skill_id-1][1]
                print(f"{life_skill_name} leveled up to {new_life_skill_level}! Earned {life_skill_level_diff * 50} coins!")
            if player_level_diff > 0:
                new_player_level = self.db.get_player_level(self.player_name)[0]
                print(f"Player leveled up to {new_player_level}! Earned {player_level_diff * 100} coins!")
            if quest_coins > 0:
                print(f"Earned {quest_coins} coins from quest!")
        else:
            print("Invalid child skill ID.")
    
    def complete_quest(self, quest_id, quest_type, child_skill_id, exp_amount, coin_reward):
        self.db.complete_quest(self.player_name, quest_id, quest_type, child_skill_id, exp_amount, coin_reward)
    
    def display_stats(self):
        player_level, player_exp, player_coins, quests_completed = self.db.get_player_level(self.player_name)
        print(f"\nPlayer: {self.player_name} (Level {player_level}, EXP {player_exp}, Coins {player_coins}, Quests Completed {quests_completed})")
        
        stats = self.db.get_player_stats(self.player_name)
        current_life_skill = None
        
        print("\nPlayer Stats:")
        for stat in stats:
            life_skill_name, life_skill_level, life_skill_exp, child_skill_name, child_skill_level, child_skill_exp = stat
            
            if life_skill_name != current_life_skill:
                print(f"\n{life_skill_name} (Level {life_skill_level}, EXP {life_skill_exp}):")
                current_life_skill = life_skill_name
            
            print(f"  - {child_skill_name}: Level {child_skill_level}, EXP {child_skill_exp}")