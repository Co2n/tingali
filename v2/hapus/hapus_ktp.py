# Update keynya dulu abrang kali salah > a
# cara jalaninnya > python hapus_ktp.py
import csv
import urllib.parse
from supabase import create_client, Client

# 1. KREDENSIAL SUPABASE
url = "https://ftlzqrwrlivgszomwhhb.supabase.co"
key = "aeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ0bHpxcndybGl2Z3N6b213aGhiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzA0NzgwMywiZXhwIjoyMDg4NjIzODAzfQ._cpBfS42rnPzdI0eRQfYU2KzCG4h2uepEv095gIyS7E"
supabase: Client = create_client(url, key)

nama_tabel = "ONLINE_09_03_2026_2000"
nama_bucket = "ktp"
file_csv = "daftar_fid.csv" # Pastikan file ini ada di folder yang sama

print(f"Membaca file {file_csv}...\n")

# 2. MEMBACA FID DARI CSV
target_fids = []
try:
    with open(file_csv, mode='r', encoding='utf-8-sig') as f:
        # Gunakan delimiter=';' jika CSV Anda disimpan dari Excel versi Indonesia
        # Jika pakai koma biasa, hapus parameter delimiter ini
        reader = csv.DictReader(f, delimiter=';') 
        for row in reader:
            target_fids.append(row['fid'])
except FileNotFoundError:
    print(f"ERROR: File {file_csv} tidak ditemukan di folder ini.")
    exit()

print(f"Ditemukan {len(target_fids)} fid untuk dihapus. Memulai proses...\n")

# 3. PROSES PENGHAPUSAN BERDASARKAN FID
for fid in target_fids:
    print(f"Memproses fid: {fid}...")
    
    # Ambil data HANYA untuk fid tersebut
    response = supabase.table(nama_tabel).select("ktp").eq("fid", fid).execute()
    
    # Cek apakah fid ada di database
    if not response.data:
        print(f"  -> LEWATI: fid {fid} tidak ditemukan di database.")
        continue
        
    url_ktp = response.data[0]['ktp']
    
    # Cek apakah kolom ktp sudah kosong
    if not url_ktp:
        print(f"  -> LEWATI: Kolom KTP untuk fid {fid} sudah kosong.")
        continue

    try:
        # Ekstrak nama file dari URL
        file_name = url_ktp.split('/')[-1]
        file_name = urllib.parse.unquote(file_name) # Bersihkan karakter %20 dll
        
        # Hapus file dari Bucket Storage
        # Catatan: Jika file tidak ada di bucket (sudah terhapus manual), fungsi ini biasanya tidak akan error
        # tapi tetap mengembalikan status sukses
        supabase.storage.from_(nama_bucket).remove([file_name])
        
        # Kosongkan kolom 'ktp' di tabel
        supabase.table(nama_tabel).update({"ktp": None}).eq("fid", fid).execute()
        
        print(f"  -> Sukses! File '{file_name}' dihapus dan data dikosongkan.")
        
    except Exception as e:
        print(f"  -> Gagal memproses fid {fid}. Error: {e}")

print("\nPROSES PENGHAPUSAN SPESIFIK SELESAI!")