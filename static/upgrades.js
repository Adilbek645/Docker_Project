function upgradeForge(newForgeLevel, cost){
    fetch('/upgrade_buy', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            new_forge_level: newForgeLevel,
            cost: cost
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            document.getElementById('gold-display').innerText = data.new_gold;
            document.getElementById('forge-level-display').innerText = data.new_forge_level;
            console.log("Успешное улучшение кузницы: " + data.new_forge_level);
            alert("Кузня успешно улучшена до уровня " + data.new_forge_level + "!");
        } else {
            alert("Кузнец говорит: " + data.error);
        }
    })
    .catch(error => {
        console.error("Ошибка сети:", error);
    });
}