let selectedMaterials = {
    'Лезвие': null,
    'Гарда': null,
    'Рукоять': null
};

function selectMaterial(name, category, imageUrl) {
    selectedMaterials[category] = name;
    
    let slotId = '';
    if (category === 'Лезвие') slotId = 'slot-blade';
    if (category === 'Гарда') slotId = 'slot-guard';
    if (category === 'Рукоять') slotId = 'slot-handle';
    
    let slot = document.getElementById(slotId);
    slot.innerHTML = `<img src="${imageUrl}" style="width: 64px; height: 64px; image-rendering: pixelated;">`;
}

function forgeSword() {
    let swordName = document.getElementById('sword-name').value;
    
    if (!selectedMaterials['Лезвие'] || !selectedMaterials['Гарда'] || !selectedMaterials['Рукоять']) {
        alert("Выберите все 3 компонента (Лезвие, Гарду и Рукоять)!");
        return;
    }
    
    fetch('/forge_sword', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            blade: selectedMaterials['Лезвие'],
            guard: selectedMaterials['Гарда'],
            handle: selectedMaterials['Рукоять'],
            sword_name: swordName || "Безымянный Клинок"
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
