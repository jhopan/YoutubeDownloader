from flask import Flask, request, render_template, jsonify, send_from_directory, url_for
import yt_dlp
import os
import platform
import logging
import re

# Konfigurasi logging dasar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
# Ganti dengan ENV untuk production!
app.secret_key = 'e8a3b7d1c5f0a2e9b6d4c8f1a3e7b9d5c0f2a4e8b6d3c7f1'

# --- Lokasi Download ---
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

FFMPEG_PATH = None
if "com.termux" in os.environ.get("PREFIX", "").lower():
    FFMPEG_PATH = '/data/data/com.termux/files/usr/bin/ffmpeg'
    logging.info(f"Termux detected. FFMPEG Path: {FFMPEG_PATH}")
    if not os.path.exists(FFMPEG_PATH):
        logging.warning("FFmpeg tidak ditemukan di Termux! Konversi MP3 akan GAGAL.")
else:
    logging.info("Desktop detected. FFmpeg akan dicari di PATH.")

def sanitize_filename(filename):
    """Membersihkan nama file."""
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()

@app.route('/')
def index():
    """Menampilkan halaman utama."""
    return render_template('index.html')

@app.route('/get_formats', methods=['POST'])
def get_formats():
    """Mengambil daftar format video/audio dari URL."""
    data = request.get_json()
    video_url = data.get('url')

    if not video_url:
        return jsonify({'status': 'error', 'message': 'URL tidak ditemukan.'}), 400

    try:
        logging.info(f"Mengambil format untuk: {video_url}")
        ydl_opts = {'quiet': True, 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
        
        formats_list = []
        video_title = info_dict.get('title', 'video_tanpa_judul')

        for f in info_dict.get('formats', []):
            # Hanya ambil format yang punya URL (bisa diunduh)
            if f.get('url'):
                format_note = f.get('format_note', '')
                resolution = f.get('resolution', 'Audio')
                ext = f.get('ext', 'N/A')
                filesize = f.get('filesize') or f.get('filesize_approx')
                filesize_mb = f"~{filesize / (1024*1024):.1f} MB" if filesize else "N/A"

                # Filter sederhana untuk tampilan (bisa disesuaikan)
                # Ambil video+audio (biasanya format_note ada 'p') atau audio saja
                # Atau video saja
                if 'p' in format_note or 'audio only' in f.get('format', ''):
                    formats_list.append({
                        'id': f.get('format_id'),
                        'text': f"{ext.upper()} - {resolution} ({format_note}) - {filesize_mb}",
                        'is_audio': 'audio only' in f.get('format', '')
                    })

        # Tambahkan opsi MP3 secara manual
        formats_list.append({
            'id': 'mp3_128',
            'text': "MP3 - 128kbps (Audio Saja - Memerlukan Konversi)",
            'is_audio': True
        })

        logging.info(f"Format ditemukan: {len(formats_list)}")
        return jsonify({
            'status': 'success',
            'formats': formats_list,
            'title': video_title
        })

    except Exception as e:
        logging.error(f"Gagal mengambil format: {e}")
        return jsonify({'status': 'error', 'message': f"Gagal mengambil format: {e}"})

@app.route('/download', methods=['POST'])
def download_video_specific():
    """Mengunduh format spesifik atau mengkonversi ke MP3."""
    data = request.get_json()
    video_url = data.get('url')
    format_id = data.get('format_id')
    video_title = data.get('title', 'video_unduhan')

    if not video_url or not format_id:
        return jsonify({'status': 'error', 'message': 'URL atau Format ID hilang.'}), 400

    clean_title = sanitize_filename(video_title)
    final_filename = ""
    ydl_opts = {}

    try:
        if format_id == 'mp3_128':
            logging.info(f"Memulai konversi MP3 untuk: {video_url}")
            final_filename = f"{clean_title}.mp3"
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, final_filename),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
                'ffmpeg_location': FFMPEG_PATH,
                'quiet': False, 'progress': True, 'noplaylist': True,
            }
        else:
            logging.info(f"Memulai download format {format_id} untuk: {video_url}")
            # Perlu cara untuk tahu ekstensi dari format_id, atau biarkan yt-dlp menentukannya
            # Pendekatan sederhana: Biarkan yt-dlp menamainya, lalu coba temukan
            # Pendekatan lebih baik: Ambil info lagi atau simpan info sebelumnya.
            # Untuk demo, kita buat nama file dengan format_id (kurang ideal)
            # --> Mari kita coba buat nama file yang lebih baik dengan .%(ext)s
            final_filename_template = f"{clean_title}_{format_id}.%(ext)s"
            ydl_opts = {
                'format': format_id,
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, final_filename_template),
                'quiet': False, 'progress': True, 'noplaylist': True,
                'ffmpeg_location': FFMPEG_PATH,
            }

        # Lakukan download/konversi (INI BLOCKING!)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Dapatkan info dulu untuk tahu nama file pastinya
            info = ydl.extract_info(video_url, download=False)
            # Jika MP3, nama file sudah kita tentukan
            if format_id != 'mp3_128':
                 # Cari format yang cocok untuk dapat ekstensi
                 sel_format = next((f for f in info['formats'] if f['format_id'] == format_id), None)
                 ext = sel_format.get('ext', 'mp4') if sel_format else 'mp4'
                 final_filename = f"{clean_title}_{format_id}.{ext}"
                 ydl_opts['outtmpl'] = os.path.join(DOWNLOAD_FOLDER, final_filename) # Update outtmpl

            # Sekarang download
            ydl.download([video_url])
        
        logging.info(f"Proses selesai untuk: {final_filename}")
        download_link = url_for('serve_download', filename=final_filename, _external=True)
        
        return jsonify({
            'status': 'success', 
            'message': f"File '{final_filename}' siap!", 
            'link': download_link,
            'filename': final_filename
        })

    except Exception as e:
        logging.error(f"Gagal download/konversi: {e}")
        return jsonify({'status': 'error', 'message': f"Gagal download/konversi: {e}"})

@app.route('/downloads/<filename>')
def serve_download(filename):
    """Menyajikan file yang sudah diunduh."""
    logging.info(f"Menyajikan file: {filename}")
    try:
        return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        logging.error(f"File tidak ditemukan saat disajikan: {filename}")
        return "File tidak ditemukan.", 404

if __name__ == '__main__':
    is_termux_env = "com.termux" in os.environ.get("PREFIX", "").lower()
    debug_mode = not is_termux_env
    logging.info(f"Menjalankan Flask server dengan debug mode: {debug_mode}")
    app.run(host='0.0.0.0', port=8080, debug=debug_mode)
