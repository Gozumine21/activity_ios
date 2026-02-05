# シンプルなドラクエ風テキストRPG
import random
import time


def slow_print(text: str, delay: float = 0.02) -> None:
    """少しゆっくり表示して雰囲気を出す。delayを0にすれば高速表示。"""
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()


def choose_job() -> dict:
    jobs = {
        "1": {"name": "戦士", "hp": 30, "mp": 5, "atk": 8, "def": 5, "skill": "かぶと割り"},
        "2": {"name": "魔法使い", "hp": 20, "mp": 20, "atk": 4, "def": 3, "skill": "メラ"},
    }
    slow_print("職業を選んでください 1) 戦士  2) 魔法使い")
    while True:
        choice = input("> ").strip()
        if choice in jobs:
            return jobs[choice]
        slow_print("1 か 2 を入力してください。")


def player_turn(player: dict, enemy: dict) -> None:
    slow_print(f"\n{enemy['name']}にどうする？ 1) こうげき  2) とくぎ")
    while True:
        action = input("> ").strip()
        if action == "1":
            damage = max(0, player["atk"] + random.randint(-2, 2) - enemy["def"])
            enemy["hp"] -= damage
            slow_print(f"{player['name']}のこうげき！ {enemy['name']}に{damage}のダメージ！")
            return
        if action == "2":
            use_skill(player, enemy)
            return
        slow_print("1 か 2 を入力してください。")


def use_skill(player: dict, enemy: dict) -> None:
    if player["mp"] <= 0:
        slow_print("MPが足りない！")
        return
    player["mp"] -= 3
    if player["job"] == "戦士":
        damage = max(0, player["atk"] + 4 + random.randint(-1, 1) - enemy["def"])
        slow_print(f"{player['name']}の{player['skill']}！ {enemy['name']}に{damage}のダメージ！")
    else:
        damage = max(0, 8 + random.randint(-3, 3) - enemy["def"])
        slow_print(f"{player['name']}は{player['skill']}を唱えた！ {enemy['name']}に{damage}のダメージ！")
    enemy["hp"] -= damage


def enemy_turn(player: dict, enemy: dict) -> None:
    damage = max(0, enemy["atk"] + random.randint(-2, 2) - player["def"])
    player["hp"] -= damage
    slow_print(f"{enemy['name']}のこうげき！ {player['name']}は{damage}のダメージを受けた！")


def battle(player: dict, enemy: dict) -> bool:
    slow_print(f"\n{enemy['name']}があらわれた！")
    if "art" in enemy:
        print(enemy["art"])
    while player["hp"] > 0 and enemy["hp"] > 0:
        slow_print(f"\n{player['name']} HP:{player['hp']} MP:{player['mp']} | {enemy['name']} HP:{enemy['hp']}")
        player_turn(player, enemy)
        if enemy["hp"] <= 0:
            slow_print(f"{enemy['name']}をたおした！")
            return True
        enemy_turn(player, enemy)
    slow_print(f"{player['name']}は力尽きた...")
    slow_print("GAME OVER")
    return False


def main() -> None:
    slow_print("=== ちいさな冒険のはじまり ===", delay=0.01)
    name = input("あなたの名前を教えてください: ").strip() or "ゆうしゃ"
    job = choose_job()

    player = {
        "name": name,
        "job": job["name"],
        "hp": job["hp"],
        "mp": job["mp"],
        "atk": job["atk"],
        "def": job["def"],
        "skill": job["skill"],
    }

    slime = {
        "name": "スライム",
        "hp": 18,
        "atk": 6,
        "def": 2,
        "art": r"""
        ／￣￣＼
       ｜  ● ● ｜   ぷるぷる…
       ｜   ω  ｜ 
        ＼＿W＿／
        """,
    }
    battle(player, slime)


if __name__ == "__main__":
    main()
