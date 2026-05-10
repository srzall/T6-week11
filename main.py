# Samsul Rizal
# F1D02310025


import sys
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, 
    QMessageBox, QHeaderView, QFrame, QTextEdit, QDialog, 
    QFormLayout, QLineEdit, QComboBox
)
from PySide6.QtCore import QThread, Signal, Qt

BASE_URL = "https://api.pahrul.my.id/api/posts"

class ApiWorker(QThread):
    """Menjalankan request HTTP di thread terpisah dari UI utama."""
    finished = Signal(object) # Mengirim data sukses (dict/list)
    error = Signal(str)       # Mengirim pesan error
    
    def __init__(self, method, url, data=None):
        super().__init__()
        self.method = method
        self.url = url
        self.data = data

    def run(self):
        try:
            # Simulasi state handling
            if self.method == 'GET':
                res = requests.get(self.url, timeout=10)
            elif self.method == 'POST':
                res = requests.post(self.url, json=self.data, timeout=10)
            elif self.method == 'PUT':
                res = requests.put(self.url, json=self.data, timeout=10)
            elif self.method == 'DELETE':
                res = requests.delete(self.url, timeout=10)

            # Handling Response Code
            if res.status_code in (200, 201):
                self.finished.emit(res.json())
            elif res.status_code == 204: # Biasanya DELETE mengembalikan 204 No Content
                self.finished.emit({"message": "Berhasil dihapus"})
            elif res.status_code == 422: # Error Validasi Unik (Slug)
                pesan_error = res.json().get('message', 'Validasi gagal, pastikan Slug unik!')
                self.error.emit(f"Error 422: {pesan_error}")
            else:
                self.error.emit(f"Error {res.status_code}: {res.text}")
                
        except requests.exceptions.Timeout:
            self.error.emit("Request Timeout! Server tidak merespon.")
        except requests.exceptions.ConnectionError:
            self.error.emit("Koneksi Error! Gagal terhubung ke API Pahrul.")
        except Exception as e:
            self.error.emit(f"Terjadi Kesalahan System: {str(e)}")


