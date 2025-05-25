# Termux YouTube Downloader Web App

Aplikasi web sederhana berbasis Flask untuk mengunduh video YouTube, dirancang untuk dijalankan di Termux.

## Fitur

* Antarmuka web sederhana untuk memasukkan URL.
* Pilihan kualitas dasar.
* Mengunduh video ke folder `~/storage/downloads`.
* Menjalankan unduhan di latar belakang (background thread).

## Prasyarat

* Termux terinstal di Android.
* Git terinstal di Termux (`pkg install git`).
* Python terinstal di Termux (`pkg install python`).
* FFmpeg terinstal di Termux (`pkg install ffmpeg`).
* Akses penyimpanan Termux diaktifkan (`termux-setup-storage`).

## Instalasi & Menjalankan

1.  **Clone Repositori:**
    ```bash
    git clone [URL_REPOSITORI_GIT_ANDA]
    cd yt-downloader-termux
    ```

2.  **Instal Dependensi:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Jalankan Aplikasi:**
    ```bash
    python app.py
    ```

4.  **Akses Aplikasi:**
    * Buka browser di perangkat Android Anda.
    * Kunjungi alamat: `http://localhost:8080` atau `http://127.0.0.1:8080`.

## Catatan Penting

* **Persyaratan Layanan YouTube:** Pastikan Anda mematuhi persyaratan layanan YouTube saat mengunduh video. Gunakan secara bertanggung jawab.
* **Pembaruan `yt-dlp`:** YouTube sering berubah. Anda mungkin perlu memperbarui `yt-dlp` secara berkala: `pip install --upgrade yt-dlp`.
* **Penyimpanan:** Video akan memakan ruang penyimpanan Anda.
* **Kinerja:** Kecepatan unduh bergantung pada koneksi internet dan kemampuan perangkat Anda.