/**
 * leaflet-url-search.js
 * Fitur untuk mencari dan menyorot objek peta berdasarkan parameter URL.
 * Contoh penggunaan URL: index.html?fid=1001
 */

(function() {
    // Fungsi helper untuk mengambil nilai parameter dari URL
    function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        var results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }

    /**
     * Fungsi utama pencarian
     * @param {L.Map} mapObj - Objek peta Leaflet
     * @param {L.Layer} targetLayer - Layer GeoJSON tempat pencarian dilakukan
     * @param {String} urlParamName - Nama parameter di URL (contoh: 'fid')
     * @param {String} featurePropertyName - Nama properti di data GeoJSON (contoh: 'fid')
     * @param {Object} options - Opsi tambahan untuk marker (opsional)
     */
    window.searchAndHighlightByUrl = function(mapObj, targetLayer, urlParamName, featurePropertyName, options) {
        var paramValue = getUrlParameter(urlParamName);
        
        // Jika tidak ada parameter di URL, hentikan proses
        if (!paramValue) return;

        var found = false;

        // Iterasi setiap fitur di layer
        targetLayer.eachLayer(function(layer) {
            if (found) return; // Optimasi: berhenti jika sudah ketemu

            var props = layer.feature.properties;
            
            // Cek apakah properti fitur ada dan nilainya cocok
            // Menggunakan String() untuk memastikan perbandingan teks vs angka tetap jalan
            if (props && String(props[featurePropertyName]) === String(paramValue)) {
                
                // 1. Zoom ke lokasi fitur
                if (layer.getBounds) {
                    // Untuk Polygon/Line
                    var bounds = layer.getBounds();
                    if (bounds.isValid()) {
                        mapObj.fitBounds(bounds);
                    }
                } else if (layer.getLatLng) {
                    // Untuk Point
                    mapObj.setView(layer.getLatLng(), 19);
                }

                // 2. Buka Popup (jika layer memiliki popup)
                if (layer.openPopup) {
                    layer.openPopup();
                }

                // 3. Sorot Fitur (Highlight)
                // Kita coba gunakan fungsi highlightFeature bawaan dari no-cache.html jika ada
                if (typeof highlightFeature === 'function') {
                    // Simulasi event object agar kompatibel dengan fungsi highlightFeature yang ada
                    highlightFeature({ target: layer });
                } else {
                    // Fallback style jika fungsi highlightFeature tidak tersedia
                    if (layer.setStyle) {
                        layer.setStyle({
                            color: 'rgba(255, 255, 0, 1.00)', // Kuning terang
                            weight: 5,
                            opacity: 1,
                            fillOpacity: 0.7
                        });
                    }
                }

                 // 4. Tambahkan Marker/Circle jika ada di options
                if (options && options.marker && options.marker.circle) {
                    var centerLatLng;
                    if (layer.getLatLng) {
                        centerLatLng = layer.getLatLng();
                    } else if (layer.getBounds) {
                        centerLatLng = layer.getBounds().getCenter();
                    }

                    if (centerLatLng) {
                        var circleOpts = options.marker.circle;
                        var highlightCircle = L.circleMarker(centerLatLng, circleOpts).addTo(mapObj);
                        highlightCircle.bringToFront(); // Posisi index paling atas
                    }
                }

                found = true;
                console.log("Fitur ditemukan: " + featurePropertyName + " = " + paramValue);
            }
        });

        if (!found) {
            console.warn("Fitur dengan " + featurePropertyName + " = " + paramValue + " tidak ditemukan.");
        }
    };
})();
