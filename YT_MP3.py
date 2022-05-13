
import datetime, math, subprocess, os, sys, re, threading, urllib.request
import tkinter as tk
from tkinter.constants import VERTICAL
import tkinter.font as tkFont
import tkinter.filedialog as tkFDialog
from tkinter import messagebox
from tkinter import ttk
from ctypes import windll
import youtube_dl
from mutagen.id3 import APIC, ID3

# global variables
SOFTWARE_NAME = 'YouTube MP3'
MAX_LOG_COUNT = 10
CURRENT_DIRECTORY = os.getcwd()
console_log_txt = ''
csv_flag = False
processing_flag = False
attempt_count = 1
error_cfgs = []
ready_flag = False


def video_download(url):

    global attempt_count
    change_button_status(False)
    # url check
    if not ('https://www.youtube.com/' in url or 'https://youtu.be/' in url):
        console_log('YouTubeのURLにのみ対応しています。')
        if not csv_flag:
            messagebox.showerror(SOFTWARE_NAME, 'URLが間違っています。')
        change_button_status(True)
        return 'URLが間違っています。'

    # 動画情報 
    video_title = run_command('youtube-dl {} --get-title'.format(url), False)[0]
    if video_title == '':
        video_title = run_command('youtube-dl {} --get-title'.format(url), False)[0]
    video_duration = run_command('youtube-dl {} --get-duration'.format(url), False)[0]

    console_log(['', 'タイトル  > {}'.format(video_title), '動画時間  > {}'.format(video_duration), ''], list_flag=True)

    # DL処理
    output_file_name = '{}/{}'.format(output_entry.get(), re.sub(r"[\\/:*?'<>|]+\n",'', video_title))
    audio_url = run_command('youtube-dl {} --format bestaudio -g'.format(url), display=False)[0]
    console_log(['音声のダウンロードを開始します。', 'URL > {}'.format(audio_url)], list_flag=True)
    run_command('ffmpeg -y -i "{}" "{}.mp3"'.format(audio_url, output_file_name))
    console_log(['音声ダウンロード完了。', ''], list_flag=True)

    try:
        # サムネイル カバーアート
        console_log('カバーアート用にサムネイルをダウンロードします。')
        thumb_url = run_command('youtube-dl --get-thumbnail {}'.format(url), display=False)[0]
        # URLに ? が入ってるとうまく行かない時がある
        if '?' in thumb_url:
            thumb_url = thumb_url[0:thumb_url.find('?')]
        run_command('ffmpeg "{}/thumb.jpg" -y -i "{}"'.format(output_entry.get(), thumb_url), display=False)

        thumb_url  = output_entry.get() + '/thumb.jpg'
        audio = ID3('{}.mp3'.format(output_file_name))
        with open(thumb_url, 'rb') as albumart:
            audio.add(
                APIC(
                    encoding=3,
                    mime='image/jpg',
                    type=3,
                    data=albumart.read()
                ))
        audio.save(v2_version=3)
        console_log('サムネイルを設定しました。')
        if os.path.exists(thumb_url):
            os.remove(thumb_url)

        console_log('')
        console_log('ダウンロード完了。')
        console_log('')


    except Exception as e:
        console_log(['エラーが発生しました。 この動画のサムネイルはダウンロードできない可能性があります。', str(e.with_traceback(sys.exc_info()[2])), ''], list_flag=True)
        change_button_status(True)
        return ' [ERROR] ' + str(e.with_traceback(sys.exc_info()[2]))
    
    if not csv_flag:
        messagebox.showinfo(SOFTWARE_NAME, '動画のダウンロードが終了しました。')
        change_button_status(True)
    return 'OK'



def csv_download(urls):
    global attempt_count, error_cfgs
    print(urls)
    for url in urls:
        attempt_count = 1
        console_log('')
        console_log('---------------------------------')
        console_log('  ' + str(urls.index(url) + 1) + '個目の設定で出力します。')
        console_log('---------------------------------')
        console_log('')
        msg = video_download(url)
        if msg == 'OK':
            error_cfgs.append('O [' + ','.join(url) + '] 正常に終了しました。')
        else:
            error_cfgs.append('X [' + ','.join(url) + '] ' + msg)
    messagebox.showinfo(SOFTWARE_NAME, '動画のダウンロードが終了しました。')
    console_log('入力されたタスクが終了しました。')
    error_cfgs.append('')
    console_log(error_cfgs, list_flag=True)
    global csv_flag
    csv_flag = False
    change_button_status(True)
    return


