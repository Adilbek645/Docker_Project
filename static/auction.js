function auctionSell(swordId) {
    fetch('/auction_sell', {
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
            document.getElementById('gold-display').innerText = data.new_gold;
            document.getElementById('sword-' + swordId).remove();
            
            alert("Аукционист ударил молотком! Меч продан за " + data.sold_price + " 🪙!");
        } else {
            alert("Ошибка: " + data.error);
        }
    })
    .catch(error => {
        console.error("Ошибка сети:", error);
    });
}