class PostFormDialog(QDialog):
    def __init__(self, parent=None, post_data=None):
        super().__init__(parent)
        self.setWindowTitle("Form Post")
        self.setFixedSize(400, 350)
        
        self.setup_ui()
        if post_data:
            self.set_data(post_data)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.in_title = QLineEdit()
        self.in_author = QLineEdit()
        self.in_slug = QLineEdit()
        self.in_slug.setPlaceholderText("Harus unik (contoh: post-pertama)")
        
        self.in_status = QComboBox()
        self.in_status.addItems(["draft", "published", "archived"])
        
        self.in_body = QTextEdit()
        self.in_body.setFixedHeight(100)

        form.addRow("Title:", self.in_title)
        form.addRow("Author:", self.in_author)
        form.addRow("Slug:", self.in_slug)
        form.addRow("Status:", self.in_status)
        form.addRow("Body:", self.in_body)

        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Simpan")
        self.btn_cancel = QPushButton("Batal")
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(form)
        layout.addLayout(btn_layout)

    def get_data(self):
        return {
            "title": self.in_title.text(),
            "author": self.in_author.text(),
            "slug": self.in_slug.text(),
            "status": self.in_status.currentText(),
            "body": self.in_body.toPlainText()
        }

    def set_data(self, data):
        self.in_title.setText(data.get("title", ""))
        self.in_author.setText(data.get("author", ""))
        self.in_slug.setText(data.get("slug", ""))
        self.in_status.setCurrentText(data.get("status", "draft"))
        self.in_body.setText(data.get("body", ""))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("API Post Manager")
        self.resize(950, 600)
        self.setup_ui()
        self.muat_data_tabel() # Load data awal

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # --- BAGIAN KIRI: TABEL & TOMBOL ---
        kiri_layout = QVBoxLayout()
        
        # Header & Status Label
        header_layout = QHBoxLayout()
        judul = QLabel("<b>Daftar Posts</b>")
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet("color: gray;")
        header_layout.addWidget(judul)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_status)
        kiri_layout.addLayout(header_layout)

        # Tabel
        self.tabel = QTableWidget()
        self.tabel.setColumnCount(4)
        self.tabel.setHorizontalHeaderLabels(["ID", "Title", "Author", "Status"])
        self.tabel.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabel.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabel.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabel.itemSelectionChanged.connect(self.on_table_selection)
        kiri_layout.addWidget(self.tabel)

        # Tombol Aksi
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_add = QPushButton("➕ Tambah")
        self.btn_edit = QPushButton("✏ Edit")
        self.btn_delete = QPushButton("🗑 Hapus")
        
        # Default Edit & Hapus mati jika tidak ada baris dipilih
        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)

        self.btn_refresh.clicked.connect(self.muat_data_tabel)
        self.btn_add.clicked.connect(self.tambah_post)
        self.btn_edit.clicked.connect(self.edit_post)
        self.btn_delete.clicked.connect(self.hapus_post)

        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        kiri_layout.addLayout(btn_layout)

        # --- BAGIAN KANAN: DETAIL PANEL ---
        kanan_frame = QFrame()
        kanan_frame.setFixedWidth(350)
        kanan_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 5px;")
        kanan_layout = QVBoxLayout(kanan_frame)
        
        kanan_layout.addWidget(QLabel("<b>🔎 Detail Post & Comments</b>"))
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        kanan_layout.addWidget(self.detail_text)

        # Menggabungkan layout
        main_layout.addLayout(kiri_layout, 2)
        main_layout.addWidget(kanan_frame, 1)

    # --- FUNGSI UI STATE HANDLING ---
    def set_loading(self, text="Loading..."):
        self.lbl_status.setText(f"⏳ {text}")
        self.lbl_status.setStyleSheet("color: orange; font-weight: bold;")
        self.tabel.setEnabled(False) # Kunci UI sementara request berjalan
        
    def set_ready(self, text="Ready"):
        self.lbl_status.setText(text)
        self.lbl_status.setStyleSheet("color: green; font-weight: bold;")
        self.tabel.setEnabled(True)

    def on_table_selection(self):
        """Mengatur tombol aktif/mati dan memuat detail panel."""
        baris = self.tabel.currentRow()
        if baris >= 0:
            self.btn_edit.setEnabled(True)
            self.btn_delete.setEnabled(True)
            id_post = self.tabel.item(baris, 0).text()
            self.muat_detail_post(id_post)
        else:
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.detail_text.clear()

    # --- HTTP GET: AMBIL SEMUA POST ---
    def muat_data_tabel(self):
        self.set_loading("Mengambil data posts...")
        self.worker_get = ApiWorker('GET', BASE_URL)
        self.worker_get.finished.connect(self.on_data_loaded)
        self.worker_get.error.connect(self.on_api_error)
        self.worker_get.start()

    def on_data_loaded(self, data):
        # Struktur response API biasanya list atau dict dengan key 'data'
        posts = data.get('data', []) if isinstance(data, dict) else data
        
        self.tabel.setRowCount(0)
        for post in posts:
            row = self.tabel.rowCount()
            self.tabel.insertRow(row)
            self.tabel.setItem(row, 0, QTableWidgetItem(str(post.get('id', ''))))
            self.tabel.setItem(row, 1, QTableWidgetItem(post.get('title', '')))
            self.tabel.setItem(row, 2, QTableWidgetItem(post.get('author', '')))
            self.tabel.setItem(row, 3, QTableWidgetItem(post.get('status', '')))
        
        self.set_ready("Data berhasil dimuat")

    # --- HTTP GET: AMBIL DETAIL POST ---
    def muat_detail_post(self, id_post):
        self.set_loading(f"Mengambil detail ID {id_post}...")
        url = f"{BASE_URL}/{id_post}"
        self.worker_detail = ApiWorker('GET', url)
        self.worker_detail.finished.connect(self.on_detail_loaded)
        self.worker_detail.error.connect(self.on_api_error)
        self.worker_detail.start()

    def on_detail_loaded(self, data):
        # Ekstrak data dari API
        post = data.get('data', data)
        comments = post.get('comments', [])
        
        # Format tampilan detail
        detail_html = f"""
        <h3>{post.get('title', '')}</h3>
        <b>Author:</b> {post.get('author', '')}<br>
        <b>Status:</b> {post.get('status', '')}<br>
        <b>Slug:</b> {post.get('slug', '')}<br>
        <hr>
        <p>{post.get('body', '')}</p>
        <hr>
        <b>Komentar ({len(comments)}):</b><br>
        """
        for k in comments:
            detail_html += f"• <i>{k.get('commenter_name', 'Anonim')}</i>: {k.get('body', '')}<br>"

        self.detail_text.setHtml(detail_html)
        self.set_ready("Detail dimuat")

    # --- HTTP POST: TAMBAH POST ---
    def tambah_post(self):
        dialog = PostFormDialog(self)
        if dialog.exec():
            data_baru = dialog.get_data()
            self.set_loading("Mengirim post baru...")
            self.worker_post = ApiWorker('POST', BASE_URL, data_baru)
            self.worker_post.finished.connect(self.on_post_added)
            self.worker_post.error.connect(self.on_api_error)
            self.worker_post.start()

    def on_post_added(self, response):
        post = response.get('data', response)
        id_baru = post.get('id', 'Unknown')
        QMessageBox.information(self, "Sukses", f"Post berhasil ditambahkan!\nID dari server: {id_baru}")
        self.muat_data_tabel()

    # --- HTTP PUT: EDIT POST ---
    def edit_post(self):
        baris = self.tabel.currentRow()
        if baris < 0: return
        
        id_post = self.tabel.item(baris, 0).text()
        url = f"{BASE_URL}/{id_post}"
        
        # Ambil data dari tabel untuk pre-fill (ideal: tunggu GET detail, tapi ini mempercepat UI)
        post_lama = {
            "title": self.tabel.item(baris, 1).text(),
            "author": self.tabel.item(baris, 2).text(),
            "status": self.tabel.item(baris, 3).text(),
        }

        dialog = PostFormDialog(self, post_lama)
        if dialog.exec():
            data_update = dialog.get_data()
            self.set_loading(f"Mengupdate ID {id_post}...")
            self.worker_put = ApiWorker('PUT', url, data_update)
            self.worker_put.finished.connect(self.on_post_updated)
            self.worker_put.error.connect(self.on_api_error)
            self.worker_put.start()

    def on_post_updated(self, response):
        QMessageBox.information(self, "Sukses", "Data post berhasil diupdate!")
        self.muat_data_tabel()

    # --- HTTP DELETE: HAPUS POST ---
    def hapus_post(self):
        baris = self.tabel.currentRow()
        if baris < 0: return
        
        id_post = self.tabel.item(baris, 0).text()
        konfirmasi = QMessageBox.question(
            self, "Konfirmasi Delete", 
            f"Yakin ingin menghapus Post ID {id_post}?\nSemua komentar terkait akan ikut terhapus (Cascade)!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if konfirmasi == QMessageBox.StandardButton.Yes:
            self.set_loading(f"Menghapus ID {id_post}...")
            url = f"{BASE_URL}/{id_post}"
            self.worker_del = ApiWorker('DELETE', url)
            self.worker_del.finished.connect(self.on_post_deleted)
            self.worker_del.error.connect(self.on_api_error)
            self.worker_del.start()

    def on_post_deleted(self, response):
        QMessageBox.information(self, "Sukses", "Data post beserta komentarnya berhasil dihapus!")
        self.muat_data_tabel()
        self.detail_text.clear()

    # --- GLOBAL ERROR HANDLING ---
    def on_api_error(self, pesan):
        self.set_ready("Error Server")
        QMessageBox.warning(self, "API Error", pesan)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Styling standar agar rapi
    app.setStyleSheet("""
        QMainWindow { background-color: #ecf0f1; }
        QPushButton { padding: 6px; background-color: #3498db; color: white; border-radius: 4px; font-weight:bold; }
        QPushButton:hover { background-color: #2980b9; }
        QPushButton:disabled { background-color: #bdc3c7; }
        QTableWidget { background-color: white; border: 1px solid #ccc; }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())