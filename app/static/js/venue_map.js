function initVenueMap(venueName, venueAddress) {
    if (typeof ymaps === 'undefined') {
        console.error('Яндекс.Карты не загрузились');
        return;
    }
    
    ymaps.ready(function() {
        // Геокодирование — поиск координат по адресу
        ymaps.geocode(venueAddress, {
            results: 1
        }).then(function(res) {
            var firstGeoObject = res.geoObjects.get(0);
            var coords = firstGeoObject.geometry.getCoordinates();
            
            var map = new ymaps.Map("venue-map", {
                center: coords,
                zoom: 16,
                controls: ['zoomControl', 'fullscreenControl']
            });
            
            var placemark = new ymaps.Placemark(coords, {
                balloonContent: "<b>" + venueName + "</b><br/>" + venueAddress,
                iconContent: venueName
            }, {
                preset: 'islands#redStretchyIcon',
                balloonMaxWidth: 200
            });
            
            map.geoObjects.add(placemark);
            
            // Добавляем кнопку для построения маршрута (опционально)
            var routeButton = new ymaps.control.Button({
                data: { content: "Проложить маршрут" },
                options: { maxWidth: 160 }
            });
            
            routeButton.events.add('click', function() {
                window.open('https://yandex.ru/maps/?mode=routes&rtext=~' + coords.join(','));
            });
            
            map.controls.add(routeButton, { float: 'right' });
            
        }).catch(function(err) {
            console.error('Ошибка геокодирования:', err);
            document.getElementById('venue-map').innerHTML = 
                '<div class="alert alert-warning h-100 d-flex align-items-center justify-content-center">' +
                '⚠️ Не удалось загрузить карту по адресу: ' + venueAddress +
                '</div>';
        });
    });
}