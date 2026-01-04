import json
import numpy as np
import trimesh
from pathlib import Path

def load_assembly_json(json_file):
    """Lädt die JSON-Datei mit der Assembly-Definition"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def rgba_to_normalized(rgba):
    """Konvertiert RGBA [0-255] zu normalisierten Werten [0-1]"""
    return [rgba[0]/255.0, rgba[1]/255.0, rgba[2]/255.0, rgba[3]/255.0]

def create_transformation_matrix(xyz, rpy):
    """
    Erstellt eine 4x4 Transformationsmatrix aus Position (xyz) und Rotation (rpy)
    xyz: Dictionary mit X, Y, Z in mm
    rpy: Dictionary mit R (Roll), P (Pitch), Y (Yaw) in Grad
    """
    # Position in Meter umrechnen (von mm)
    x, y, z = xyz['X'] / 1000.0, xyz['Y'] / 1000.0, xyz['Z'] / 1000.0
    
    # Rotation in Radianten umrechnen
    roll = np.radians(rpy['R'])
    pitch = np.radians(rpy['P'])
    yaw = np.radians(rpy['Y'])
    
    # Rotationsmatrizen (ZYX-Konvention)
    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])
    
    Ry = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])
    
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])
    
    # Kombinierte Rotation
    R = Rz @ Ry @ Rx
    
    # 4x4 Transformationsmatrix erstellen
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = [x, y, z]
    
    return T

def load_stl_with_transform(stl_path, xyz, rpy, color, scale=0.001):
    """
    Lädt eine STL-Datei und wendet Transformation und Farbe an
    
    Parameters:
    -----------
    stl_path : str
        Pfad zur STL-Datei
    xyz : dict
        Position in mm
    rpy : dict
        Rotation in Grad
    color : list
        RGBA Farbe [0-255]
    scale : float
        Skalierungsfaktor (Standard: 0.001 für mm->m)
    """
    try:
        # STL laden
        mesh = trimesh.load(stl_path)
        
        # Sicherstellen, dass es ein einzelnes Mesh ist
        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(mesh.dump())
        
        # WICHTIG: Skalierung anwenden (STL in mm -> Meter)
        mesh.apply_scale(scale)
        print(f"    Skalierung: {scale} (STL-Einheiten -> Meter)")
        
        # Transformation anwenden
        transform = create_transformation_matrix(xyz, rpy)
        mesh.apply_transform(transform)
        
        # Farbe setzen (als visuelle Eigenschaft)
        mesh.visual.face_colors = [int(c) for c in color]
        
        return mesh
    except FileNotFoundError:
        print(f"WARNUNG: STL-Datei nicht gefunden: {stl_path}")
        return None
    except Exception as e:
        print(f"FEHLER beim Laden von {stl_path}: {e}")
        return None

def create_wheel_from_json(json_file, stl_directory='.', scale=0.001):
    """
    Erstellt ein Rad aus der JSON-Definition
    
    Parameters:
    -----------
    json_file : str
        Pfad zur JSON-Datei
    stl_directory : str
        Verzeichnis mit STL-Dateien
    scale : float
        Skalierungsfaktor für STL-Dateien (Standard: 0.001 für mm->m)
    """
    data = load_assembly_json(json_file)
    assembly = data.get('Assembly', {})
    components = assembly.get('Components', [])
    
    meshes = []
    
    for component in components:
        stl_file = component.get('Data3D', '')
        geometry = component.get('Geometry', {})
        material = component.get('Material', {})
        color_info = material.get('Color', {})
        rgba = color_info.get('rgba', [128, 128, 128, 255])
        
        xyz = geometry.get('xyz', {'X': 0, 'Y': 0, 'Z': 0})
        rpy = geometry.get('rpy', {'R': 0, 'P': 0, 'Y': 0})
        
        if stl_file:
            stl_path = Path(stl_directory) / stl_file
            mesh = load_stl_with_transform(stl_path, xyz, rpy, rgba, scale)
            if mesh is not None:
                meshes.append(mesh)
    
    if meshes:
        return trimesh.util.concatenate(meshes)
    else:
        # Platzhalter-Rad erstellen
        return create_placeholder_wheel()

def create_placeholder_wheel():
    """
    Erstellt ein einfaches Platzhalter-Rad
    """
    # Reifen (Torus)
    tire = trimesh.creation.annulus(r_min=0.038, r_max=0.046, height=0.030)
    tire.visual.face_colors = [20, 20, 20, 255]  # Schwarz
    
    # Felge (Zylinder)
    rim = trimesh.creation.cylinder(radius=0.038, height=0.025)
    rim.visual.face_colors = [128, 128, 128, 255]  # Grau
    
    # Nabe (kleinerer Zylinder)
    hub = trimesh.creation.cylinder(radius=0.015, height=0.032)
    hub.visual.face_colors = [137, 207, 240, 255]  # Hellblau
    
    return trimesh.util.concatenate([tire, rim, hub])

def create_robot_with_wheels(json_file='Regular-Wheel.json', 
                             stl_directory='.', 
                             output_file='robot_with_wheels.glb',
                             animate=False,
                             stl_scale=0.001):
    """
    Erstellt einen Roboter mit zentralem Block und 4 Rädern
    
    Parameters:
    -----------
    json_file : str
        Pfad zur Wheel-JSON-Datei
    stl_directory : str
        Verzeichnis mit STL-Dateien
    output_file : str
        Ausgabedatei für GLB
    animate : bool
        Wenn True, werden mehrere Frames mit Rotation erstellt
    stl_scale : float
        Skalierungsfaktor für STL-Dateien (0.001 = mm->m, 1.0 = keine Skalierung)
    """
    print("=" * 60)
    print("Erstelle Roboter mit zentralem Block und 4 Rädern")
    print("=" * 60)
    print(f"STL-Skalierung: {stl_scale} (z.B. 0.001 für mm->m)")
    
    # Zentraler blauer Block erstellen
    print("\n[1] Erstelle zentralen blauen Block...")
    central_block = trimesh.creation.box(extents=[0.15, 0.20, 0.08])  # 150x200x80mm
    central_block.visual.face_colors = [30, 100, 200, 255]  # Blau
    # Block anheben (Bodenfreiheit)
    central_block.apply_translation([0, 0, 0.06])  # 60mm über Boden
    print(f"   Größe: 150 x 200 x 80 mm")
    print(f"   Farbe: Blau")
    
    # Rad laden (einmal, dann kopieren)
    print("\n[2] Lade Rad-Geometrie...")
    try:
        wheel_base = create_wheel_from_json(json_file, stl_directory, stl_scale)
        print(f"   ✓ Rad geladen: {len(wheel_base.vertices)} Vertices")
    except Exception as e:
        print(f"   Fehler beim Laden, verwende Platzhalter: {e}")
        wheel_base = create_placeholder_wheel()
    
    # 4 Räder an den Ecken positionieren
    print("\n[3] Positioniere 4 Räder...")
    
    # Rad-Positionen (vorne-links, vorne-rechts, hinten-links, hinten-rechts)
    wheel_positions = [
        {'name': 'Vorne Links',  'pos': [-0.065, 0.085, 0.046], 'rot': 0},      # FL
        {'name': 'Vorne Rechts', 'pos': [0.065, 0.085, 0.046], 'rot': 180},   # FR
        {'name': 'Hinten Links',  'pos': [-0.065, -0.085, 0.046], 'rot': 0},     # RL
        {'name': 'Hinten Rechts', 'pos': [0.065, -0.085, 0.046], 'rot': 180}   # RR
    ]
    
    all_meshes = [central_block]
    
    num_frames = 36 if animate else 1  # 36 Frames für Animation (10 Grad pro Frame)
    
    for frame in range(num_frames):
        rotation_angle = frame * 10  # Grad pro Frame
        frame_meshes = [central_block.copy()]
        
        for i, wheel_pos in enumerate(wheel_positions):
            wheel = wheel_base.copy()
            
            # Rotation um Y-Achse (Fahrtrichtung)
            rot_matrix = trimesh.transformations.rotation_matrix(
                np.radians(rotation_angle), [0, 1, 0], [0, 0, 0]
            )
            wheel.apply_transform(rot_matrix)
            
            # Rotation um Z-Achse (für rechte Räder)
            if wheel_pos['rot'] != 0:
                flip_matrix = trimesh.transformations.rotation_matrix(
                    np.radians(wheel_pos['rot']), [0, 0, 1], [0, 0, 0]
                )
                wheel.apply_transform(flip_matrix)
            
            # Position setzen
            wheel.apply_translation(wheel_pos['pos'])
            
            frame_meshes.append(wheel)
            
            if frame == 0:  # Nur beim ersten Frame ausgeben
                print(f"   [{i+1}] {wheel_pos['name']}: "
                      f"X={wheel_pos['pos'][0]*1000:.1f}mm, "
                      f"Y={wheel_pos['pos'][1]*1000:.1f}mm, "
                      f"Z={wheel_pos['pos'][2]*1000:.1f}mm")
        
        if animate:
            # Frame speichern
            combined = trimesh.util.concatenate(frame_meshes)
            frame_file = output_file.replace('.glb', f'_frame_{frame:03d}.glb')
            combined.export(frame_file, file_type='glb')
        else:
            all_meshes.extend(frame_meshes[1:])  # Block nur einmal
    
    if not animate:
        # Alle Meshes kombinieren
        print("\n[4] Kombiniere alle Komponenten...")
        combined_robot = trimesh.util.concatenate(all_meshes)
        
        print(f"   Gesamt-Vertices: {len(combined_robot.vertices)}")
        print(f"   Gesamt-Faces: {len(combined_robot.faces)}")
        
        # Exportieren
        print(f"\n[5] Exportiere nach: {output_file}")
        combined_robot.export(output_file, file_type='glb')
        
        # Statistiken
        bounds = combined_robot.bounds
        size = bounds[1] - bounds[0]
        print(f"\n{'='*60}")
        print("✓ Roboter erfolgreich erstellt!")
        print(f"{'='*60}")
        print(f"\nAbmessungen:")
        print(f"  Breite (X):  {size[0]*1000:.1f} mm")
        print(f"  Länge (Y):   {size[1]*1000:.1f} mm")
        print(f"  Höhe (Z):    {size[2]*1000:.1f} mm")
        print(f"\nKomponenten:")
        print(f"  - 1x Zentraler Block (blau)")
        print(f"  - 4x Räder (Regular-Wheel)")
        
        return combined_robot
    else:
        print(f"\n✓ {num_frames} animierte Frames erstellt!")
        return None

def create_simple_robot_demo(output_file='simple_robot.glb'):
    """
    Erstellt einen einfachen Demo-Roboter ohne externe JSON/STL-Dateien
    """
    print("=" * 60)
    print("Erstelle einfachen Demo-Roboter")
    print("=" * 60)
    
    # Zentraler Block
    central_block = trimesh.creation.box(extents=[0.15, 0.20, 0.08])
    central_block.visual.face_colors = [30, 100, 200, 255]  # Blau
    central_block.apply_translation([0, 0, 0.06])
    
    # 4 einfache Räder
    wheel_positions = [
        [-0.065, 0.085, 0.046],   # Vorne Links
        [0.065, 0.085, 0.046],    # Vorne Rechts
        [-0.065, -0.085, 0.046],  # Hinten Links
        [0.065, -0.085, 0.046]    # Hinten Rechts
    ]
    
    meshes = [central_block]
    
    for pos in wheel_positions:
        # Rad erstellen (Zylinder mit Reifen)
        rim = trimesh.creation.cylinder(radius=0.046, height=0.030)
        rim.apply_transform(trimesh.transformations.rotation_matrix(
            np.radians(90), [1, 0, 0]
        ))
        rim.visual.face_colors = [50, 50, 50, 255]
        rim.apply_translation(pos)
        meshes.append(rim)
    
    # Kombinieren und exportieren
    robot = trimesh.util.concatenate(meshes)
    robot.export(output_file, file_type='glb')
    
    print(f"✓ Demo-Roboter erstellt: {output_file}")
    return robot

# Hauptprogramm
if __name__ == "__main__":
    import sys
    
    # Parameter
    json_file = "Regular-Wheel.json"
    stl_directory = "."
    output_file = "robot_with_wheels.glb"
    create_demo = False
    animate = False
    stl_scale = 0.001  # Standard: mm->m
    
    # Kommandozeilenargumente
    if '--demo' in sys.argv:
        create_demo = True
    if '--animate' in sys.argv:
        animate = True
    if '--scale' in sys.argv:
        # --scale 0.001 oder --scale 1.0
        idx = sys.argv.index('--scale')
        if idx + 1 < len(sys.argv):
            stl_scale = float(sys.argv[idx + 1])
            print(f"Verwende STL-Skalierung: {stl_scale}")
    
    args = [arg for arg in sys.argv[1:] if not arg.startswith('--') and not arg.replace('.','').replace('-','').isdigit()]
    if len(args) > 0:
        json_file = args[0]
    if len(args) > 1:
        stl_directory = args[1]
    if len(args) > 2:
        output_file = args[2]
    
    try:
        if create_demo:
            # Einfacher Demo-Roboter ohne externe Dateien
            create_simple_robot_demo(output_file)
        else:
            # Roboter mit JSON/STL-Rädern
            create_robot_with_wheels(json_file, stl_directory, output_file, animate, stl_scale)
            
    except FileNotFoundError as e:
        print(f"\n✗ Datei nicht gefunden: {e}")
        print("\nErstelle Demo-Roboter stattdessen...")
        create_simple_robot_demo(output_file)
    except Exception as e:
        print(f"\n✗ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        print("\nErstelle Demo-Roboter stattdessen...")
        create_simple_robot_demo(output_file)

"""
INSTALLATION:
-------------
pip install numpy trimesh[easy]

