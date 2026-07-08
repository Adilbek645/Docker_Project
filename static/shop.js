function shop_buy(materialName, category, price, requiredLevel) {
    fetch('/shop_buy', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            material_name: materialName,
            material_category: category,
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            document.getElementById('gold-display').innerText = data.gold_left;
            console.log("Успешная покупка: " + materialName);
        } else {
            alert("Торговец говорит: " + data.error);
        }
    })
    .catch(error => {
        console.error("Ошибка сети:", error);
    });
}

