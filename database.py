import sqlite3
import datetime

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        # Players table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'live',
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                coins INTEGER DEFAULT 0,
                quests_completed INTEGER DEFAULT 0
            )
        ''')
        
        # Check if columns exist in players table
        self.cursor.execute("PRAGMA table_info(players)")
        columns = [col[1] for col in self.cursor.fetchall()]
        if 'level' not in columns:
            self.cursor.execute('ALTER TABLE players ADD COLUMN level INTEGER DEFAULT 1')
        if 'exp' not in columns:
            self.cursor.execute('ALTER TABLE players ADD COLUMN exp INTEGER DEFAULT 0')
        if 'coins' not in columns:
            self.cursor.execute('ALTER TABLE players ADD COLUMN coins INTEGER DEFAULT 0')
        if 'quests_completed' not in columns:
            self.cursor.execute('ALTER TABLE players ADD COLUMN quests_completed INTEGER DEFAULT 0')
        
        # Life Skills table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS life_skills (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0
            )
        ''')
        
        # Child Skills table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS child_skills (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                life_skill_id INTEGER,
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                FOREIGN KEY (life_skill_id) REFERENCES life_skills(id)
            )
        ''')
        
        # Player Stats table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_stats (
                player_name TEXT,
                life_skill_id INTEGER,
                child_skill_id INTEGER,
                FOREIGN KEY (life_skill_id) REFERENCES life_skills(id),
                FOREIGN KEY (child_skill_id) REFERENCES child_skills(id),
                FOREIGN KEY (player_name) REFERENCES players(name),
                UNIQUE(player_name, child_skill_id)
            )
        ''')
        
        # Daily Quests table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_quests (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                child_skill_id INTEGER,
                exp_reward INTEGER,
                coin_reward INTEGER,
                FOREIGN KEY (child_skill_id) REFERENCES child_skills(id)
            )
        ''')
        
        # Routine Quests table (Weekly/Monthly)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS routine_quests (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                child_skill_id INTEGER,
                exp_reward INTEGER,
                coin_reward INTEGER,
                reset_period TEXT CHECK (reset_period IN ('weekly', 'monthly')),
                FOREIGN KEY (child_skill_id) REFERENCES child_skills(id)
            )
        ''')
        
        # Special Quests table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS special_quests (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                child_skill_id INTEGER,
                exp_reward INTEGER,
                coin_reward INTEGER,
                FOREIGN KEY (child_skill_id) REFERENCES child_skills(id)
            )
        ''')
        
        # Progression Quests table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS progression_quests (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                child_skill_id INTEGER,
                exp_reward INTEGER,
                coin_reward INTEGER,
                FOREIGN KEY (child_skill_id) REFERENCES child_skills(id)
            )
        ''')
        
        # Challenge Quests table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS challenge_quests (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                child_skill_id INTEGER,
                exp_reward INTEGER,
                coin_reward INTEGER,
                time_limit TEXT,
                streak_required INTEGER DEFAULT 0,
                FOREIGN KEY (child_skill_id) REFERENCES child_skills(id)
            )
        ''')
        
        # RNG Quests table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rng_quests (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                child_skill_id INTEGER,
                exp_reward INTEGER,
                coin_reward INTEGER,
                FOREIGN KEY (child_skill_id) REFERENCES child_skills(id)
            )
        ''')
        
        # Player Quests table to track completion
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_quests (
                player_name TEXT,
                quest_id INTEGER,
                quest_type TEXT CHECK (quest_type IN ('daily', 'routine', 'special', 'progression', 'challenge', 'rng')),
                completed BOOLEAN DEFAULT 0,
                completion_date TEXT,
                streak_count INTEGER DEFAULT 0,
                FOREIGN KEY (player_name) REFERENCES players(name)
            )
        ''')
        self.conn.commit()
    
    def initialize_quests(self):
        # Sample Daily Quests
        daily_quests = [
            (1, 'Train Stamina', 'Complete a 20-minute run.', 1, 50, 0),
            (2, 'Read a Chapter', 'Read one chapter of a book.', 4, 75, 0),
            (3, 'Practice Discipline', 'Meditate for 10 minutes.', 8, 100, 0)
        ]
        
        # Sample Routine Quests (Weekly/Monthly)
        routine_quests = [
            (1, 'Weekly Workout', 'Complete 3 workouts this week.', 11, 150, 10, 'weekly'),
            (2, 'Monthly Study', 'Finish a course module.', 4, 200, 20, 'monthly')
        ]
        
        # Sample Special Quests
        special_quests = [
            (1, 'First Milestone', 'Reach Level 2 in any child skill.', 1, 100, 50),
            (2, 'Master Focus', 'Complete 5 Focus-related tasks.', 5, 200, 100)
        ]
        
        # Sample Progression Quests
        progression_quests = [
            (1, 'Grind Stamina', 'Run for 15 minutes.', 1, 40, 0),
            (2, 'Study Session', 'Study for 30 minutes.', 4, 60, 0)
        ]
        
        # Sample Challenge Quests
        challenge_quests = [
            (1, 'Stamina Streak', 'Run daily for 3 days.', 1, 100, 30, '2025-12-31T23:59:59', 3),
            (2, 'Focus Challenge', 'Study without distractions for 1 hour.', 5, 120, 40, '2025-12-31T23:59:59', 0)
        ]
        
        # Sample RNG Quests
        rng_quests = [
            (1, 'Random Skill Boost', 'Practice a random skill.', 8, 80, 20),
            (2, 'Mystery Task', 'Complete a surprise task.', 10, 90, 25)
        ]
        
        self.cursor.executemany('INSERT OR IGNORE INTO daily_quests (id, name, description, child_skill_id, exp_reward, coin_reward) VALUES (?, ?, ?, ?, ?, ?)', daily_quests)
        self.cursor.executemany('INSERT OR IGNORE INTO routine_quests (id, name, description, child_skill_id, exp_reward, coin_reward, reset_period) VALUES (?, ?, ?, ?, ?, ?, ?)', routine_quests)
        self.cursor.executemany('INSERT OR IGNORE INTO special_quests (id, name, description, child_skill_id, exp_reward, coin_reward) VALUES (?, ?, ?, ?, ?, ?)', special_quests)
        self.cursor.executemany('INSERT OR IGNORE INTO progression_quests (id, name, description, child_skill_id, exp_reward, coin_reward) VALUES (?, ?, ?, ?, ?, ?)', progression_quests)
        self.cursor.executemany('INSERT OR IGNORE INTO challenge_quests (id, name, description, child_skill_id, exp_reward, coin_reward, time_limit, streak_required) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', challenge_quests)
        self.cursor.executemany('INSERT OR IGNORE INTO rng_quests (id, name, description, child_skill_id, exp_reward, coin_reward) VALUES (?, ?, ?, ?, ?, ?)', rng_quests)
        self.conn.commit()
    
    def create_player(self, name):
        self.cursor.execute('INSERT INTO players (name, status, level, exp, coins, quests_completed) VALUES (?, ?, ?, ?, ?, ?)', 
                          (name, 'live', 1, 0, 0, 0))
        self.conn.commit()
    
    def get_player(self):
        self.cursor.execute('SELECT * FROM players LIMIT 1')
        return self.cursor.fetchone()
    
    def initialize_player_stats(self, player_name):
        # Define Life Skills and Child Skills
        life_skills = [
            (1, 'Agility'),
            (2, 'Intellect'),
            (3, 'Soul'),
            (4, 'Strength')
        ]
        
        child_skills = [
            (1, 'Stamina', 1),
            (2, 'Mobility', 1),
            (3, 'Balance', 1),
            (4, 'Reading', 2),
            (5, 'Focus', 2),
            (6, 'Language Learning', 2),
            (7, 'Critical Thinking', 2),
            (8, 'Discipline', 3),
            (9, 'Practice', 3),
            (10, 'Reflection', 3),
            (11, 'Weight Training', 4),
            (12, 'Core', 4),
            (13, 'Endurance', 4)
        ]
        
        # Insert Life Skills
        self.cursor.executemany('INSERT OR IGNORE INTO life_skills (id, name, level, exp) VALUES (?, ?, 1, 0)', life_skills)
        
        # Insert Child Skills
        self.cursor.executemany('INSERT OR IGNORE INTO child_skills (id, name, life_skill_id, level, exp) VALUES (?, ?, ?, 1, 0)', child_skills)
        
        # Clear existing player_stats entries to avoid duplicates
        self.cursor.execute('DELETE FROM player_stats WHERE player_name = ?', (player_name,))
        
        # Initialize Player Stats
        for cs in child_skills:
            self.cursor.execute('''
                INSERT OR IGNORE INTO player_stats (player_name, life_skill_id, child_skill_id)
                VALUES (?, ?, ?)
            ''', (player_name, cs[2], cs[0]))
        
        # Initialize quests
        self.initialize_quests()
        self.conn.commit()
    
    def assign_daily_quests(self, player_name):
        current_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        self.cursor.execute('''
            SELECT COUNT(*) FROM player_quests
            WHERE player_name = ? AND quest_type = 'daily'
            AND completion_date >= ?
        ''', (player_name, current_date))
        daily_quest_count = self.cursor.fetchone()[0]
        
        if daily_quest_count == 0:
            self.cursor.execute('SELECT id, child_skill_id, exp_reward, coin_reward FROM daily_quests')
            daily_quests = self.cursor.fetchall()
            for quest in daily_quests:
                quest_id, child_skill_id, exp_reward, coin_reward = quest
                self.cursor.execute('''
                    INSERT OR REPLACE INTO player_quests (player_name, quest_id, quest_type, completed, completion_date, streak_count)
                    VALUES (?, ?, 'daily', 0, ?, 0)
                ''', (player_name, quest_id, current_date))
            self.conn.commit()
    
    def reset_daily_quests(self, player_name):
        current_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        # Mark uncompleted daily quests from yesterday as failed
        self.cursor.execute('''
            UPDATE player_quests
            SET completed = 0
            WHERE player_name = ? AND quest_type = 'daily'
            AND completion_date < ? AND completed = 0
        ''', (player_name, current_date))
        
        # Remove old daily quest assignments
        self.cursor.execute('''
            DELETE FROM player_quests
            WHERE player_name = ? AND quest_type = 'daily'
            AND completion_date < ?
        ''', (player_name, current_date))
        
        # Assign new daily quests
        self.assign_daily_quests(player_name)
        self.conn.commit()
    
    def get_player_stats(self, player_name):
        self.cursor.execute('''
            SELECT ls.name, ls.level, ls.exp, cs.name, cs.level, cs.exp
            FROM player_stats ps
            JOIN life_skills ls ON ps.life_skill_id = ls.id
            JOIN child_skills cs ON ps.child_skill_id = cs.id
            WHERE ps.player_name = ?
            ORDER BY ls.id, cs.id
        ''', (player_name,))
        return self.cursor.fetchall()
    
    def get_player_level(self, player_name):
        self.cursor.execute('SELECT level, exp, coins, quests_completed FROM players WHERE name = ?', (player_name,))
        return self.cursor.fetchone()
    
    def get_available_quests(self, player_name):
        current_time = datetime.datetime.now().isoformat()
        quests = []
        
        # Daily Quests (assigned automatically, shown if not completed today)
        self.cursor.execute('''
            SELECT dq.id, dq.name, dq.description, dq.child_skill_id, dq.exp_reward, dq.coin_reward
            FROM daily_quests dq
            JOIN player_quests pq ON dq.id = pq.quest_id
            WHERE pq.player_name = ? AND pq.quest_type = 'daily'
            AND pq.completed = 0 AND pq.completion_date >= ?
        ''', (player_name, datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()))
        quests.extend([(row[0], row[1], row[2], row[3], row[4], row[5], 'daily') for row in self.cursor.fetchall()])
        
        # Routine Quests (reset weekly/monthly)
        self.cursor.execute('''
            SELECT id, name, description, child_skill_id, exp_reward, coin_reward, reset_period
            FROM routine_quests
            WHERE id NOT IN (
                SELECT quest_id FROM player_quests
                WHERE player_name = ? AND quest_type = 'routine'
                AND (
                    (reset_period = 'weekly' AND completion_date >= ?)
                    OR (reset_period = 'monthly' AND completion_date >= ?)
                )
            )
        ''', (player_name, 
              (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())).replace(hour=0, minute=0, second=0, microsecond=0).isoformat(),
              datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()))
        quests.extend([(row[0], row[1], row[2], row[3], row[4], row[5], 'routine', row[6]) for row in self.cursor.fetchall()])
        
        # Special Quests (one-time, check if not completed)
        self.cursor.execute('''
            SELECT id, name, description, child_skill_id, exp_reward, coin_reward
            FROM special_quests
            WHERE id NOT IN (
                SELECT quest_id FROM player_quests
                WHERE player_name = ? AND quest_type = 'special' AND completed = 1
            )
        ''', (player_name,))
        quests.extend([(row[0], row[1], row[2], row[3], row[4], row[5], 'special') for row in self.cursor.fetchall()])
        
        # Progression Quests (always available)
        self.cursor.execute('SELECT id, name, description, child_skill_id, exp_reward, coin_reward FROM progression_quests')
        quests.extend([(row[0], row[1], row[2], row[3], row[4], row[5], 'progression') for row in self.cursor.fetchall()])
        
        # Challenge Quests (check time limit and streak)
        self.cursor.execute('''
            SELECT id, name, description, child_skill_id, exp_reward, coin_reward, time_limit, streak_required
            FROM challenge_quests
            WHERE time_limit > ? AND id NOT IN (
                SELECT quest_id FROM player_quests
                WHERE player_name = ? AND quest_type = 'challenge' AND completed = 1
            )
        ''', (current_time, player_name))
        quests.extend([(row[0], row[1], row[2], row[3], row[4], row[5], 'challenge', row[6], row[7]) for row in self.cursor.fetchall()])
        
        # RNG Quests (simplified as one-time for now)
        self.cursor.execute('''
            SELECT id, name, description, child_skill_id, exp_reward, coin_reward
            FROM rng_quests
            WHERE id NOT IN (
                SELECT quest_id FROM player_quests
                WHERE player_name = ? AND quest_type = 'rng' AND completed = 1
            )
        ''', (player_name,))
        quests.extend([(row[0], row[1], row[2], row[3], row[4], row[5], 'rng') for row in self.cursor.fetchall()])
        
        return quests
    
    def complete_quest(self, player_name, quest_id, quest_type, child_skill_id, exp_reward, coin_reward):
        self.update_skill_exp(player_name, child_skill_id, exp_reward, coin_reward)
        self.cursor.execute('''
            INSERT OR REPLACE INTO player_quests (player_name, quest_id, quest_type, completed, completion_date, streak_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (player_name, quest_id, quest_type, 1, datetime.datetime.now().isoformat(), 1))
        self.cursor.execute('''
            UPDATE players
            SET quests_completed = quests_completed + 1
            WHERE name = ?
        ''', (player_name,))
        self.conn.commit()
    
    def update_skill_exp(self, player_name, child_skill_id, exp_gained, quest_coins):
        # Update child skill EXP and level
        self.cursor.execute('SELECT exp, level FROM child_skills WHERE id = ?', (child_skill_id,))
        current_exp, current_level = self.cursor.fetchone()
        new_exp = current_exp + exp_gained
        new_level = self.calculate_child_skill_level(new_exp)
        child_level_diff = new_level - current_level
        
        self.cursor.execute('''
            UPDATE child_skills
            SET exp = ?, level = ?
            WHERE id = ?
        ''', (new_exp, new_level, child_skill_id))
        
        # Update life skill EXP and level
        self.cursor.execute('''
            SELECT SUM(exp), SUM(level)
            FROM child_skills
            WHERE life_skill_id = (SELECT life_skill_id FROM child_skills WHERE id = ?)
        ''', (child_skill_id,))
        life_skill_exp, life_skill_level = self.cursor.fetchone()
        
        self.cursor.execute('''
            UPDATE life_skills
            SET exp = ?, level = ?
            WHERE id = (SELECT life_skill_id FROM child_skills WHERE id = ?)
        ''', (life_skill_exp, self.calculate_life_skill_level(life_skill_exp), child_skill_id))
        
        # Update player EXP, level, and coins
        self.cursor.execute('SELECT SUM(exp) FROM life_skills')
        total_exp = self.cursor.fetchone()[0]
        player_level = self.calculate_player_level(total_exp)
        
        self.cursor.execute('SELECT level, coins FROM players WHERE name = ?', (player_name,))
        current_player_level, current_coins = self.cursor.fetchone()
        player_level_diff = player_level - current_player_level
        
        # Calculate life skill level difference
        prev_life_skill_exp = life_skill_exp - exp_gained
        life_skill_level_diff = self.calculate_life_skill_level(life_skill_exp) - self.calculate_life_skill_level(prev_life_skill_exp)
        
        # Calculate total coins from level-ups and quest
        total_coins = current_coins + (child_level_diff * 20) + (life_skill_level_diff * 50) + (player_level_diff * 100) + quest_coins
        
        self.cursor.execute('''
            UPDATE players
            SET exp = ?, level = ?, coins = ?
            WHERE name = ?
        ''', (total_exp, player_level, total_coins, player_name))
        
        self.conn.commit()
        return child_level_diff, life_skill_level_diff, player_level_diff, total_coins
    
    def calculate_player_level(self, total_exp):
        if total_exp < 500:
            return 1
        level = 1
        exp_needed = 500
        current_exp = total_exp
        while current_exp >= exp_needed:
            level += 1
            current_exp -= exp_needed
            exp_needed = 500 + (exp_needed * 0.5)
        return level
    
    def calculate_life_skill_level(self, total_exp):
        if total_exp < 350:
            return 1
        level = 1
        exp_needed = 350
        current_exp = total_exp
        while current_exp >= exp_needed:
            level += 1
            current_exp -= exp_needed
            exp_needed = 350 + (exp_needed * 0.25)
        return level
    
    def calculate_child_skill_level(self, total_exp):
        if total_exp < 100:
            return 1
        level = 1
        exp_needed = 100
        current_exp = total_exp
        while current_exp >= exp_needed:
            level += 1
            current_exp -= exp_needed
            exp_needed = 100 + (exp_needed * 0.5)
        return level
    
    def __del__(self):
        self.conn.close()