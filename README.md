# Circle Crop GUI

このプロジェクトは、画像を円形に切り抜くためのグラフィカルユーザーインターフェース（GUI）を提供します。ユーザーは直感的なインターフェースを使って画像を選択し、切り抜く範囲を視覚的に指定できます。

---

## ディレクトリ構成

```
Circle/
├── .circleci/
│   └── config.yml                # CircleCI用CI/CD設定ファイル
├── circle-crop-gui/
│   ├── src/
│   │   ├── main.py               # アプリケーションのエントリーポイント
│   │   ├── gui.py                # TkinterによるGUI実装
│   │   └── image_utils.py        # 画像の円形切り抜きロジック
│   └── tests/
│       └── test_image_utils.py   # image_utilsのテストコード
├── .gitignore                    # 仮想環境などの除外設定
├── requirements.txt              # 必要なPythonパッケージ
└── README.md                     # このファイル
```

---

## インストール方法

1. 必要なパッケージをインストールします。

   ```
   pip install -r requirements.txt
   ```

---

## 使い方

1. アプリケーションを起動します。

   ```
   python circle-crop-gui/src/main.py
   ```

2. 「Select Image」ボタンで画像ファイルを選択します。

3. キャンバス上でマウスドラッグして円形の切り抜き範囲を指定できます。  
   （中心座標・半径も手動で入力可能）

4. 「Crop Image」ボタンで切り抜き画像を保存できます。

---

## 依存パッケージ

- Pillow
- pytest（テスト用）

---

## Gitブランチ命名ルール

<タイプ>/<変更内容>-<issue番号（任意）>

### タイプの種類：
- `feature`：新機能の追加
- `fix`：バグ修正
- `refactor`：リファクタリング（挙動を変えない改善）
- `chore`：設定ファイルやREADMEの更新など
- `test`：テストの追加・修正

---

## CI/CD

CircleCIで自動テストが実行されるよう `.circleci/config.yml` を用意しています。