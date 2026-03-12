import os
import csv
import urllib.parse  # Tambahkan baris ini
from supabase_auth import datetime
from supabase import create_client, Client

# 1. MASUKKAN KREDENSIAL ANDA DI SINI
url = "https://ftlzqrwrlivgszomwhhb.supabase.co"
key = "aeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ0bHpxcndybGl2Z3N6b213aGhiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzA0NzgwMywiZXhwIjoyMDg4NjIzODAzfQ._cpBfS42rnPzdI0eRQfYU2KzCG4h2uepEv095gIyS7E"
supabase: Client = create_client(url, key)

nama_tabel = "ONLINE_09_03_2026_2000"
nama_bucket = "ktpagree"
file_csv = "daftar_fid.csv" # Sesuaikan dengan nama file CSV Anda

print(f"Membaca file {file_csv}...")

# 2. MEMBACA FID DARI CSV
target_fids = []
try:
    with open(file_csv, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Mengambil nilai dari kolom 'fid'
            target_fids.append(row['fid'])
except FileNotFoundError:
    print(f"ERROR: File {file_csv} tidak ditemukan di folder ini.")
    exit()

print(f"Ditemukan {len(target_fids)} fid untuk diproses. Memulai upload...\n")

# 3. PROSES UPLOAD BERDASARKAN FID
for fid in target_fids:
    # Mengambil data HANYA untuk fid yang sedang di-loop
    response = supabase.table(nama_tabel).select("fid, ktpagree").eq("fid", fid).execute()
    
    # Jika fid tidak ada di database Supabase
    if not response.data:
        print(f"LEWATI: fid {fid} tidak ditemukan di tabel Supabase.")
        continue
        
    baris_data = response.data[0]
    local_path = baris_data['ktpagree']
    
    # Lewati jika path kosong di database
    if not local_path:
        print(f"LEWATI: fid {fid} kolom ktpagree-nya kosong.")
        continue
        
    # Lewati jika sudah berupa URL (sudah pernah sukses terupload)
    if str(local_path).startswith("http"):
        print(f"LEWATI: fid {fid} sudah berupa URL (Selesai sebelumnya).")
        continue
        
    # Membersihkan format path (spasi, URL encoding, kutip)
    local_path = local_path.strip(" '\"")
    local_path = urllib.parse.unquote(local_path)
    local_path = os.path.normpath(local_path)
    
    # ---------------------------------------------------------
    # OPSIONAL: Jika path di DB ternyata relative (hanya nama file),
    # hapus tanda '#' di bawah dan sesuaikan folder utama Anda
    # folder_utama = r"C:\Data_QGIS\Folder_ktpagree"
    # if not os.path.isabs(local_path):
    #     local_path = os.path.join(folder_utama, local_path)
    # ---------------------------------------------------------

    # 4. EKSEKUSI UPLOAD & UPDATE
    if os.path.exists(local_path):
        print(f"Proses ktpagree untuk fid: {fid}...")
        try:
            nama_asli, ext = os.path.splitext(local_path)
            if not ext:
                ext = ".jpg"
                
            datenow = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_file_name = f"ktpagree_{fid}_{datenow}{ext}"
            
            # Upload ke Storage
            with open(local_path, 'rb') as f:
                supabase.storage.from_(nama_bucket).upload(new_file_name, f, {"upsert": "true"})
            
            # Dapatkan URL & Update Database
            public_url = supabase.storage.from_(nama_bucket).get_public_url(new_file_name)
            supabase.table(nama_tabel).update({"ktpagree": public_url}).eq("fid", fid).execute()
            
            print(f"  -> Sukses! URL: {public_url}")
            
        except Exception as e:
            print(f"  -> Gagal memproses fid {fid}. Error: {e}")
    else:
        print(f"LEWATI: File fisik tidak ditemukan untuk fid {fid} -> {local_path}")

print("\nPROSES SELESAI!")