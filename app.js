function calcBmr(weightKg, heightCm, age, sex) {
  if (sex === "男性") {
    return 10 * weightKg + 6.25 * heightCm - 5 * age + 5;
  }
  return 10 * weightKg + 6.25 * heightCm - 5 * age - 161;
}

function sleepFactor(sleepHours) {
  if (sleepHours >= 7.0 && sleepHours <= 8.5) {
    return { factor: 1.0, comment: "睡眠は理想的です。フルパワーで活動できます。" };
  }
  if ((sleepHours >= 6.0 && sleepHours < 7.0) || (sleepHours > 8.5 && sleepHours <= 9.0)) {
    return { factor: 0.88, comment: "睡眠はやや不足/過多です。無理のない運動量にしましょう。" };
  }
  if ((sleepHours >= 5.0 && sleepHours < 6.0) || (sleepHours > 9.0 && sleepHours <= 10.0)) {
    return { factor: 0.75, comment: "睡眠不足または過眠気味です。軽めの活動がおすすめです。" };
  }
  if (sleepHours < 5.0) {
    return { factor: 0.55, comment: "睡眠不足です。激しい運動は避け、休息を優先してください。" };
  }
  return { factor: 0.7, comment: "睡眠がかなり長いです。体がだるい場合は軽い運動に留めましょう。" };
}

function kcalPerMinute(weightKg, intensity) {
  const metValues = { 軽い: 3.0, 中程度: 5.0, 激しい: 8.0 };
  return metValues[intensity] * weightKg * 0.0175;
}

function exerciseKcalFromMinutes(weightKg, minutes, intensity) {
  return minutes * kcalPerMinute(weightKg, intensity);
}

function toggleExerciseMode() {
  const mode = document.getElementById("exerciseMode").value;
  const isMinutes = mode === "minutes";
  document.getElementById("exerciseKcalField").classList.toggle("hidden", isMinutes);
  document.getElementById("exerciseMinutesField").classList.toggle("hidden", !isMinutes);
  document.getElementById("exerciseIntensityField").classList.toggle("hidden", !isMinutes);
}

function calculate({ sleepHours, intakeKcal, exerciseKcal, weightKg, heightCm, age, sex }) {
  const bmr = calcBmr(weightKg, heightCm, age, sex);
  const sleepBurn = (bmr / 24) * sleepHours * 0.9;
  const awakeRestBurn = (bmr / 24) * (24 - sleepHours) * 1.05;
  const baseBurn = sleepBurn + awakeRestBurn;
  const energyBalance = intakeKcal - baseBurn - exerciseKcal;
  const { factor, comment: sleepComment } = sleepFactor(sleepHours);
  const remainingKcal = Math.max(0, energyBalance * factor);

  const minutes = {};
  for (const intensity of ["軽い", "中程度", "激しい"]) {
    const rate = kcalPerMinute(weightKg, intensity);
    minutes[intensity] = rate > 0 ? Math.floor(remainingKcal / rate) : 0;
  }

  const dailyExerciseCap = intakeKcal * 0.35 * factor;
  const usedRatio = dailyExerciseCap > 0 ? exerciseKcal / dailyExerciseCap : 1.0;

  let status;
  let advice;
  if (energyBalance < 0) {
    status = "エネルギー不足";
    advice = `摂取カロリーが基礎代謝＋運動量を下回っています（不足: ${Math.abs(Math.floor(energyBalance))} kcal）。追加の運動より、栄養補給と休息を優先してください。`;
  } else if (remainingKcal < 80) {
    status = "ほぼ限界";
    advice = "本日の活動量は十分です。激しい運動は控え、ストレッチや散歩程度にしましょう。";
  } else if (usedRatio >= 0.8) {
    status = "運動量 多め";
    advice = "すでに多く運動しています。無理せず、残りは軽い運動がおすすめです。";
  } else {
    status = "活動可能";
    advice = `あと約 ${Math.floor(remainingKcal)} kcal 分の運動が可能です。中程度の運動なら約 ${minutes["中程度"]} 分が目安です。`;
  }

  return {
    bmr: Math.floor(bmr),
    baseBurn: Math.floor(baseBurn),
    energyBalance: Math.floor(energyBalance),
    remainingKcal: Math.floor(remainingKcal),
    sleepFactor: factor,
    sleepComment,
    minutes,
    status,
    advice,
    exerciseDone: Math.floor(exerciseKcal),
    intake: Math.floor(intakeKcal),
  };
}

