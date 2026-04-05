# tetris1

Pyxel で動くシンプルなテトリスです。キーボードでもタッチでも遊べます。

## セットアップ

```bash
.venv/bin/pip install pyxel
```

## 実行

```bash
.venv/bin/python tetris1.py
```

## 操作

- `←` / `→`: 移動
- `Z` / `X`: 回転
- `↓`: ソフトドロップ
- `Space`: ハードドロップ
- `R`: リスタート
- 画面下のボタン: スマホ用タッチ操作
- GitHub Pages 版: 画面外下部の固定ボタンでも操作可能

## スマホで遊ぶ

Pyxel の HTML 出力を使うと、スマホのブラウザで遊べます。

```bash
.venv/bin/pyxel package . tetris1.py
.venv/bin/pyxel app2html tetris1.pyxapp
```

生成された HTML ファイルを Web サーバーに置いてスマホで開いてください。
このリポジトリ名のままなら出力は `tetris1.html` です。

## GitHub Pages で公開

このリポジトリは `docs/index.html` をそのまま GitHub Pages で公開する構成です。

1. GitHub に push する
2. GitHub の `Settings > Pages` を開く
3. `Source` を `Deploy from a branch` にする
4. `Branch` を `main`、フォルダを `/docs` にする
5. `Save` を押す

公開 URL は通常 `https://ractodaisuki.github.io/tetris1/` です。
