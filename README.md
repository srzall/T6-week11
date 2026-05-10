# API Post Manager - PySide6

## 📖 Deskripsi Singkat
**API Post Manager** adalah aplikasi desktop berbasis antarmuka grafis (GUI) yang dirancang untuk mengelola data *post* menggunakan REST API publik (`https://api.pahrul.my.id/api/posts`). 

Aplikasi ini mendemonstrasikan implementasi operasi CRUD (Create, Read, Update, Delete) secara utuh. Untuk memberikan pengalaman pengguna yang maksimal, seluruh *network request* (panggilan API) dijalankan di belakang layar menggunakan **Threading (QThread)**, sehingga antarmuka aplikasi (UI) tetap responsif dan tidak mengalami *freeze* atau macet saat memuat data.

## ✨ Fitur Utama
1. **Daftar & Detail Post (GET):** Menampilkan semua post dalam bentuk tabel dan memuat detail lengkap (termasuk komentar) di panel samping saat baris tabel diklik.
2. **Tambah Post (POST):** Form input untuk menambahkan post baru dengan penanganan status respons dari server.
3. **Edit Post (PUT):** Mengubah data post yang sudah ada langsung melalui API.
4. **Hapus Post (DELETE):** Menghapus data post (beserta komentarnya/cascade) dengan dialog konfirmasi.
5. **Asynchronous API Calls:** Menerapkan `QThread` untuk semua interaksi HTTP.
6. **State & Error Handling:** Menampilkan indikator status *Loading / Ready*, serta menangani error validasi dari server (contoh: status 422 jika *Slug* tidak unik) maupun error koneksi (*timeout/connection error*).

## 🛠️ Teknologi yang Digunakan
* **Bahasa:** Python 3
* **GUI Framework:** PySide6
* **HTTP Client:** Requests

## 📸 Screenshot Antarmuka

*(Pastikan file gambar screenshot Anda satu folder dengan README ini dan bernama `screenshot.png`)*

![Tampilan Aplikasi Post Manager](screenshot.png)

## 🚀 Cara Menjalankan Aplikasi
1. Pastikan library `PySide6` dan `requests` sudah terinstal:
   ```bash
   pip install PySide6 requests