function parseNumber(id, name) {
  const el = document.getElementById(id);
  const value = parseFloat(el.value);
  if (Number.isNaN(value) || value < 0) {
    throw new Error(`${name}に正しい数値を入力してください。`);
  }
  return value;
}

function renderResult(result) {
  const sign = result.energyBalance >= 0 ? "+" : "";
  const exerciseNote = result.exerciseNote
    ? `<p class="sleep-note">${result.exerciseNote}</p>`
    : "";
  return `
    <div class="status-badge">${result.status}</div>
    <dl class="result-list">
      <div><dt>基礎代謝量（BMR）</dt><dd>${result.bmr} kcal/日</dd></div>
      <div><dt>基礎的な消費</dt><dd>${result.baseBurn} kcal</dd></div>
      <div><dt>摂取カロリー</dt><dd>${result.intake} kcal</dd></div>
      <div><dt>すでに消費した運動量</dt><dd>${result.exerciseDone} kcal</dd></div>
      <div><dt>エネルギー収支</dt><dd>${sign}${result.energyBalance} kcal</dd></div>
      <div><dt>睡眠による回復係数</dt><dd>${Math.round(result.sleepFactor * 100)}%</dd></div>
    </dl>
    ${exerciseNote}
    <p class="sleep-note">${result.sleepComment}</p>
    <h2>今日あと活動できる量</h2>
    <p class="highlight">${result.remainingKcal} <span>kcal</span></p>
    <ul class="minutes">
      <li><span>軽い運動</span><strong>${result.minutes["軽い"]} 分</strong></li>
      <li><span>中程度</span><strong>${result.minutes["中程度"]} 分</strong></li>
      <li><span>激しい運動</span><strong>${result.minutes["激しい"]} 分</strong></li>
    </ul>
    <div class="advice">
      <h3>アドバイス</h3>
      <p>${result.advice}</p>
    </div>
  `;
}

function saveInputs() {
  const ids = [
    "sleep",
    "intake",
    "exerciseMode",
    "exercise",
    "exerciseMinutes",
    "exerciseIntensity",
    "weight",
    "height",
    "age",
    "sex",
  ];
  const data = {};
  ids.forEach((id) => {
    const el = document.getElementById(id);
    data[id] = el.value;
  });
  localStorage.setItem("activityInputs", JSON.stringify(data));
}

function loadInputs() {
  const raw = localStorage.getItem("activityInputs");
  if (!raw) return;
  try {
    const data = JSON.parse(raw);
    Object.entries(data).forEach(([id, value]) => {
      const el = document.getElementById(id);
      if (el) el.value = value;
    });
    toggleExerciseMode();
  } catch (_) {
    // ignore
  }
}

document.getElementById("exerciseMode").addEventListener("change", toggleExerciseMode);

document.getElementById("calcBtn").addEventListener("click", () => {
  const resultEl = document.getElementById("result");
  try {
    const sleep = parseNumber("sleep", "睡眠時間");
    if (sleep > 24) throw new Error("睡眠時間は0〜24時間で入力してください。");

    const intake = parseNumber("intake", "摂取カロリー");
    const weight = parseNumber("weight", "体重");
    const height = parseNumber("height", "身長");
    const age = parseInt(document.getElementById("age").value, 10);
    if (Number.isNaN(age) || age < 1 || age > 120) {
      throw new Error("年齢に正しい数値（1〜120）を入力してください。");
    }

    const mode = document.getElementById("exerciseMode").value;
    let exerciseKcal;
    let exerciseNote;
    if (mode === "minutes") {
      const minutes = parseNumber("exerciseMinutes", "運動時間");
      const intensity = document.getElementById("exerciseIntensity").value;
      exerciseKcal = exerciseKcalFromMinutes(weight, minutes, intensity);
      exerciseNote = `入力: ${Math.floor(minutes)}分（${intensity}）→ 約 ${Math.floor(exerciseKcal)} kcal に換算`;
    } else {
      exerciseKcal = parseNumber("exercise", "運動量");
      exerciseNote = `入力: ${Math.floor(exerciseKcal)} kcal（直接入力）`;
    }

    const result = calculate({
      sleepHours: sleep,
      intakeKcal: intake,
      exerciseKcal,
      weightKg: weight,
      heightCm: height,
      age,
      sex: document.getElementById("sex").value,
    });
    result.exerciseNote = exerciseNote;

    saveInputs();
    resultEl.innerHTML = renderResult(result);
    resultEl.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    resultEl.innerHTML = `<p class="error">${err.message}</p>`;
  }
});

loadInputs();
toggleExerciseMode();

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("sw.js").catch(() => {});
}
