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
    if (newCard) newCard.style.display = 'none'; // Скрываем выбранный материал из инвентаря
    
    let slotId = '';
    if (category === 'Лезвие') slotId = 'slot-blade';
    if (category === 'Гарда') slotId = 'slot-guard';
    if (category === 'Рукоять') slotId = 'slot-handle';
    
    let slot = document.getElementById(slotId);
    slot.innerHTML = `<img src="${imageUrl}">`;
    slot.setAttribute('data-placeholder', ''); // Убираем фоновый текст
}

function unselectMaterial(slotElement, category) {
    if (!selectedMaterials[category]) return; // Ничего не выбрано
    
    if (selectedMaterialCards[category]) {
        let card = document.getElementById(selectedMaterialCards[category]);
        if (card) card.style.display = 'block'; // Возвращаем в инвентарь
    }
    
    selectedMaterials[category] = null;
    selectedMaterialCards[category] = null;
    
    slotElement.innerHTML = '';
    slotElement.setAttribute('data-placeholder', slotElement.getAttribute('data-default')); // Возвращаем текст
}

function forgeSword() {
    if (!selectedMaterials['Лезвие'] || !selectedMaterials['Гарда'] || !selectedMaterials['Рукоять']) {
        alert("Выберите все 3 компонента (Лезвие, Гарду и Рукоять)!");
        return;
    }

    game_score = 0; // Сбрасываем очки перед новой ковкой
    blade_minigame();
    guard_minigame();
    handle_minigame();
    
    // Wait for the minigames to finish before proceeding
    setTimeout(() => {
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