def comfirm_clicked():
    # 二重処理を防ぐ
    global processing_flag
    if processing_flag:
        return
    else:
        processing_flag = True

    try:
        answers = [url_entry.get(), output_entry.get()]
    except Exception as e:
        console_log('予想外のエラーが発生しました。')
        return

    # check output directory
    if not os.path.isdir(answers[1]):
        console_log('出力フォルダが存在していません。')
        messagebox.showerror(SOFTWARE_NAME, '出力フォルダが見つかりません。')
        return

    # Youtube接続確認
    try:
        urllib.request.urlopen('https://www.youtube.com/').close()
    except :
        console_log('YouTubeに接続できません')
        messagebox.showerror(SOFTWARE_NAME, 'YouTubeに接続できませんでした。')
        return

    # CSVチェック
    urls = ''
    global csv_flag, error_cfgs
    csv_flag = False
    if os.path.isfile(answers[1] + '/download_list.txt') and answers[0].replace(' ', '') == '': # if download list exists and url is empty
        console_log(['', '設定ファイルを確認しました。'], list_flag=True)
        f = open(answers[1] + '/download_list.txt', encoding='UTF-8', mode='r')
        urls = f.readlines()
        if len(urls) != 0:
            csv_flag = True
            for url in urls: # format url
                urls[urls.index(url)] = url.replace('\n', '').replace(' ', '')
    
    
    # 入力チェック
    if csv_flag:
        # CSV出力
        thread = threading.Thread(target=csv_download, args=[urls], daemon=True)
        thread.start()
        return

    else:
        # ノーマル出力

        # check textboxes 
        if answers[0] == '':
            console_log('URLを入力してください。')
            messagebox.showerror(SOFTWARE_NAME, 'URLが空欄です。')
            return
        if answers[1] == '':
            console_log('出力ファイルを設定してください。')
            messagebox.showerror(SOFTWARE_NAME, '出力ファイルを設定してください。')
            return
        
        attempt_count = 1
        thread = threading.Thread(target=video_download, args=[answers[0]], daemon=True)
        thread.start()
        return


def run_command(cmd, display=True, cwd=CURRENT_DIRECTORY):
    if cwd == '':
        cwd = output_entry.get()

    # コマンド実行
    try:
        sproc = subprocess.run(cmd, cwd=cwd, **subprocess_args(True))
    except (subprocess.CalledProcessError, IndexError, OSError):
        console_log('コマンド実行時にエラーが発生しました。')
        return 
    # 出力を取得
    try:
        output_lines = sproc.stdout.decode('UTF-8').split('\n')
    except Exception as e:
        output_lines = sproc.stdout.decode('cp932').split('\n')

    # エラーが発生したときはエラーメッセージを返す
    if len(output_lines) == 1 and output_lines[0] == '':
        try:
            cmd_error = sproc.stderr.decode('UTF-8').split('\n')
        except Exception as e:
            cmd_error = sproc.stderr.decode('cp932').split('\n')
        cmd_error.insert(0, '-----------ERROR-----------')
        console_log(cmd_error, list_flag=True, log_only=True)

    if display:
        console_log(output_lines, list_flag=True)
    
    global ready_flag
    if not ready_flag:
        change_button_status(True)
        ready_flag = True
    return output_lines


def output_clicked():
    output_file_path = tkFDialog.askdirectory()
    output_entry.delete(0, tk.END)
    output_entry.insert(0, output_file_path)


def console_log(txt, list_flag=False, log_only=False):
    ms = str(math.floor(datetime.datetime.now().microsecond/10000)).zfill(2)
    if not log_only: # log_only が True のときはコンソールをオフにする
        console_viewer.configure(state='normal')
    
    global console_log_txt
    if list_flag:
        for n in range(0, len(txt)):
            console_viewer.insert('1.0', '[' + datetime.datetime.now().strftime('%H:%M:%S.') + ms + ']  ' + txt[-1*n - 1] + '\n')
        console_log_txt += '\n'.join(txt)
    else:
        console_viewer.insert('1.0', '[' + datetime.datetime.now().strftime('%H:%M:%S.') + ms + ']  ' + txt + '\n')
        console_log_txt = console_log_txt + txt + '\n'
    console_viewer.configure(state='disabled')


def change_button_status(flag):
    global csv_flag
    if flag:
        if not csv_flag:
            url_entry['state'] = tk.NORMAL
            output_entry['state'] = tk.NORMAL
            output_button['state'] = tk.NORMAL
            confirm_button['state'] = tk.NORMAL
    else:
        url_entry['state'] = tk.DISABLED
        output_entry['state'] = tk.DISABLED
        output_button['state'] = tk.DISABLED
        confirm_button['state'] = tk.DISABLED


