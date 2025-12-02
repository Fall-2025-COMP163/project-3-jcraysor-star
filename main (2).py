
"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code

Name: Jared C Raysor

AI Usage: Used AI to help design and implement combat_system functions,
including enemy creation, SimpleBattle methods, abilities, and utilities.
"""

import random

from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Create an enemy based on type
    """
    enemy_type = enemy_type.lower()
    if enemy_type == "goblin":
        health = 50
        strength = 8
        magic = 2
        xp = 25
        gold = 10
        name = "Goblin"
    elif enemy_type == "orc":
        health = 80
        strength = 12
        magic = 5
        xp = 50
        gold = 25
        name = "Orc"
    elif enemy_type == "dragon":
        health = 200
        strength = 25
        magic = 15
        xp = 200
        gold = 100
        name = "Dragon"
    else:
        raise InvalidTargetError(f"Unknown enemy type: {enemy_type}")

    return {
        "name": name,
        "type": enemy_type,
        "health": health,
        "max_health": health,
        "strength": strength,
        "magic": magic,
        "xp_reward": xp,
        "gold_reward": gold,
    }


def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level
    """
    if character_level <= 2:
        enemy_type = "goblin"
    elif character_level <= 5:
        enemy_type = "orc"
    else:
        enemy_type = "dragon"
    return create_enemy(enemy_type)

# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    Simple turn-based combat system
    """

    def __init__(self, character, enemy):
        """Initialize battle with character and enemy"""
        self.character = character
        self.enemy = enemy
        self.combat_active = True
        self.turn_count = 0

    def start_battle(self):
        """
        Start the combat loop
        """
        if self.character.get("health", 0) <= 0:
            raise CharacterDeadError("Character is already dead")

        while self.combat_active:
            display_combat_stats(self.character, self.enemy)

            # Player turn
            self.player_turn()
            winner = self.check_battle_end()
            if winner is not None:
                break

            # Enemy turn
            self.enemy_turn()
            winner = self.check_battle_end()
            if winner is not None:
                break

            self.turn_count += 1

        if self.character["health"] <= 0:
            return {"winner": "enemy", "xp_gained": 0, "gold_gained": 0}
        else:
            rewards = get_victory_rewards(self.enemy)
            self.character["experience"] = self.character.get("experience", 0) + rewards["xp"]
            self.character["gold"] = self.character.get("gold", 0) + rewards["gold"]
            return {"winner": "player", "xp_gained": rewards["xp"], "gold_gained": rewards["gold"]}

    def player_turn(self):
        """
        Handle player's turn
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active")

        display_battle_log("Your turn!")
        print("1. Basic Attack")
        print("2. Special Ability")
        print("3. Try to Run")

        choice = input("Choose an action (1-3): ").strip()

        if choice == "1":
            dmg = self.calculate_damage(self.character, self.enemy)
            self.apply_damage(self.enemy, dmg)
            display_battle_log(f"You hit the {self.enemy['name']} for {dmg} damage!")
        elif choice == "2":
            try:
                desc = use_special_ability(self.character, self.enemy)
                display_battle_log(desc)
            except AbilityOnCooldownError as e:
                display_battle_log(str(e))
        elif choice == "3":
            if self.attempt_escape():
                display_battle_log("You successfully escaped!")
                self.combat_active = False
            else:
                display_battle_log("You failed to escape!")
        else:
            display_battle_log("Invalid choice, you hesitate and lose your turn.")

    def enemy_turn(self):
        """
        Handle enemy's turn - simple AI
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active")

        if self.enemy["health"] <= 0:
            return

        display_battle_log(f"{self.enemy['name']}'s turn!")
        dmg = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, dmg)
        display_battle_log(f"{self.enemy['name']} hits you for {dmg} damage!")

    def calculate_damage(self, attacker, defender):
        """
        Calculate damage from attack
        """
        atk = attacker.get("strength", 0)
        def_str = defender.get("strength", 0)
        dmg = atk - (def_str // 4)
        if dmg < 1:
            dmg = 1
        return dmg

    def apply_damage(self, target, damage):
        """
        Apply damage to a character or enemy
        """
        current = target.get("health", 0)
        current -= damage
        if current < 0:
            current = 0
        target["health"] = current

    def check_battle_end(self):
        """
        Check if battle is over
        """
        if self.enemy["health"] <= 0:
            self.combat_active = False
            return "player"
        if self.character["health"] <= 0:
            self.combat_active = False
            return "enemy"
        return None

    def attempt_escape(self):
        """
        Try to escape from battle
        """
        roll = random.randint(1, 100)
        if roll <= 50:
            self.combat_active = False
            return True
        return False

# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    """
    Use character's class-specific special ability
    """
    if character.get("ability_on_cooldown", False):
        raise AbilityOnCooldownError("Ability is on cooldown")

    char_class = character.get("class", "").lower()
    if char_class == "warrior":
        msg = warrior_power_strike(character, enemy)
    elif char_class == "mage":
        msg = mage_fireball(character, enemy)
    elif char_class == "rogue":
        msg = rogue_critical_strike(character, enemy)
    elif char_class == "cleric":
        msg = cleric_heal(character)
    else:
        msg = "Nothing happens."

    character["ability_on_cooldown"] = True
    return msg


def warrior_power_strike(character, enemy):
    """Warrior special ability"""
    base = character.get("strength", 0)
    dmg = base * 2
    enemy["health"] = max(0, enemy["health"] - dmg)
    return f"Warrior Power Strike deals {dmg} damage to {enemy['name']}!"


def mage_fireball(character, enemy):
    """Mage special ability"""
    base = character.get("magic", 0)
    dmg = base * 2
    enemy["health"] = max(0, enemy["health"] - dmg)
    return f"Mage casts Fireball for {dmg} damage to {enemy['name']}!"


def rogue_critical_strike(character, enemy):
    """Rogue special ability"""
    base = character.get("strength", 0)
    if random.randint(1, 100) <= 50:
        dmg = base * 3
        enemy["health"] = max(0, enemy["health"] - dmg)
        return f"Critical Strike succeeds for {dmg} damage!"
    else:
        dmg = base
        enemy["health"] = max(0, enemy["health"] - dmg)
        return f"Critical Strike fails; normal hit for {dmg} damage."


def cleric_heal(character):
    """Cleric special ability"""
    heal_amount = 30
    max_hp = character.get("max_health", 0)
    current = character.get("health", 0)
    current += heal_amount
    if current > max_hp:
        current = max_hp
    character["health"] = current
    return f"Cleric heals for {heal_amount} HP!"

# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    """
    Check if character is in condition to fight
    """
    return character.get("health", 0) > 0 and not character.get("in_battle", False)


def get_victory_rewards(enemy):
    """
    Calculate rewards for defeating enemy
    """
    return {
        "xp": enemy.get("xp_reward", 0),
        "gold": enemy.get("gold_reward", 0),
    }


def display_combat_stats(character, enemy):
    """
    Display current combat status
    """
    print(f"\n{character['name']}: HP={character['health']}/{character['max_health']}")
    print(f"{enemy['name']}: HP={enemy['health']}/{enemy['max_health']}")


def display_battle_log(message):
    """
    Display a formatted battle message
    """
    print(f">>> {message}")


if __name__ == "__main__":
    print("=== COMBAT SYSTEM TEST ===")
