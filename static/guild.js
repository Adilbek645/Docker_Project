function submitSword(swordId) {
    fetch('/guild_submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            sword_id: swordId
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            document.getElementById('rep-display').innerText = data.reputation;
            
            const swordCard = document.getElementById('sword-' + swordId);
            if (swordCard) {
                swordCard.remove();
            }
            console.log("Меч успешно сдан!");
        } else {
            alert("Ошибка: " + data.error);
        }
    })
    .catch(error => {
        console.error("Ошибка сети:", error);
    });
}

function startExpedition(tier) {
    fetch('/guild_expedition', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            tier: tier
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            alert("Ваши наемники вернулись из экспедиции!\nОни нашли: " + data.material_name + " (" + data.rarity + ")");
            // Перезагрузим страницу чтобы обновить золото и кнопки
            window.location.reload();
        } else {
            alert("Ошибка: " + data.error);
        }
    })
    .catch(error => {
        console.error("Ошибка сети:", error);
    });
}
