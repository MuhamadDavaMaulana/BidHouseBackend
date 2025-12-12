# BidHouse Auction API (FastAPI)

Proyek ini adalah implementasi *backend* API untuk platform lelang modern, dikembangkan menggunakan **FastAPI** dan **SQLAlchemy (ORM)**. Fokus utama adalah pada integritas data waktu (UTC) dan alur autentikasi JWT standar.

---

## Status Deployment (Nilai Plus)

API ini sudah *live* dan dapat diuji secara langsung melalui URL publik.

| Deskripsi | Tautan |
| :--- | :--- |
| **Repository Source Code** | `https://github.com/MuhamadDavaMaulana/BidHouseBackend.git` |
| **Website Hasil Deploy** | `https://bidhousebackend.onrender.com` |
| **Dokumentasi API (Swagger UI)** | `https://bidhousebackend.onrender.com/docs` |

---

## Struktur Proyek

API ini mengadopsi struktur modular untuk pemisahan tanggung jawab yang jelas:

| File/Direktori | Deskripsi |
| :--- | :--- |
| `app/main.py` | Titik masuk utama aplikasi, konfigurasi API, dan pendaftaran *router*. |
| `app/database.py` | Konfigurasi koneksi database (SQLite), dan definisi *engine* database. |
| `app/models.py` | Definisi *Object-Relational Mapping* (ORM) untuk tabel database (SQLAlchemy Models). |
| `app/schemas.py` | Skema data Pydantic untuk validasi *request/response* API. |
| `app/crud.py` | Lapisan Logika Interaksi Database murni (Create, Read, Update, Delete). |
| `app/auth.py` | Implementasi keamanan: JWT (JSON Web Tokens) dan Hashing Password (Argon2). |
| `app/routers/` | **Definisi *Endpoints*:** `users.py`, `items.py`, `bids.py`. |
| `requirements.txt` | Daftar dependensi Python yang diperlukan untuk menjalankan proyek. |

---

## Panduan Menjalankan Proyek Secara Lokal

### 1. Persyaratan Sistem
* Python **3.9+**
* Package Manager: `pip`

### 2. Langkah-Langkah Setup

1.  **Kloning Repositori:**
    ```bash
    git clone [https://github.com/MuhamadDavaMaulana/BidHouseBackend.git](https://github.com/MuhamadDavaMaulana/BidHouseBackend.git)
    cd BidHouseBackend
    ```

2.  **Buat dan Aktifkan Virtual Environment:**
    ```bash
    python -m venv venv
    # Linux/macOS
    source venv/bin/activate
    # Windows (PowerShell)
    .\venv\Scripts\activate
    ```

3.  **Instal Dependensi:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Inisialisasi Database (SQLite):**
    Perintah ini akan membuat file `bidhouse.db` dan semua skema tabel yang diperlukan.
    ```bash
    python -c "from app.database import init_db; init_db()"
    ```

5.  **Jalankan Server API:**
    ```bash
    uvicorn app.main:app --reload
    ```
    Server akan aktif di: `http://127.0.0.1:8000/`

---

## Akses dan Otorisasi API (Menggunakan Swagger UI)

Akses dokumentasi interaktif (Swagger UI) melalui: **`http://127.0.0.1:8000/docs`**.

#### 1. Mendapatkan Token Akses (Login)

Token diperlukan untuk mengakses *endpoint* terproteksi.

* Akses *endpoint* **`POST /api/token`**.
* Masukkan `username` dan `password` (*gunakan kredensial pengguna yang sudah terdaftar*).
* Salin nilai string **`access_token`** dari respons JSON.

#### 2. Otorisasi Otomatis di Swagger UI

Setelah mendapatkan token, masukkan ke sistem otorisasi Swagger:

* Klik tombol **"Authorize"** (biasanya di kanan atas halaman).
* Tempelkan **hanya nilai token** yang Anda salin ke dalam *field* yang disediakan.
* Klik **Authorize**.

Setelah otorisasi, semua permintaan yang Anda eksekusi melalui Swagger UI akan secara otomatis menyertakan *Header* `Authorization: Bearer <token>`.

---

## Desain & Keputusan Arsitektur

Saya mengadopsi struktur aplikasi yang modular dengan pemisahan tanggung jawab yang ketat (Model, CRUD, Router) untuk skalabilitas dan pemeliharaan.

### Integritas dan Keamanan Kritis

1.  **Integritas Waktu (UTC-Aware):**
    * Semua waktu lelang (`start_time`, `end_time`) dan waktu *bid* dicatat dan dibandingkan menggunakan format **UTC Timezone-Aware**.
    * **Tujuan:** Mengeliminasi *bug* perbandingan waktu yang fatal, memastikan bahwa lelang berakhir pada waktu yang tepat secara global.

2.  **Keamanan Password (Argon2):**
    * Saya menggunakan **Argon2** sebagai algoritma *hashing* password.
    * **Tujuan:** Argon2 adalah standar industri modern yang direkomendasikan dan lebih tahan terhadap serangan *brute-force* daripada algoritma yang lebih lama (seperti bcrypt).

3.  **Otentikasi (JWT + Header):**
    * Token akses (JWT) dikelola dengan masa aktif **30 menit** dan dikirim via *Header* standar API.

### Modularitas dan Kejelasan Kode

* **CRUD Layer:** Semua logika interaksi dengan database terisolasi di `app/crud.py`, memastikan *router* tetap bersih dan hanya menangani validasi *request* dan status HTTP.
* **Dependencies FastAPI:** Memanfaatkan *Dependency Injection* (`Depends()`) untuk mengelola sesi database dan verifikasi pengguna, menjaga kode *endpoint* tetap deklaratif.