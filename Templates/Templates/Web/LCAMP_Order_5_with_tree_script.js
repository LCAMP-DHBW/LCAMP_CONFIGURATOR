// --- Globale Variablen ---


// --- Sensor-Form-Skripte ---
function showSensorTab(index) {
    const panels = document.querySelectorAll('.tab-panel');
    const buttons = document.querySelectorAll('.tab-btn');
    panels.forEach((panel, i) => {
        panel.classList.toggle('hidden', i !== index);
    });
    buttons.forEach((btn, i) => btn.classList.toggle('active', i === index));
}



function collectSensors(containerId) {
    const selects = document.querySelectorAll(`#${containerId} select`);
    return Array.from(selects).map(sel => sel.value);
}



async function sendSensors() {
    const sensorData = {
        front: collectSensors("frontSensors"),
        frontAux: document.getElementById('auxSensorFront').value,
        rear: collectSensors("rearSensors"),
        rearAux: document.getElementById('auxSensorRear').value,
        center: collectSensors("centerSensors"),
        centerAux: document.getElementById('auxSensorCenter').value,
        controller: collectSensors("controllerSensors"),
        controllerAux: document.getElementById('auxSensorController').value
    };
    const msg = {
        sender: document.getElementById('sender')?.value || "WebUI",
        command: "SetSensors",
        content: document.getElementById('content')?.value || "",
        type: "setSensors",
        sensorConfiguration: sensorData
    };
    await sendToServer(msg);
}

// --- Server-Kommunikation ---
async function sendCommand() {
    const msg = {
        sender: document.getElementById('sender').value,
        command: document.getElementById('command').value,
        content: document.getElementById('content').value,
        type: "sendCommand"
    };
    await sendToServer(msg);
}

async function sendConfiguration() {
    const msg = {
        sender: document.getElementById('sender').value,
        command: document.getElementById('command').value,
        content: document.getElementById('content').value,
        type: "setAxis",
        axisConfiguration: {
            frontDrives: document.getElementById('frontDrives').value,
            rearDrives: document.getElementById('rearDrives').value,
            frontWheels: document.getElementById('frontWheels').value,
            rearWheels: document.getElementById('rearWheels').value,
            driveType: document.querySelector('input[name="driveType"]:checked').value,
            robotName: document.getElementById('robotName').value,
        }
    };
    await sendToServer(msg);
}

async function sendSystemConfiguration() {
    const msg = {
        sender: document.getElementById('sender').value,
        command: document.getElementById('command').value,
        content: document.getElementById('content').value,
        type: "setSystemConfig",
    };
    await sendToServer(msg);
}

async function sendToServer(msg) {
    const replyDiv = document.getElementById('reply');
    try {
        const res = await fetch('http://localhost:7070/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(msg)
        });
        const jsonData = await res.json();

        // Seriennummer auslesen, falls vorhanden
        if (jsonData.serialNumber) {
            document.getElementById('serialNumber').textContent = jsonData.serialNumber;
        }
        if (jsonData.robotName) {
            document.getElementById('robotName').value = jsonData.robotName;
        }
        replyDiv.textContent = JSON.stringify(jsonData, null, 2);
    } catch (err) {
        replyDiv.textContent = "Fehler beim Senden: " + err;
    }
}

// --- Initialisierung ---
// Auch die Initialisierungsfunktion muss den neuen Sensor befüllen:
(async function init() {

    const sensorOptionsJson = { "options": ["...", "Lidar", "UltraSonic", "LED-Light", "Temp"] };
    const sensorOptionsAuxJson = { "options": ["...", "LineFollower"] };
    const sensorOptionsControllerJson = { "options": ["...", "ESP32", "Raspbery Zero", "Arduino Nano"] };

    // Befüllt die Dropdowns in den Panels
    const panels = ["frontSensors", "rearSensors", "centerSensors", "controllerSensors"];
    panels.forEach(panelId => populateSelects(panelId, sensorOptionsJson.options));

    // Befüllt die neuen Aux-Dropdowns
    const auxSelects = ["auxSensorFront", "auxSensorRear", "auxSensorCenter", "auxSensorController"];
    auxSelects.forEach(selectId => populateSingleSelect(selectId, sensorOptionsAuxJson.options));
    const contrSelects = ["auxControllerFront", "auxControllerRear", "auxControllerCenter"];
    contrSelects.forEach(selectId => populateSingleSelect(selectId, sensorOptionsControllerJson.options));

})();

function populateSelects(containerId, options) {
    const selects = document.querySelectorAll(`#${containerId} select`);
    selects.forEach(select => {
        select.innerHTML = "";
        options.forEach(opt => {
            const optionElement = document.createElement("option");
            optionElement.value = opt;
            optionElement.textContent = opt;
            select.appendChild(optionElement);
        });
    });
}

function populateSingleSelect(id, options) {
    const select = document.getElementById(id);
    if (!select) return;
    select.innerHTML = "";
    options.forEach(opt => {
        const optionElement = document.createElement("option");
        optionElement.value = opt;
        optionElement.textContent = opt;
        select.appendChild(optionElement);
    });
}