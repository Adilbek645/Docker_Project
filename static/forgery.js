let selectedMaterials = {
    'Лезвие': null,
    'Гарда': null,
    'Рукоять': null
};

let game_score = 0;

function blade_minigame() {
    let score = 0;
    let timeLeft = 10; // 10 seconds for the minigame
    const interval = setInterval(() => {
        if (timeLeft <= 0) {
            clearInterval(interval);
            alert("Время вышло! Ваш результат: " + score);
            game_score += score;
            document.querySelector('.minigame_blade').innerHTML = `<p>Ваш результат: ${score}</p>`;
            return;
        }
        
        // Simulate a random event that increases the score
        if (Math.random() < 0.5) { // 50% chance to increase score
            score += Math.floor(Math.random() * 34) + 1; // Random score between 1 and 10
        }
        
        timeLeft--;
    }, 1000);
}

function guard_minigame() {
    let score = 0;
    let timeLeft = 10; // 10 seconds for the minigame
    const interval = setInterval(() => {
        if (timeLeft <= 0) {
            clearInterval(interval);
            alert("Время вышло! Ваш результат: " + score);
            game_score += score;
            document.querySelector('.minigame_guard').innerHTML = `<p>Ваш результат: ${score}</p>`;
            return;
        }
        
        // Simulate a random event that increases the score
        if (Math.random() < 0.5) { // 50% chance to increase score
            score += Math.floor(Math.random() * 33) + 1; // Random score between 1 and 10
        }
        
        timeLeft--;
    }, 1000);
}

function handle_minigame() {
    let score = 0;
    let timeLeft = 10; // 10 seconds for the minigame
    const interval = setInterval(() => {
        if (timeLeft <= 0) {
            clearInterval(interval);
            alert("Время вышло! Ваш результат: " + score);
            game_score += score;
            document.querySelector('.minigame_handle').innerHTML = `<p>Ваш результат: ${score}</p>`;
            return;
        }
        
        // Simulate a random event that increases the score
        if (Math.random() < 0.5) { // 50% chance to increase score
            score += Math.floor(Math.random() * 33) + 1; // Random score between 1 and 10
        }
        
        timeLeft--;
    }, 1000);
}


let selectedMaterialCards = {
    'Лезвие': null,
    'Гарда': null,
    'Рукоять': null
};

function selectMaterial(name, category, imageUrl, cardId) {
    if (selectedMaterialCards[category]) {
        let oldCard = document.getElementById(selectedMaterialCards[category]);
        if (oldCard) oldCard.style.display = 'block'; // Возвращаем старый материал в инвентарь
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
    if (overlay) overlay.style.display = 'flex';

    let audio = new Audio('/static/sound/freesound_community-anvil-hit-1-103967.mp3');
    // первый удар сразу, затем в цикле
    audio.play().catch(e => console.log("Sound error: ", e));
    let forgeInterval = setInterval(() => {
        let hitSound = audio.cloneNode();
        hitSound.volume = 0.5;
        hitSound.play().catch(e => console.log(e));
    }, 500);

    game_score = 0;
    blade_minigame();
    guard_minigame();
    handle_minigame();
    
    
    setTimeout(() => {
        clearInterval(forgeInterval);
        if (overlay) overlay.style.display = 'none';
        sendForgeRequest();
    }, 11000);
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
            alert("Вы успешно выковали меч! Его цена: " + data.price + " 🪙");
            window.location.href = "/inventory";
        } else {
            alert("Ошибка: " + data.error);
        }
    })
    .catch(error => console.error("Ошибка:", error));
}

