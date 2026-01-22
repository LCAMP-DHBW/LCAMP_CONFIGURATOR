// Generate_Wheel.js
import * as THREE from 'three';

function createRoller(
  radius = 10,
  height = 40,
  bulge = 0.3,
  inner = 1.5,
  segments = 32,
  color = "#0f0f0f"
) {
  const points = [];
  const steps = segments;

  // innerer Radius unten
  points.push(new THREE.Vector2(inner, -height / 2));

  // äußere bauchige Kontur
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;              // 0 → 1
    const y = t * height;
    const r = radius * (1 + bulge * Math.sin(Math.PI * t));
    points.push(new THREE.Vector2(r, y - height / 2));
  }

  // innerer Radius oben + schließen
  points.push(new THREE.Vector2(inner, height / 2));
  points.push(new THREE.Vector2(inner, -height / 2));

  const geometry = new THREE.LatheGeometry(points, 64);
  const material = new THREE.MeshStandardMaterial({ color });
  const roller = new THREE.Mesh(geometry, material);

  return roller;
}

function getTransform(alpha, theta, r, d) {
  const ca = Math.cos(alpha);
  const sa = Math.sin(alpha);
  const ct = Math.cos(theta);
  const st = Math.sin(theta);

  const m = new THREE.Matrix4();
  m.set(
    ct, st * sa, st * ca, r * ct,
    0, ca, -sa, d,
    -st, ct * sa, ca * ct, -r * st,
    0, 0, 0, 1);
  return m;
}

//*************************************************************************
function Create_Tire(
  outerRadius = 48,
  innerRadius = 39,
  tireHeight = 30.0,
  tireColor = "#020202"
) {
  /* Tire */
  // Outer shape
  const ringShape = new THREE.Shape();
  ringShape.absarc(0, 0, outerRadius, 0, Math.PI * 2, false);

  // Inner hole
  const holePath = new THREE.Path();
  holePath.absarc(0, 0, innerRadius, 0, Math.PI * 2, true);
  ringShape.holes.push(holePath);

  // Extrude settings
  const extrudeSettings = { depth: tireHeight, bevelEnabled: false };

  // Geometry & mesh
  const tubeGeo = new THREE.ExtrudeGeometry(ringShape, extrudeSettings);
  const tubeMat = new THREE.MeshStandardMaterial({ color: tireColor });
  const tireMesh = new THREE.Mesh(tubeGeo, tubeMat);
  tireMesh.rotation.x = Math.PI / 2;

  return tireMesh
}





//****************************************************************************
export function GenerateSensorBox(
  radius = 190,
  height = 64,
  clip = 153,
  dir = 1,
  colors
) {

  const cylBoxGeo = new THREE.CylinderGeometry(
    radius,   // radiusTop
    radius,   // radiusBottom
    height,   // height
    64
  );
  const secantPlaneFront = new THREE.Plane(
    new THREE.Vector3(dir, 0, 0).normalize(), // plane normal (tilt = secant)
    -clip                                          // plane offset
  );


  const cylBoxMat = new THREE.MeshStandardMaterial({
    color: colors.main,
    transparent: true,
    opacity: 0.9,
    side: THREE.DoubleSide,
    clippingPlanes: [secantPlaneFront],
    clipShadows: true
  });



  const sBox = new THREE.Mesh(cylBoxGeo, cylBoxMat);

  return sBox;
}

//****************************************************************************************************
// Create Regular Wheel
export function Create_Regular_Wheel(
  outerRadius = 48,
  colors
) {
  const innerRadius = outerRadius - 8;

  /* 🔹 Transparent Cylinder */
  const cylGeo = new THREE.CylinderGeometry(
    innerRadius,    // top radius
    innerRadius,    // bottom radius
    38,    // height
    64    // radial segments
  );

  const cylMat = new THREE.MeshStandardMaterial({
    color: colors.detail,
    transparent: true,
    opacity: 0.8,
    side: THREE.DoubleSide
  });

  /* Geometrie & Material */
  const boxHubCapGeo = new THREE.CylinderGeometry(
    20,    // top radius
    20,    // bottom radius
    10,    // height
    6    // radial segments
  );

  const hubCapMat = new THREE.MeshStandardMaterial({ color: colors.accent });

  const hubCap = new THREE.Mesh(boxHubCapGeo, hubCapMat)
  const wheelblock = new THREE.Mesh(cylGeo, cylMat);
  const tire = Create_Tire(48, 33, 30, 54, colors.tireColor);

  hubCap.position.y = 18.0;           // über dem Block
  tire.position.y = 15.0;

  wheelblock.add(hubCap);
  wheelblock.add(tire);

  return wheelblock;
}

