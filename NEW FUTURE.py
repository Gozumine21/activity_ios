# シンプルなドラクエ風テキストRPG
import random
import time
import threading
import os

try:
    import pygame
    _mixer_available = True
except Exception:
    pygame = None
    _mixer_available = False

try:
    import winsound  # Windows用サウンド
except ImportError:  # 念のため他環境でもエラーにならないように
    winsound = None

# BGM用フラグ（winsound用）
_bgm_running = False
_bgm_thread: threading.Thread | None = None

# 使用するBGMファイル名（このスクリプトと同じフォルダに置く）
BGM_FILE = "bgm.mp3"  # .ogg や .wav でもOK


class Color:
    RED = "\033[31m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    MAGENTA = "\033[35m"
    BLUE = "\033[34m"
    WHITE = "\033[37m"
    RESET = "\033[0m"


def play_sound(event: str) -> None:
    """簡単な効果音を鳴らす（Windows限定）。うるさければ中身を空にしてOK。"""
    if winsound is None:
        return

    if event == "attack":  # プレイヤー攻撃
        winsound.Beep(900, 60)
        winsound.Beep(1100, 80)
    elif event == "skill":  # 技・魔法
        winsound.Beep(1200, 80)
        winsound.Beep(1500, 120)
    elif event == "hit":  # ダメージ
        winsound.Beep(600, 80)
    elif event == "breath":  # ドラゴンのブレス
        for f in range(400, 900, 80):
            winsound.Beep(f, 40)
    elif event == "victory":  # 勝利
        for f in (800, 1000, 1200, 1400):
            winsound.Beep(f, 120)
    elif event == "gameover":  # ゲームオーバー
        for f in (600, 500, 400, 300):
            winsound.Beep(f, 200)


def _bgm_worker() -> None:
    """バックグラウンドでシンプルなBGMを流すスレッド"""
    global _bgm_running
    if winsound is None:
        return
    # なんとなく勇者っぽい簡単なフレーズ（チープなビープ音BGM）
    pattern = [
        (659, 200),  # E5
        (784, 200),  # G5
        (880, 200),  # A5
        (784, 200),  # G5
        (659, 200),  # E5
        (523, 200),  # C5
        (587, 200),  # D5
        (659, 400),  # E5
    ]
    while _bgm_running:
        for freq, dur in pattern:
            if not _bgm_running:
                break
            winsound.Beep(freq, dur)
            # 少し間をあけてループ
            time.sleep(0.03)


def start_bgm() -> None:
    """BGMを再生開始（すでに再生中なら何もしない）
    優先順位:
    1. pygame + 外部BGMファイル (bgm.mp3 など)
    2. winsound ビープ音BGM
    """
    global _bgm_running, _bgm_thread

    # 1. pygameで本物のBGMファイルを再生
    if _mixer_available and pygame is not None and os.path.exists(BGM_FILE):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(BGM_FILE)
                pygame.mixer.music.play(-1)  # ループ再生
            return
        except Exception:
            # 失敗したらwinsound方式にフォールバック
            pass

    # 2. winsoundによるビープ音BGM
    if winsound is None or _bgm_running:
        return
    _bgm_running = True
    _bgm_thread = threading.Thread(target=_bgm_worker, daemon=True)
    _bgm_thread.start()


def stop_bgm() -> None:
    """BGMを停止"""
    global _bgm_running

    # pygame BGM を止める
    if _mixer_available and pygame is not None:
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass

    # winsound BGM を止める
    _bgm_running = False


def clear_screen() -> None:
    """画面をざっくりクリア（Windowsコンソール向け）"""
    print("\033[2J\033[H", end="")


def slow_print(text: str, delay: float = 0.02, color: str = Color.RESET) -> None:
    """少しゆっくり表示して雰囲気を出す。delayを0にすれば高速表示。"""
    print(color, end="")
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print(Color.RESET)


def choose_job() -> dict:
    jobs = {
        # HPとMPを大きく上げて遊びやすく
        "1": {"name": "戦士", "hp": 80, "mp": 20, "atk": 8, "def": 5, "skill": "かぶと割り"},
        "2": {"name": "魔法使い", "hp": 50, "mp": 50, "atk": 4, "def": 3, "skill": "メラ"},
    }
    slow_print("職業を選んでください 1) 戦士  2) 魔法使い", color=Color.CYAN)
    while True:
        choice = input("> ").strip()
        if choice in jobs:
            return jobs[choice]
        slow_print("1 か 2 を入力してください。")


def player_turn(player: dict, enemy: dict) -> None:
    slow_print(f"\n{enemy['name']}にどうする？ 1) こうげき  2) とくぎ", color=Color.YELLOW)
    while True:
        action = input("> ").strip()
        if action == "1":
            play_sound("attack")
            damage = max(0, player["atk"] + random.randint(-2, 2) - enemy["def"])
            enemy["hp"] -= damage
            slow_print(f"{player['name']}のこうげき！ {enemy['name']}に{damage}のダメージ！", color=Color.GREEN)
            return
        if action == "2":
            use_skill(player, enemy)
            return
        slow_print("1 か 2 を入力してください。", color=Color.RED)


def use_skill(player: dict, enemy: dict) -> None:
    if player["mp"] <= 0:
        slow_print("MPが足りない！", color=Color.RED)
        return

    # いつでも必殺技を確定発動（MPが足りないときだけ不発）
    if player["mp"] >= 6:
        player["mp"] -= 6
        play_sound("skill")
        if player["job"] == "戦士":
            slow_print("周囲の空気が震えだした……", color=Color.CYAN)
            slow_print(f"{player['name']}は剣を高く掲げた！", color=Color.YELLOW)
            slow_print("ギャラクシーブレード！！！", color=Color.MAGENTA)
            slow_print("――星の軌跡が一直線にほとばしる！", color=Color.WHITE)
            damage = max(0, player["atk"] + 10 + random.randint(0, 4) - enemy["def"])
        else:  # 魔法使い
            slow_print("足元に魔法陣が浮かび上がる！", color=Color.BLUE)
            slow_print(f"{player['name']}は天空に杖を突き上げた！", color=Color.MAGENTA)
            slow_print("スターダスト・メテオ！！！", color=Color.YELLOW)
            slow_print("――無数の光の隕石が降りそそぐ！", color=Color.WHITE)
            damage = max(0, 12 + random.randint(-2, 6) - enemy["def"])
        enemy["hp"] -= damage
        slow_print(f"{enemy['name']}に{damage}の大ダメージ！", color=Color.GREEN)
        return

    # MPが6未満のときだけ通常特技
    player["mp"] -= 3
    play_sound("skill")
    if player["job"] == "戦士":
        damage = max(0, player["atk"] + 4 + random.randint(-1, 1) - enemy["def"])
        slow_print(f"{player['name']}の{player['skill']}！ {enemy['name']}に{damage}のダメージ！", color=Color.MAGENTA)
    else:
        damage = max(0, 8 + random.randint(-3, 3) - enemy["def"])
        slow_print(f"{player['name']}は{player['skill']}を唱えた！ {enemy['name']}に{damage}のダメージ！", color=Color.MAGENTA)
    enemy["hp"] -= damage


def enemy_turn(player: dict, enemy: dict) -> None:
    # ドラゴン専用の技：ほのおのブレス
    if enemy["name"] == "ドラゴン" and random.random() < 0.4:
        damage = max(0, enemy["atk"] + 6 + random.randint(-2, 4) - player["def"])
        player["hp"] -= damage
        play_sound("breath")
        slow_print("ドラゴンは大きく息を吸い込んだ…！", color=Color.YELLOW)
        slow_print("ごうごうと　ほのおのブレスをはいた！", color=Color.RED)
        slow_print(f"{player['name']}は{damage}のダメージを受けた！", color=Color.RED)
        return

    damage = max(0, enemy["atk"] + random.randint(-2, 2) - player["def"])
    player["hp"] -= damage
    play_sound("hit")
    slow_print(f"{enemy['name']}のこうげき！ {player['name']}は{damage}のダメージを受けた！", color=Color.RED)


def show_dragon_art() -> None:
    """ドラゴンのカラーASCIIアートを、よりリアル＆派手に表示"""
    clear_screen()
    art = [
        # 夜空と月
        (Color.BLUE,   "   ✦✦✦✦✦✦✦✦✦✦✦✦  夜空  ✦✦✦✦✦✦✦✦✦✦✦✦"),
        (Color.BLUE,   "        ✦        ✦       ✦       ✦        ✦    "),
        (Color.CYAN,   "              .-\"\"\"\"-.        ○ 満月        "),
        (Color.CYAN,   "             /  .-.   \\                         "),
        # 山と火山
        (Color.MAGENTA,"    火山    /  /   \\   \\     闇山              "),
        (Color.MAGENTA,"          _/__/_____\\___\\_______   __          "),
        (Color.RED,    "       __/   真っ赤な溶岩      /__/  \\__       "),
        # ドラゴンの頭
        (Color.GREEN,  "              /\\           ／⌒⌒⌒⌒⌒＼        "),
        (Color.GREEN,  "      角    /  \\__      ／  竜王ドラゴン ＼   "),
        (Color.GREEN,  "           /  /\\  \\__  /   (｀・ω・´)    |   "),
        (Color.GREEN,  "          /  /  \\    \\/\\                 /   "),
        # 体と翼
        (Color.YELLOW, "         /__/____\\____/  \\  炎の翼     /    "),
        (Color.YELLOW, "        /   /    /   / /\\ \\___________/     "),
        (Color.YELLOW, "   尾  /   /    /   / /  \\  鱗         \\     "),
        (Color.YELLOW, "      /___/____/___/ /____\\_____________\\    "),
        # ブレス
        (Color.RED,    "                ((  ゴオオオオオオ…  ))      "),
        (Color.RED,    "                 \\\\  炎  炎  炎  炎  //       "),
        (Color.RED,    "                  \\\\＿＿＿＿＿＿＿＿＿//       "),
        (Color.RED,    "                    ⌒⌒⌒⌒⌒⌒⌒⌒⌒⌒         "),
    ]
    for color, line in art:
        slow_print(line, delay=0.0, color=color)


def show_player_art(player: dict) -> None:
    """プレイヤーキャラのカラーASCIIアートを表示"""
    job = player.get("job", "勇者")
    clear_screen()
    title = f"{player['name']}（{job}）"
    slow_print(f"=== {title} ===", delay=0.0, color=Color.CYAN)

    if job == "戦士":
        art = [
            (Color.CYAN,   "　　　　  空                                      "),
            (Color.CYAN,   "　　　☁　　　　　☁　　　　　　☁　　　　　　"),
            (Color.GREEN,  "　草原________________________________________________"),
            (Color.YELLOW, "                 /\\          盾"),
            (Color.YELLOW, "   剣           /  \\      ____"),
            (Color.YELLOW, "  ／|          / /\\ \\    |__|"),
            (Color.WHITE,  " (   )        /_/__\\_\\   (・ω・ )"),
            (Color.GREEN,  "  | |        __/|  |\\__  /|  |\\"),
            (Color.GREEN,  " /___\\      /   |__|   \\/_|__|_\\"),
            (Color.BLUE,   "  ブーツ       /      く     く "),
        ]
    else:  # 魔法使い
        art = [
            (Color.CYAN,    "　　　　  夜空　　　　　　　　　　　☆　　　　"),
            (Color.CYAN,    "　　　✦　　　✦　　　　✦　　　　　✦　　　　"),
            (Color.MAGENTA, "             /\\      とんがり帽子      "),
            (Color.MAGENTA, "   杖       /  \\"),
            (Color.MAGENTA, "  ／|      /_/\\_\\"),
            (Color.WHITE,   " (   )      (・ω・ )"),
            (Color.BLUE,    "  | |      __/|  |\\__"),
            (Color.BLUE,    " /___\\    /   |__|   \\"),
            (Color.MAGENTA, "  ローブ      ︶    ︶ "),
            (Color.YELLOW,  "   魔力の光   ☆  ✦  ☆  ✦  ☆"),
        ]

    for color, line in art:
        slow_print(line, delay=0.0, color=color)


def show_field_background() -> None:
    """最初の草原マップを色付きで表示"""
    clear_screen()
    art = [
        (Color.CYAN,   "＝＝＝＝＝＝＝＝＝＝  竜の城へつづく草原  ＝＝＝＝＝＝＝＝＝＝"),
        (Color.CYAN,   "                ☁        ☁                    ☁"),
        (Color.GREEN,  "      山        /\\             森           /\\"),
        (Color.GREEN,  "             /\\/_\\    /\\     /\\/\\        /\\/_\\"),
        (Color.GREEN,  "   村       /_/  \\___/_/\\___/__/  \\__   /_/  \\__"),
        (Color.YELLOW, "          小さな村        砂利道             城への道"),
        (Color.BLUE,   "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"),
    ]
    for color, line in art:
        slow_print(line, delay=0.0, color=color)


def battle(player: dict, enemy: dict) -> bool:
    # プレイヤーと敵の登場シーン
    show_player_art(player)
    color = Color.CYAN if enemy["name"] != "ドラゴン" else Color.MAGENTA
    slow_print(f"\n{enemy['name']}があらわれた！", color=color)
    while player["hp"] > 0 and enemy["hp"] > 0:
        slow_print(
            f"\n{player['name']} HP:{player['hp']} MP:{player['mp']} | {enemy['name']} HP:{enemy['hp']}",
            color=Color.CYAN,
        )
        player_turn(player, enemy)
        if enemy["hp"] <= 0:
            slow_print(f"{enemy['name']}をたおした！", color=Color.GREEN)
            play_sound("victory")
            return True
        enemy_turn(player, enemy)
    slow_print(f"{player['name']}は力尽きた...", color=Color.RED)
    slow_print("GAME OVER", color=Color.RED)
    play_sound("gameover")
    return False


def main() -> None:
    # ゲーム全体でBGMを再生
    start_bgm()
    try:
        show_field_background()
        slow_print("=== ちいさな冒険のはじまり ===", delay=0.01, color=Color.CYAN)
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

        slime = {"name": "スライム", "hp": 18, "atk": 6, "def": 2}
        if battle(player, slime):
            # スライムを倒したらドラゴン戦
            slow_print("\n遠くで大きな咆哮が聞こえる……", color=Color.MAGENTA)
            dragon = {"name": "ドラゴン", "hp": 40, "atk": 10, "def": 5}
            show_dragon_art()
            battle(player, dragon)
    finally:
        # 終了時にBGMを停止
        stop_bgm()


if __name__ == "__main__":
    main()
