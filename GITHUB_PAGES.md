# GitHub Pages 公開手順

`activity_ios` フォルダを GitHub Pages で公開し、iPhone からいつでも使えるようにする手順です。

## 前提

- GitHub アカウントがあること
- PC に Git が入っていること

## 手順 1: GitHub にリポジトリを作る

1. [GitHub](https://github.com) にログイン
2. 右上 **+** → **New repository**
3. Repository name: 例 `activity-calculator`
4. **Public** を選択 → **Create repository**

## 手順 2: ファイルをアップロード

### 方法A: ブラウザから（簡単）

1. 作ったリポジトリを開く
2. **Add file** → **Upload files**
3. `activity_ios` フォルダの中身をすべてドラッグ＆ドロップ
   - `index.html`, `app.js`, `styles.css`, `manifest.json`, `sw.js`
   - `icon-192.png`, `icon-512.png`
4. **Commit changes**

### 方法B: コマンドから

```powershell
cd "C:\Users\牛頭峰一\Desktop\Python"
git init
git add activity_ios/
git commit -m "Add activity calculator PWA for iPhone"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/activity-calculator.git
git push -u origin main
```

※ 既にリポジトリがある場合は `activity_ios` の中身をルートに置くか、下記のサブフォルダ設定を使います。

## 手順 3: GitHub Pages を有効化

1. リポジトリの **Settings** → 左メニュー **Pages**
2. **Source**: Deploy from a branch
3. **Branch**:
   - ファイルをリポジトリ直下に置いた場合: `main` / `/ (root)`
   - `activity_ios` フォルダのまま置いた場合: `main` / `/activity_ios`
4. **Save**

数分待つと、次のような URL が表示されます。

```
https://あなたのユーザー名.github.io/activity-calculator/
```

または（サブフォルダの場合）

```
https://あなたのユーザー名.github.io/リポジトリ名/activity_ios/
```

## 手順 4: iPhone で使う

1. iPhone の **Safari** で上の URL を開く
2. 共有ボタン → **ホーム画面に追加**
3. アイコンから起動すればアプリのように使えます

## 更新方法

ファイルを変更したあと、再度 GitHub にアップロード（または `git push`）すれば、数分で自動的に反映されます。

## トラブルシューティング

| 症状 | 対処 |
|------|------|
| 404 になる | Pages の Branch / フォルダ設定を確認 |
| 真っ白 | `index.html` が正しい場所にあるか確認 |
| ホーム画面追加できない | Safari で開いているか確認（Chrome では不可） |
| 古い画面のまま | Safari の履歴を削除するか、しばらく待つ |
