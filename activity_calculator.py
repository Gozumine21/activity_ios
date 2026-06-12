"""
睡眠時間・摂取カロリー・運動量から、
1日にあとどれだけ活動（運動）できるかを算出するアプリ
"""

import tkinter as tk
from tkinter import messagebox, ttk


def calc_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """ミフリン・セントジeor式で基礎代謝量（kcal/日）を計算"""
    if sex == "男性":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def sleep_factor(sleep_hours: float) -> tuple[float, str]:
    """睡眠時間から回復度（0〜1）とコメントを返す"""
    if 7.0 <= sleep_hours <= 8.5:
        return 1.0, "睡眠は理想的です。フルパワーで活動できます。"
    if 6.0 <= sleep_hours < 7.0 or 8.5 < sleep_hours <= 9.0:
        return 0.88, "睡眠はやや不足/過多です。無理のない運動量にしましょう。"
    if 5.0 <= sleep_hours < 6.0 or 9.0 < sleep_hours <= 10.0:
        return 0.75, "睡眠不足または過眠気味です。軽めの活動がおすすめです。"
    if sleep_hours < 5.0:
        return 0.55, "睡眠不足です。激しい運動は避け、休息を優先してください。"
    return 0.70, "睡眠がかなり長いです。体がだるい場合は軽い運動に留めましょう。"


def kcal_per_minute(weight_kg: float, intensity: str) -> float:
    """運動強度ごとの消費カロリー（kcal/分）の目安"""
    # MET × 体重(kg) × 0.0175 ≒ kcal/分
    met_values = {"軽い": 3.0, "中程度": 5.0, "激しい": 8.0}
    met = met_values[intensity]
    return met * weight_kg * 0.0175


def exercise_kcal_from_minutes(weight_kg: float, minutes: float, intensity: str) -> float:
    """運動時間（分）と強度から消費カロリーを換算"""
    return minutes * kcal_per_minute(weight_kg, intensity)


def calculate(
    sleep_hours: float,
    intake_kcal: float,
    exercise_kcal: float,
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: str,
) -> dict:
    """1日の活動可能量を算出"""
    bmr = calc_bmr(weight_kg, height_cm, age, sex)

    # 睡眠中・覚醒中の基礎的な消費（睡眠は基礎代謝の約90%）
    sleep_burn = bmr / 24 * sleep_hours * 0.90
    awake_rest_burn = bmr / 24 * (24 - sleep_hours) * 1.05
    base_burn = sleep_burn + awake_rest_burn

    # 食事で得たエネルギー − 基礎消費 − すでにした運動 ＝ 残りエネルギー
    energy_balance = intake_kcal - base_burn - exercise_kcal

    factor, sleep_comment = sleep_factor(sleep_hours)
    remaining_kcal = max(0, energy_balance * factor)

    # 運動強度別の「あと何分できるか」
    minutes_by_intensity = {}
    for intensity in ("軽い", "中程度", "激しい"):
        rate = kcal_per_minute(weight_kg, intensity)
        if rate > 0:
            minutes_by_intensity[intensity] = int(remaining_kcal / rate)
        else:
            minutes_by_intensity[intensity] = 0

    # 1日の推奨運動上限（摂取カロリーの30%程度を目安）
    daily_exercise_cap = intake_kcal * 0.35 * factor
    used_ratio = exercise_kcal / daily_exercise_cap if daily_exercise_cap > 0 else 1.0

    if energy_balance < 0:
        status = "エネルギー不足"
        advice = (
            f"摂取カロリーが基礎代謝＋運動量を下回っています（不足: {abs(int(energy_balance))} kcal）。\n"
            "追加の運動より、栄養補給と休息を優先してください。"
        )
    elif remaining_kcal < 80:
        status = "ほぼ限界"
        advice = "本日の活動量は十分です。激しい運動は控え、ストレッチや散歩程度にしましょう。"
    elif used_ratio >= 0.8:
        status = "運動量 多め"
        advice = "すでに多く運動しています。無理せず、残りは軽い運動がおすすめです。"
    else:
        status = "活動可能"
        advice = (
            f"あと約 {int(remaining_kcal)} kcal 分の運動が可能です。\n"
            f"中程度の運動なら約 {minutes_by_intensity['中程度']} 分が目安です。"
        )

    return {
        "bmr": int(bmr),
        "base_burn": int(base_burn),
        "energy_balance": int(energy_balance),
        "remaining_kcal": int(remaining_kcal),
        "sleep_factor": factor,
        "sleep_comment": sleep_comment,
        "minutes": minutes_by_intensity,
        "status": status,
        "advice": advice,
        "exercise_done": int(exercise_kcal),
        "intake": int(intake_kcal),
    }


class ActivityApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("1日の活動量計算アプリ")
        self.geometry("520x760")
        self.resizable(False, False)
        self.configure(bg="#1a1a2e")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#1a1a2e", foreground="#eaeaea", font=("Meiryo UI", 10))
        style.configure("Title.TLabel", font=("Meiryo UI", 16, "bold"), foreground="#00d4aa")
        style.configure("TButton", font=("Meiryo UI", 11, "bold"))
        style.configure("TCombobox", font=("Meiryo UI", 10))

        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 16, "pady": 6}

        ttk.Label(self, text="活動量・運動量 計算アプリ", style="Title.TLabel").pack(pady=(18, 4))
        ttk.Label(
            self,
            text="睡眠・食事・運動を入力すると、今日あとどれだけ動けるかを算出します",
        ).pack(pady=(0, 12))

        frame = tk.Frame(self, bg="#16213e", padx=20, pady=16)
        frame.pack(fill="x", padx=16)

        self.entries: dict[str, tk.Entry] = {}
        fields = [
            ("睡眠時間（時間）", "sleep", "7.5"),
            ("摂取カロリー（kcal）", "intake", "2000"),
            ("体重（kg）", "weight", "65"),
            ("身長（cm）", "height", "170"),
            ("年齢", "age", "30"),
        ]
        for label, key, default in fields:
            row = tk.Frame(frame, bg="#16213e")
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=label, width=28).pack(side="left")
            entry = tk.Entry(row, width=12, font=("Meiryo UI", 11), justify="center")
            entry.insert(0, default)
            entry.pack(side="right")
            self.entries[key] = entry

        row = tk.Frame(frame, bg="#16213e")
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="運動量の入力方法", width=28).pack(side="left")
        self.exercise_mode = tk.StringVar(value="kcal")
        mode_box = ttk.Combobox(
            row,
            textvariable=self.exercise_mode,
            values=["kcalで入力", "分で入力"],
            width=12,
            state="readonly",
        )
        mode_box.pack(side="right")

        row = tk.Frame(frame, bg="#16213e")
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="運動で消費（kcal）", width=28).pack(side="left")
        exercise_entry = tk.Entry(row, width=12, font=("Meiryo UI", 11), justify="center")
        exercise_entry.insert(0, "300")
        exercise_entry.pack(side="right")
        self.entries["exercise"] = exercise_entry

        row = tk.Frame(frame, bg="#16213e")
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="運動時間（分）", width=28).pack(side="left")
        minutes_entry = tk.Entry(row, width=12, font=("Meiryo UI", 11), justify="center")
        minutes_entry.insert(0, "30")
        minutes_entry.pack(side="right")
        self.entries["exercise_minutes"] = minutes_entry

        row = tk.Frame(frame, bg="#16213e")
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="運動の強さ（分入力時）", width=28).pack(side="left")
        self.exercise_intensity = tk.StringVar(value="中程度")
        ttk.Combobox(
            row,
            textvariable=self.exercise_intensity,
            values=["軽い", "中程度", "激しい"],
            width=10,
            state="readonly",
        ).pack(side="right")

        row = tk.Frame(frame, bg="#16213e")
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="性別", width=28).pack(side="left")
        self.sex_var = tk.StringVar(value="男性")
        ttk.Combobox(row, textvariable=self.sex_var, values=["男性", "女性"], width=10, state="readonly").pack(
            side="right"
        )

        tk.Button(
            self,
            text="計算する",
            font=("Meiryo UI", 12, "bold"),
            bg="#00d4aa",
            fg="#1a1a2e",
            activebackground="#00b894",
            relief="flat",
            padx=20,
            pady=8,
            command=self._on_calculate,
        ).pack(pady=16)

        result_frame = tk.Frame(self, bg="#0f3460", padx=16, pady=12)
        result_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.result_text = tk.Text(
            result_frame,
            height=18,
            font=("Meiryo UI", 10),
            bg="#0f3460",
            fg="#eaeaea",
            relief="flat",
            wrap="word",
        )
        self.result_text.pack(fill="both", expand=True)
        self.result_text.insert("1.0", "上の項目を入力して「計算する」を押してください。")
        self.result_text.configure(state="disabled")

    def _get_float(self, key: str, name: str) -> float | None:
        try:
            value = float(self.entries[key].get().strip())
            if value < 0:
                raise ValueError
            return value
        except ValueError:
            messagebox.showerror("入力エラー", f"{name}に正しい数値を入力してください。")
            return None

    def _on_calculate(self) -> None:
        sleep = self._get_float("sleep", "睡眠時間")
        if sleep is None or sleep > 24:
            if sleep is not None:
                messagebox.showerror("入力エラー", "睡眠時間は0〜24時間で入力してください。")
            return

        intake = self._get_float("intake", "摂取カロリー")
        weight = self._get_float("weight", "体重")
        height = self._get_float("height", "身長")
        if None in (intake, weight, height):
            return

        if self.exercise_mode.get() == "分で入力":
            exercise_minutes = self._get_float("exercise_minutes", "運動時間")
            if exercise_minutes is None:
                return
            exercise = exercise_kcal_from_minutes(weight, exercise_minutes, self.exercise_intensity.get())
            exercise_note = f"{int(exercise_minutes)}分（{self.exercise_intensity.get()}）→ 約{int(exercise)} kcal"
        else:
            exercise = self._get_float("exercise", "運動量")
            if exercise is None:
                return
            exercise_note = f"{int(exercise)} kcal（直接入力）"

        try:
            age = int(self.entries["age"].get().strip())
            if age < 1 or age > 120:
                raise ValueError
        except ValueError:
            messagebox.showerror("入力エラー", "年齢に正しい数値（1〜120）を入力してください。")
            return

        result = calculate(
            sleep_hours=sleep,
            intake_kcal=intake,
            exercise_kcal=exercise,
            weight_kg=weight,
            height_cm=height,
            age=age,
            sex=self.sex_var.get(),
        )

        lines = [
            "━━━━ 計算結果 ━━━━",
            f"状態: {result['status']}",
            "",
            f"基礎代謝量（BMR）      : {result['bmr']} kcal/日",
            f"基礎的な消費（推定）   : {result['base_burn']} kcal",
            f"摂取カロリー           : {result['intake']} kcal",
            f"すでに消費した運動量   : {result['exercise_done']} kcal",
            f"  （{exercise_note}）",
            f"エネルギー収支         : {result['energy_balance']:+d} kcal",
            "",
            f"睡眠による回復係数     : {result['sleep_factor']:.0%}",
            f"→ {result['sleep_comment']}",
            "",
            "━━━━ 今日あと活動できる量 ━━━━",
            f"追加で可能な運動量     : 約 {result['remaining_kcal']} kcal",
            "",
            "運動強度別の目安時間:",
            f"  ・軽い運動（散歩など）  : 約 {result['minutes']['軽い']} 分",
            f"  ・中程度（ジョギング等）: 約 {result['minutes']['中程度']} 分",
            f"  ・激しい運動（HIIT等）  : 約 {result['minutes']['激しい']} 分",
            "",
            "━━━━ アドバイス ━━━━",
            result["advice"],
        ]

        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "\n".join(lines))
        self.result_text.configure(state="disabled")


def main() -> None:
    app = ActivityApp()
    app.mainloop()


if __name__ == "__main__":
    main()
