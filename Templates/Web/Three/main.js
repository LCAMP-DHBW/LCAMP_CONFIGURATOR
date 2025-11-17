// Lokale Three.js-Module importieren
//import * as THREE from './node_modules/three/build/three.module.js';
import * as three from 'https://cdn.jsdelivr.net/npm/three@0.167.0/build/three.module.js';

import { GLTFLoader } from './three.js-master/examples/jsm/loaders/GLTFLoader.js';
//import { GLTFLoader } from './node_modules/three/examples/jsm/loaders/GLTFLoader.js';

//import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.167.0/examples/jsm/controls/OrbitControls.js';

//import { OrbitControls } from './node_modules/three/examples/jsm/controls/OrbitControls.js';
// Szene, Kamera, Renderer
const scene = new three.Scene();
const camera = new three.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new three.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Licht
const light = new three.DirectionalLight(0xffffff, 1);
light.position.set(5, 10, 7.5);
scene.add(light);
scene.add(new three.AmbientLight(0x404040, 1));

// OrbitControls (Kamerasteuerung per Maus)
//const controls = new OrbitControls(camera, renderer.domElement);
camera.position.set(0, 1, 3);
//controls.update();

// GLB/GLTF-Loader
const loader = new GLTFLoader();
loader.load('roboteil.glb', (gltf) => {
    const model = gltf.scene;
    scene.add(model);
    model.rotation.y = Math.PI;
    window.model = model;
}, undefined, (error) => {
    console.error('Fehler beim Laden des GLB:', error);
});

// Animation
function animate() {
    requestAnimationFrame(animate);
    if (window.model) {
        window.model.rotation.y += 0.005;
    }
  //  controls.update();
    renderer.render(scene, camera);
}
animate();

// Auf Fenstergröße reagieren
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
