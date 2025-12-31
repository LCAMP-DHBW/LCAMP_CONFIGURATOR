// JavaScript source code
// --- Farbschema-Logik ---

function drawSchematic(mainColor, accentColor, detailColor) {
    const canvas = document.getElementById('colorCanvas');
    if (!canvas.getContext) return;
    const ctx = canvas.getContext('2d');

    // Canvas leeren
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Hintergrund
    ctx.fillStyle = '#f7f7f7';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Beispiel-Skizze: Eine Prinzipskizze des Roboters

    // Hauptkörper (Hauptfarbe)
    ctx.fillStyle = mainColor;
    ctx.fillRect(50, 60, 300, 80);

    // Räder (Akzentfarbe)
    ctx.fillStyle = accentColor;
    ctx.beginPath();
    ctx.arc(80, 140, 25, 0, 2 * Math.PI);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(320, 140, 25, 0, 2 * Math.PI);
    ctx.fill();

    // Sensor (Detailfarbe)
    ctx.fillStyle = detailColor;
    ctx.fillRect(175, 20, 50, 40);
    ctx.fillStyle = mainColor;
    ctx.fillRect(185, 30, 30, 20); // Linse

    // Text-Labels
    ctx.fillStyle = '#333';
    ctx.font = '12px Arial';
    ctx.fillText('Hauptkörper', 170, 105);
    ctx.fillText('Sensor', 180, 80);
    ctx.fillText('Räder', 70, 175);
    ctx.fillText('Räder', 310, 175);
}

function updateCanvas() {
    const mainColor = document.getElementById('mainColor').value;
    const accentColor = document.getElementById('accentColor').value;
    const detailColor = document.getElementById('detailColor').value;

    drawSchematic(mainColor, accentColor, detailColor);
}

// Initialer Aufruf beim Laden der Seite
window.addEventListener('load', () => {
    updateCanvas();

    // Event-Listener für Farbänderungen
    document.getElementById('mainColor').addEventListener('input', updateCanvas);
    document.getElementById('accentColor').addEventListener('input', updateCanvas);
    document.getElementById('detailColor').addEventListener('input', updateCanvas);
});