//****************************************************************************************
// Create Regular Wheel
export function Create_Mecanum_Wheel(
  outerRadius = 48,
  colors,
  direction
) {
  const innerRadius = outerRadius - 20;


  const cylGeo = new THREE.CylinderGeometry(
    innerRadius,    // top radius
    innerRadius,    // bottom radius
    38,    // height
    64    // radial segments
  );
  const cylMat = new THREE.MeshStandardMaterial({
    color: colors.detailr,
    transparent: true,
    opacity: 0.8,
    side: THREE.DoubleSide
  });
  /* Geometrie & Material */
  const boxHubCapGeo = new THREE.CylinderGeometry(
    20,    // top radius
    20,    // bottom radius
    10,    // height
    6    // radial segments
  );

  const hubCapMat = new THREE.MeshStandardMaterial({ color: colors.accent });

  const hubCap = new THREE.Mesh(boxHubCapGeo, hubCapMat)
  const wheelblock = new THREE.Mesh(cylGeo, cylMat);
  const baseRoller = createRoller(8, 34, 0.2, 1.5, 64, colors.tire);

  const alpha = THREE.MathUtils.degToRad(45 * direction);
  const r = 39;
  const d = 0;
  const count = 9;
  const stepDeg = 360 / count;
  for (let i = 0; i < count; i++) {
    const roller = baseRoller.clone();

    const theta = THREE.MathUtils.degToRad(i * stepDeg);

    const M = getTransform(alpha, theta, r, d);

    roller.matrixAutoUpdate = false;
    roller.matrix.copy(M);

    wheelblock.add(roller);
  }
  hubCap.position.y = 18.0;           // über dem Block


  wheelblock.add(hubCap);

  return wheelblock;
}

//****************************************************************************************
// Create Regular Wheel
export function Create_Omni_Wheel(
  outerRadius = 48,
  colors
) {
  const innerRadius = outerRadius - 20;
  const cylGeo = new THREE.CylinderGeometry(
    innerRadius,    // top radius
    innerRadius,    // bottom radius
    34,    // height
    64    // radial segments
  );
  const cylMat = new THREE.MeshStandardMaterial({
    color: colors.detail,
    transparent: true,
    opacity: 0.8,
    side: THREE.DoubleSide
  });
  /* Geometrie & Material */
  const boxHubCapGeo = new THREE.CylinderGeometry(
    20,    // top radius
    20,    // bottom radius
    10,    // height
    6    // radial segments
  );

  const hubCapMat = new THREE.MeshStandardMaterial({ color: colors.accent });

  const hubCap = new THREE.Mesh(boxHubCapGeo, hubCapMat)
  const wheelblock = new THREE.Mesh(cylGeo, cylMat);
  const baseRoller = createRoller(8, 31, 0.2, 1.5, 64, colors.tire);

  const alpha = THREE.MathUtils.degToRad(90);
  const r = 39;

  const count = 6;
  const stepDeg = 360 / count;
  for (let i = 0; i < count; i++) {
    const roller = baseRoller.clone();

    const theta = THREE.MathUtils.degToRad(i * stepDeg);

    const M = getTransform(alpha, theta, r, -10);

    roller.matrixAutoUpdate = false;
    roller.matrix.copy(M);

    wheelblock.add(roller);
  }
  for (let i = 0; i < count; i++) {
    const roller = baseRoller.clone();

    const theta = THREE.MathUtils.degToRad(i * stepDeg + 30);

    const M = getTransform(alpha, theta, r, 10);

    roller.matrixAutoUpdate = false;
    roller.matrix.copy(M);

    wheelblock.add(roller);
  }
  hubCap.position.y = 18.0;           // über dem Block
  wheelblock.add(hubCap);

  return wheelblock;
}


