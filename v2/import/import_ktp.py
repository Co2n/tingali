import os
import csv
import urllib.parse
from datetime import datetime
from supabase import create_client, Client

# 1. KREDENSIAL SUPABASE
url = "https://ftlzqrwrlivgszomwhhb.supabase.co"
key = "aeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ0bHpxcndybGl2Z3N6b213aGhiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzA0NzgwMywiZXhwIjoyMDg4NjIzODAzfQ._cpBfS42rnPzdI0eRQfYU2KzCG4h2uepEv095gIyS7E"
supabase: Client = create_client(url, key)

nama_tabel = "dbKtp"
nama_bucket = "ktp"
file_csv = "data_ktp.csv" # Sesuaikan dengan nama file CSV Anda

print(f"Membaca file {file_csv}...\n")

try:
    with open(file_csv, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            nik = row['nik']
            local_path = row['file']
            url_file_baru = None # Default kosong jika file gagal diupload
            
            print(f"Memproses NIK: {nik} - {row['nama']}...")
            
            # 2. PROSES UPLOAD FILE (Jika path tersedia)
            if local_path:
                local_path = local_path.strip(" '\"")
                local_path = urllib.parse.unquote(local_path)
                local_path = os.path.normpath(local_path)
                
                if os.path.exists(local_path):
                    try:
                        nama_asli, ext = os.path.splitext(local_path)
                        if not ext: ext = ".jpg"
                            
                        # Format nama file: ktp_[nik]_[waktu].jpg
                        datenow = datetime.now().strftime("%Y%m%d_%H%M%S")
                        new_file_name = f"ktp_{nik}_{datenow}{ext}"
                        
                        # Upload ke Supabase Storage
                        with open(local_path, 'rb') as img_file:
                            supabase.storage.from_(nama_bucket).upload(new_file_name, img_file, {"upsert": "true"})
                        
                        # Dapatkan Public URL
                        url_file_baru = supabase.storage.from_(nama_bucket).get_public_url(new_file_name)
                        print(f"  -> Upload Foto Sukses!")
                        
                    except Exception as e:
                        print(f"  -> Gagal upload foto NIK {nik}. Error: {e}")
                else:
                    print(f"  -> Peringatan: File fisik tidak ditemukan di laptop ({local_path})")
            
            # 3. PERSIAPKAN DATA UNTUK DATABASE
            # Memasukkan semua kolom dari CSV ke dalam dictionary
            data_db = {
                "nik": nik,
                "nama": row['nama'],
                "gender": row['gender'],
                "tgl_lahir": row['tgl_lahir'], # Pastikan di CSV formatnya YYYY-MM-DD
                "alamat": row['alamat'],
                "desa": row['desa'],
                "kecamatan": row['kecamatan'],
                "file": url_file_baru # Menggunakan URL baru, bukan path lokal lagi
            }
            
            # 4. INSERT / UPSERT KE TABEL
            # Kita gunakan upsert: Jika NIK sudah ada, data akan di-update. Jika belum, data di-insert.
            # Ini sangat aman jika Anda harus me-restart script di tengah jalan.
            try:
                supabase.table(nama_tabel).upsert(data_db).execute()
                print(f"  -> Data {nik} berhasil masuk ke database!\n")
            except Exception as e:
                print(f"  -> Gagal insert data NIK {nik}. Error: {e}\n")

except FileNotFoundError:
    print(f"ERROR: File CSV '{file_csv}' tidak ditemukan di folder ini.")
    
print("PROSES SELESAI!")

# Menggunakan upsert bukan insert: Jika tiba-tiba koneksi internet Anda terputus dan Anda harus menjalankan ulang scriptnya, 
# data yang sudah masuk tidak akan error atau dobel. Sistem otomatis menimpa/memperbarui data berdasarkan NIK.