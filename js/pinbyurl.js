window.addEventListener('load', function() {
    // Pastikan variabel map global tersedia dari index.html
    if (typeof map === 'undefined' || !map) {
        console.warn("Map object not found in pinbyurl.js");
        return;
    }

    // Ambil parameter dari URL
    var urlParams = new URLSearchParams(window.location.search);
    var fid = urlParams.get('fid');
    var hash = window.location.hash;

    // Logika: Jika ada ?fid=... DAN ada hash #zoom/lat/lng
    if (fid && hash) {
        // Parsing hash. Format yang diharapkan: #zoom/lat/lng
        // Contoh: #14/-6.9681/108.6830
        var parts = hash.replace('#', '').split('/');

        if (parts.length >= 3) {
            var lat = parseFloat(parts[1]);
            var lng = parseFloat(parts[2]);

            // Validasi apakah lat dan lng adalah angka yang valid
            if (!isNaN(lat) && !isNaN(lng)) {
                // Buat marker circle
                var highlightCircle = L.circleMarker([lat, lng], {
                    radius: 12,             // Ukuran radius lingkaran
                    color: '#FF0000',       // Warna border (Merah)
                    weight: 3,              // Ketebalan border
                    fillColor: '#FFFF00',   // Warna isi (Kuning)
                    fillOpacity: 0.5        // Transparansi isi
                }).addTo(map);

                // Pastikan marker berada di urutan paling atas (z-index visual)
                highlightCircle.bringToFront();
            }
        }
    }
});