VERWENDUNG:
-----------
# Standard - Roboter mit Rädern aus JSON
python robot_creator.py

# Demo-Modus - ohne externe Dateien
python robot_creator.py --demo

# Animation - Räder drehen sich
python robot_creator.py --animate

# Mit Parametern
python robot_creator.py Regular-Wheel.json ./stl_files robot.glb

# Demo mit eigenem Dateinamen
python robot_creator.py --demo my_robot.glb

AUSGABE:
--------
- robot_with_wheels.glb: Roboter mit 4 Rädern und zentralem Block
- simple_robot.glb: Demo ohne externe Dateien (mit --demo)

STRUKTUR:
---------
- Zentraler blauer Block: 150 x 200 x 80 mm
- 4 Räder an Ecken positioniert:
  * Vorne Links  (-65, 85, 46 mm)
  * Vorne Rechts (65, 85, 46 mm)
  * Hinten Links  (-65, -85, 46 mm)
  * Hinten Rechts (65, -85, 46 mm)

FEATURES:
---------
✓ Zentraler blauer Block als Chassis
✓ 4 Räder aus Regular-Wheel.json
✓ Korrekte Positionierung
✓ Optional: Animation mit Rotation
✓ Fallback auf Demo-Geometrie
✓ GLB-Export für 3D-Viewer
"""