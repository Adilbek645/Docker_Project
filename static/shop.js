function buyItem(materialName, price, requiredLevel) {
    // Простейшая проверка на фронтенде перед отправкой запроса
    // Золото берем из HTML текста
    let currentGold = parseInt(document.getElementById('gold-display').innerText);
    
    if (currentGold < price) {
        alert("Не хватает золота!");
        return;
    }

    // Отправляем запрос на наш Flask сервер
    fetch('/api/shop/buy', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            material_name: materialName,
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            // Обновляем количество золота на экране без перезагрузки страницы
            document.getElementById('gold-display').innerText = data.gold_left;
            
            // Простейший 8-битный звуковой эффект (можно заменить на реальный аудио файл)
            console.log("Успешная покупка: " + materialName);
        } else {
            // Показываем ошибку от сервера (например, если не хватает уровня кузни)
            alert("Ошибка: " + data.error);
        }
    })
    .catch(error => {
        console.error("Ошибка сети:", error);
    });
}
