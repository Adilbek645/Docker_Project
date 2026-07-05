function submitSword(swordId) {
    fetch('/api/guild/submit', {
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
