let selectedMaterials = {
    'Лезвие': null,
    'Гарда': null,
    'Рукоять': null
};

let game_score = 0;

let selectedMaterialCards = {
    'Лезвие': null,
    'Гарда': null,
    'Рукоять': null
};

function selectMaterial(name, category, imageUrl, cardId) {
    if (selectedMaterialCards[category]) {
        let oldCard = document.getElementById(selectedMaterialCards[category]);
        if (oldCard) oldCard.style.display = 'block';
    }

    selectedMaterials[category] = name;
    selectedMaterialCards[category] = cardId;
    
    let newCard = document.getElementById(cardId);
    if (newCard) newCard.style.display = 'none'; 
    
    let slotId = '';
    if (category === 'Лезвие') slotId = 'slot-blade';
    if (category === 'Гарда') slotId = 'slot-guard';
    if (category === 'Рукоять') slotId = 'slot-handle';
    
    let slot = document.getElementById(slotId);
    slot.innerHTML = `<img src="${imageUrl}">`;
    slot.setAttribute('data-placeholder', '');
}

function unselectMaterial(slotElement, category) {
    if (!selectedMaterials[category]) return;
    
    if (selectedMaterialCards[category]) {
        let card = document.getElementById(selectedMaterialCards[category]);
        if (card) card.style.display = 'block';
    }
    
    selectedMaterials[category] = null;
    selectedMaterialCards[category] = null;
    
    slotElement.innerHTML = '';
    slotElement.setAttribute('data-placeholder', slotElement.getAttribute('data-default'));
}

function forgeSword() {
    if (!selectedMaterials['Лезвие'] || !selectedMaterials['Гарда'] || !selectedMaterials['Рукоять']) {
        alert("Выберите все 3 компонента (Лезвие, Гарду и Рукоять)!");
        return;
    }

    let overlay = document.getElementById('forge-animation-overlay');
    let progressText = document.querySelector('.forge-progress-text');
    if (overlay) overlay.style.display = 'flex';

    let final_quality = 0;
    let roll = Math.random() * 100;
    if (roll > 90) final_quality = Math.floor(Math.random() * 10) + 91;
    else if (roll > 70) final_quality = Math.floor(Math.random() * 10) + 81;
    else if (roll > 20) final_quality = Math.floor(Math.random() * 31) + 50;
    else final_quality = Math.floor(Math.random() * 35) + 15;

    game_score = final_quality;
    let current_quality = 0;

    let audio = new Audio('/static/sound/freesound_community-anvil-hit-1-103967.mp3');
    audio.play().catch(e => console.log("Sound error: ", e));
    
    let forgeInterval = setInterval(() => {
        let hitSound = audio.cloneNode();
        hitSound.volume = 0.5;
        hitSound.play().catch(e => console.log(e));
    }, 500);

    setTimeout(() => {
        clearInterval(forgeInterval);
        if (overlay) overlay.style.display = 'none';
        if (progressText) progressText.innerText = `ИДЕТ КОВКА...`;
        sendForgeRequest();
    }, 7000);
}


function sendForgeRequest() {
    let swordName = document.getElementById('sword-name').value;
    
    fetch('/forge_sword', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            blade: selectedMaterials['Лезвие'],
            guard: selectedMaterials['Гарда'],
            handle: selectedMaterials['Рукоять'],
            sword_name: swordName || "Безымянный Клинок",
            game_score: game_score
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            let qualityText = "Обычное (x1.0)";
            if (game_score > 90) qualityText = "Шедевр! (x1.5)";
            else if (game_score > 70) qualityText = "Отличное (x1.3)";
            else if (game_score < 50) qualityText = "С изъяном... (x0.5)";

            alert(`Вы успешно выковали меч!\nКачество: ${game_score}/100 - ${qualityText}\nИтоговая цена: ${data.price} 🪙`);
        } else {
            alert("Ошибка: " + data.error);
        }
    })
    .catch(error => console.error("Ошибка:", error));
}

