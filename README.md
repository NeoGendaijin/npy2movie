# 動画処理スクリプト

このリポジトリには、NPYファイルや画像ファイルから動画を作成するためのスクリプトが含まれています。

## ディレクトリ構造

```
.
├── source/           # 入力ファイル用ディレクトリ
│   ├── npy/          # NPYファイル用ディレクトリ
│   └── images/       # 画像ファイル用ディレクトリ
├── results/          # 出力ファイル用ディレクトリ
│   └── movie/        # 動画ファイル用ディレクトリ
├── create_animations.py        # 画像からアニメーションを作成するスクリプト
├── create_video_from_npy.py    # NPYファイルから動画を作成するスクリプト
├── create_video_universal.py   # 複数のNPYファイルから動画を作成するスクリプト
└── create_video_with_ffmpeg.py # FFmpegを使用して動画を作成するスクリプト
```

## 使い方

### 1. 入力ファイルの配置

- NPYファイルは `source/npy/` ディレクトリに配置してください。
- 画像ファイルは `source/images/` ディレクトリに配置してください。

### 2. スクリプトの実行

#### NPYファイルから動画を作成する

```bash
python3 create_video_from_npy.py
```

このスクリプトは `source/npy/tactile_target_array.npy` ファイルから動画を作成します。

#### 複数のNPYファイルから動画を作成する

```bash
python3 create_video_universal.py
```

このスクリプトは `source/npy/` ディレクトリ内のすべてのNPYファイルから動画を作成します。

#### FFmpegを使用してNPYファイルから動画を作成する

```bash
python3 create_video_with_ffmpeg.py
```

このスクリプトは `source/npy/tactile_output_array.npy` ファイルからFFmpegを使用して動画を作成します。

#### 画像ファイルからアニメーションを作成する

```bash
python3 create_animations.py
```

このスクリプトは `source/images/` ディレクトリ内の画像ファイルからアニメーションを作成します。

### 3. 出力ファイル

すべての出力動画ファイルは `results/movie/` ディレクトリに保存されます。

## 必要なパッケージ

以下のPythonパッケージが必要です：

- numpy
- opencv-python
- pillow
- imageio

これらのパッケージは以下のコマンドでインストールできます：

```bash
pip3 install numpy opencv-python pillow imageio
```
# npy2movie