def on_closing():
    for _, _, files in os.walk(CURRENT_DIRECTORY + '/log'):
        if len(files) >= MAX_LOG_COUNT - 1:
            files.sort()
            files = files[MAX_LOG_COUNT - 2:-1]
            for f in files:
                os.remove(CURRENT_DIRECTORY + '/log/' + f)

    now = datetime.datetime.now()
    # config
    with open(CURRENT_DIRECTORY + '/config.cfg', encoding='UTF-8', mode='w') as f:
        f.write(output_entry.get())
        f.close()
    # log
    if not os.path.isdir(CURRENT_DIRECTORY + '/log'):
        os.mkdir(CURRENT_DIRECTORY + '/log')
    with open(CURRENT_DIRECTORY + '/log/' + str(now.year).zfill(4) + str(now.month).zfill(2) + str(now.day).zfill(2) + str(now.hour).zfill(2) + str(now.minute).zfill(2) + str(now.second).zfill(2) + '.txt', encoding='UTF-8', mode='w') as f:
        global console_log
        f.write(console_log_txt)
        f.close()
    sys.exit(0)


def subprocess_args(include_stdout=True):
    if hasattr(subprocess, 'STARTUPINFO'):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        env = os.environ
    else:
        si = None
        env = None
    
    if include_stdout:
        ret = {'stdout': subprocess.PIPE}
    else:
        ret = {}
    
    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env })
    return ret


# Pyinstaller 用 埋め込みファイル参照
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS + '\\' + relative_path 
    return os.path.join(os.path.abspath('.'), relative_path)


if __name__ == '__main__':
    # difine consts
    TIME_ENTRY_WIDTH = 5
    COLOR_BG = '#f2f6fc'
    WIN_WIDTH = 1280
    WIN_HEIGHT = 720
    config_txt = ''
    if os.path.isfile(CURRENT_DIRECTORY + '/config.cfg'):
        with open(CURRENT_DIRECTORY + '/config.cfg', encoding='UTF-8', mode='r') as f:
            config_txt = f.readline()
            f.close()
        pass
    
    #----------------------------------------------------------------------------------------------
    #       GUIレイアウト
    #----------------------------------------------------------------------------------------------
    # create window
    window = tk.Tk()
    window.resizable(width=False, height=False)
    window.geometry('{}x{}+{}+{}'.format(WIN_WIDTH, WIN_HEIGHT, int((windll.user32.GetSystemMetrics(0)-WIN_WIDTH)/2), int((windll.user32.GetSystemMetrics(1)-WIN_HEIGHT)/2)))
    window.config(bg=COLOR_BG)
    window.title(SOFTWARE_NAME)
    
    # style
    normal_text_font = tkFont.Font(family='Rounded-L M+ 1c heavy', size=15)
    s = ttk.Style()
    s.configure('mutoxu_n.TFrame', background=COLOR_BG)
    s.configure('mutoxu_n.TLabel', background=COLOR_BG)

    # url
    url_frame = ttk.Frame(window, padding=0, style='mutoxu_n.TFrame')
    url_frame.pack(pady=15)
    url_label = ttk.Label(url_frame, text='URL: ', font=normal_text_font, style='mutoxu_n.TLabel').pack(side=tk.LEFT)
    url_entry = ttk.Entry(url_frame, width=150,)
    url_entry.pack(side=tk.LEFT)

    # output config
    output_frame = ttk.Frame(window, padding=3, style='mutoxu_n.TFrame')
    output_frame.pack()
    output_label = ttk.Label(output_frame, text='出力ファイル: ', font=normal_text_font, style='mutoxu_n.TLabel').pack(side=tk.LEFT)
    output_entry = ttk.Entry(output_frame, width=150)
    output_entry.insert(0, config_txt)
    output_entry.pack(side=tk.LEFT)
    output_button = ttk.Button(output_frame, text='参照', command=output_clicked)
    output_button.pack(side=tk.LEFT)

    # confirm button
    confirm_frame = ttk.Frame(window, padding=5, style='mutoxu_n.TFrame')
    confirm_frame.pack()
    confirm_button = ttk.Button(confirm_frame, text='ダウンロード', command=comfirm_clicked)
    confirm_button.pack(side=tk.RIGHT)

    # console viewer
    console_frame = ttk.Frame(window, width=1200, height=500, style='mutoxu_n.TFrame')
    console_frame.pack()
    console_viewer = tk.Text(console_frame, width=160, height=50, state='disabled')
    console_viewer.pack(pady=20)
    console_log('')
    console_log(SOFTWARE_NAME + ' mutoxu_n © 2022')
    console_log(['youtube-dl をアップデートします。'], list_flag=True)
    change_button_status(False)
    threading.Thread(target=run_command, args=['youtube-dl --update'], daemon=True).start()

    # icon
    window.wm_iconbitmap(resource_path('image/icon.ico'))
    # Start
    window.protocol('WM_DELETE_WINDOW', on_closing)
    window.mainloop()
