# YT_MP3
[youtube-dl](https://github.com/ytdl-org/youtube-dl) と [ffmpeg](https://github.com/FFmpeg/FFmpeg) を用いて、YouTubeから音声を抽出してMP3に変換するソフトです。URLと出力先を入力すればMP3ファイルでダウンロードすることができます。youtube-dl コマンドと ffmpeg コマンドが使えないとこのソフトは動きません。

Download the MP3 file from YouTube via [youtube-dl](https://github.com/ytdl-org/youtube-dl) and [ffmpeg](https://github.com/FFmpeg/FFmpeg). Input URL and output folder and you can download MP3 in that folder. YT_MP3 doesn't works if it cannot use youtube-dl command and ffmepeg command.


# 注意事項
youtube-dl と ffmpeg は同梱されていません。
それぞれのライセンスをよく読んで各自でインストールしてください。

YT_MP3 doesn't contain youtube-dl and ffmpeg.
You must understand licences and install those software.


# download_list.txt の設定
YT_MP3 では、download_list.txt にURLを入力することで一括処理を行うことができます。
download_list は出力先フォルダ内に入れておくと勝手に認識されます。

You can process multiple videos at once.
If you want to do it, you should make "download_list.txt" on output folder. YT_MP3 will detect the download list.

例 EXAMPLE)

![image](https://user-images.githubusercontent.com/55544957/148511214-e34d7e49-8e28-479a-aa60-c42e728d29fa.png)


# GUI
This software's language is Japanese. So, here is the translation.
| Japanese | English |
| - | - |
|出力ファイル|output folder|
|参照|Browse|
|ダウンロード|Download|

![image](https://user-images.githubusercontent.com/55544957/148512286-8385bb28-2722-4126-885e-75564be1aa2c.png)
