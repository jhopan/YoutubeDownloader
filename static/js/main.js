document.addEventListener('DOMContentLoaded', () => {
    const getFormatsButton = document.getElementById('getFormatsButton');
    const downloadButton = document.getElementById('downloadButton');
    const urlInput = document.getElementById('url');
    const formatsDiv = document.getElementById('formatsList');
    const statusDiv = document.getElementById('status');
    let currentVideoTitle = 'video_unduhan'; // Simpan judul video

    getFormatsButton.addEventListener('click', async (event) => {
        event.preventDefault();
        const videoUrl = urlInput.value;

        if (!videoUrl) {
            showStatus('URL YouTube tidak boleh kosong!', 'error');
            return;
        }

        showStatus('Mengambil daftar format...', 'info');
        getFormatsButton.disabled = true;
        downloadButton.classList.add('hidden');
        formatsDiv.innerHTML = ''; // Kosongkan daftar lama

        try {
            const response = await fetch('/get_formats', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: videoUrl }),
            });

            const data = await response.json();

            if (data.status === 'success') {
                showStatus('Pilih format di bawah ini:', 'success');
                currentVideoTitle = data.title; // Simpan judul
                displayFormats(data.formats);
                downloadButton.classList.remove('hidden'); // Tampilkan tombol download
            } else {
                showStatus(`Error: ${data.message}`, 'error');
            }
        } catch (error) {
            showStatus(`Error jaringan: ${error}`, 'error');
        } finally {
            getFormatsButton.disabled = false;
        }
    });

    downloadButton.addEventListener('click', async (event) => {
        event.preventDefault();
        const selectedFormat = document.querySelector('input[name="format"]:checked');

        if (!selectedFormat) {
            showStatus('Harap pilih format terlebih dahulu!', 'error');
            return;
        }

        const videoUrl = urlInput.value;
        const formatId = selectedFormat.value;

        showStatus(`Memproses format ${formatId}... Ini akan memakan waktu lama, harap tunggu...`, 'info');
        downloadButton.disabled = true;
        getFormatsButton.disabled = true;

        try {
            const response = await fetch('/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: videoUrl, format_id: formatId, title: currentVideoTitle }),
            });

            const data = await response.json();

            if (data.status === 'success') {
                showStatus('Server selesai! Memulai unduhan otomatis...', 'success');
                triggerDownload(data.link, data.filename);
            } else {
                showStatus(`Error: ${data.message}`, 'error');
            }
        } catch (error) {
            showStatus(`Error jaringan: ${error}`, 'error');
        } finally {
            downloadButton.disabled = false;
            getFormatsButton.disabled = false;
        }
    });

    function showStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = `status-${type}`;
    }

    function displayFormats(formats) {
        formatsDiv.innerHTML = ''; // Hapus isi sebelumnya
        formats.forEach(format => {
            const div = document.createElement('div');
            div.classList.add('format-item');

            const input = document.createElement('input');
            input.type = 'radio';
            input.id = `format_${format.id}`;
            input.name = 'format';
            input.value = format.id;

            const label = document.createElement('label');
            label.htmlFor = `format_${format.id}`;
            label.textContent = format.text;

            div.appendChild(input);
            div.appendChild(label);
            formatsDiv.appendChild(div);
        });
    }

    function triggerDownload(link, filename) {
        const a = document.createElement('a');
        a.href = link;
        a.download = filename || 'downloaded_video';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        showStatus('Pengunduhan seharusnya sudah dimulai di browser Anda!', 'success');
    }
});
