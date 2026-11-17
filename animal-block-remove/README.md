# Animal Block Remove

動物のブロックを消していくパズルゲームです（Python + pygame）。

## あそびかた

### ブラウザで遊ぶ
GitHub Pages のURLを開いて、画面をクリックすると始まります。インストールはいりません。
（音は、はじめてキーを押したあとから鳴ります）

### パソコンで遊ぶ
1. Python を入れて、`pip install pygame` を打つ
2. `AnimalBlockRemove` フォルダの中で `python3 main.py` を打つ

## 操作
| キー | 動き |
|---|---|
| ← → | いどう |
| ↑ | かいてん |
| ↓ | はやく落とす |
| ↓↓（すばやく2回） | 一気に落とす |
| SPACE | ホールド |
| P | 一時停止 |
| ESC | タイトルへ |

## ファイル
- `index.html` / `animalblockremove.apk` / `animalblockremove.tar.gz` / `favicon.png` : ブラウザ版（pygbag で作ったもの）
- `AnimalBlockRemove/main.py` : ゲーム本体（パソコン版・改造用）
- `AnimalBlockRemove/font.ttf` : 日本語フォント（Noto Sans CJK JP をもとにしたもの。SIL Open Font License 1.1）
- `AnimalBlockRemove/OFL.txt` : フォントのライセンス

## ブラウザ版を作り直すとき
`AnimalBlockRemove` の1つ上のフォルダで次のように打ち、できた `AnimalBlockRemove/build/web` の中身で
このリポジトリの `index.html` などを置きかえます。

```
python3 -m pip install --upgrade pygbag
python3 -m pygbag --build AnimalBlockRemove
```
