import json
import numpy as np
import trimesh
from pathlib import Path
import os

class RobotGLBConverter:
    def __init__(self, json_file, stl_folder, output_file="robot.glb"):
        """
        Konvertiert eine Robot JSON-Datei in eine GLB-Datei
        
        Args:
            json_file: Pfad zur JSON-Datei
            stl_folder: Ordner mit den STL-Dateien
            output_file: Name der Ausgabe-GLB-Datei
        """
        self.json_file = json_file
        self.stl_folder = Path(stl_folder)
        self.output_file = output_file
        self.scene = trimesh.Scene()
        
    def load_json(self):
        """Lädt die JSON-Datei"""
        with open(self.json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def grad_to_rad(self, grad):
        """Konvertiert Gradiant (400 = 360°) zu Radiant"""
        return grad * (2 * np.pi / 400)
    
    def create_transform_matrix(self, geometry):
        """
        Erstellt eine Transformationsmatrix aus Geometrie-Daten
        
        Args:
            geometry: Dictionary mit xyz, rpy und unitXYZ/unitRPY
        """
        # Position extrahieren
        xyz = geometry.get('xyz', {})
        x = xyz.get('X', 0.0)
        y = xyz.get('Y', 0.0)
        z = xyz.get('Z', 0.0)
        
        # Rotation extrahieren
        rpy = geometry.get('rpy', {})
        roll = rpy.get('R', 0.0)
        pitch = rpy.get('P', 0.0)
        yaw = rpy.get('Y', 0.0)
        
        # Einheit überprüfen und konvertieren
        unit_rpy = geometry.get('unitRPY', 'grad')
        if unit_rpy == 'grad':
            roll = self.grad_to_rad(roll)
            pitch = self.grad_to_rad(pitch)
            yaw = self.grad_to_rad(yaw)
        elif unit_rpy == 'deg':
            roll = np.radians(roll)
            pitch = np.radians(pitch)
            yaw = np.radians(yaw)
        
        # Rotationsmatrizen erstellen (Roll-Pitch-Yaw)
        Rx = trimesh.transformations.rotation_matrix(roll, [1, 0, 0])
        Ry = trimesh.transformations.rotation_matrix(pitch, [0, 1, 0])
        Rz = trimesh.transformations.rotation_matrix(yaw, [0, 0, 1])
        
        # Kombinierte Rotation
        rotation = Rz @ Ry @ Rx
        
        # Translation hinzufügen
        rotation[0:3, 3] = [x, y, z]
        
        return rotation
    
    def get_color_from_rgba(self, rgba):
        """Konvertiert RGBA-Werte zu einem normalisierten Array"""
        if rgba and len(rgba) >= 3:
            return [rgba[0]/255, rgba[1]/255, rgba[2]/255, rgba[3]/255 if len(rgba) > 3 else 1.0]
        return [0.5, 0.5, 0.5, 1.0]  # Standard Grau
    
    def process_component(self, component, parent_transform=None):
        """
        Verarbeitet eine Komponente rekursiv
        
        Args:
            component: Dictionary der Komponente
            parent_transform: Transformationsmatrix des Elternteils
        """
        if parent_transform is None:
            parent_transform = np.eye(4)
        
        # Eigene Transformation berechnen
        geometry = component.get('Geometry', {})
        local_transform = self.create_transform_matrix(geometry)
        
        # Kombinierte Transformation
        global_transform = parent_transform @ local_transform
        
        # STL-Datei laden, falls vorhanden
        data_3d = component.get('Data3D')
        if data_3d:
            stl_path = self.stl_folder / data_3d
            if stl_path.exists():
                try:
                    mesh = trimesh.load(str(stl_path))
                    
                    # Farbe anwenden
                    material = component.get('Material', {})
                    color_info = material.get('Color', {})
                    rgba = color_info.get('rgba', [128, 128, 128, 255])
                    color = self.get_color_from_rgba(rgba)
                    
                    # Mesh transformieren
                    mesh.apply_transform(global_transform)
                    
                    # Material mit Farbe erstellen
                    mesh.visual.material = trimesh.visual.material.SimpleMaterial(
                        diffuse=color
                    )
                    
                    # Zum Scene hinzufügen
                    name = component.get('Name', 'unnamed')
                    self.scene.add_geometry(mesh, node_name=name)
                    
                    print(f"✓ Geladen: {data_3d} ({name})")
                    
                except Exception as e:
                    print(f"✗ Fehler beim Laden von {data_3d}: {e}")
            else:
                print(f"✗ STL nicht gefunden: {stl_path}")
        
        # Rekursiv alle Kinder verarbeiten
        components = component.get('Components', [])
        for child in components:
            self.process_component(child, global_transform)
    
    def convert(self):
        """Hauptfunktion zur Konvertierung"""
        print(f"Lade JSON-Datei: {self.json_file}")
        robot_data = self.load_json()
        
        print(f"Robot: {robot_data.get('Name', 'Unbekannt')}")
        print(f"SerienNr: {robot_data.get('SerialNumber', 'N/A')}")
        print(f"DriveConfig: {robot_data.get('DriveConfig', 'N/A')}")
        print("\nVerarbeite Komponenten...")
        
        # Hauptgeometrie verarbeiten
        main_geometry = robot_data.get('Geometry', {})
        main_transform = self.create_transform_matrix(main_geometry)
        
        # Alle Komponenten verarbeiten
        components = robot_data.get('Components', [])
        for component in components:
            self.process_component(component, main_transform)
        
        # GLB exportieren
        print(f"\nExportiere zu: {self.output_file}")
        self.scene.export(self.output_file)
        print(f"✓ Erfolgreich exportiert!")
        print(f"  - Anzahl Meshes: {len(self.scene.geometry)}")
        
        # Statistiken
        total_vertices = sum(len(mesh.vertices) for mesh in self.scene.geometry.values())
        total_faces = sum(len(mesh.faces) for mesh in self.scene.geometry.values())
        print(f"  - Vertices: {total_vertices:,}")
        print(f"  - Faces: {total_faces:,}")


# Verwendung
if __name__ == "__main__":
    # Pfade anpassen
    json_file = "RobiControl_new.json"
    stl_folder = "stl_files"  # Ordner mit den STL-Dateien
    output_file = "lcamp_robot.glb"
    
    # Prüfen ob JSON existiert
    if not os.path.exists(json_file):
        print(f"Fehler: JSON-Datei '{json_file}' nicht gefunden!")
        exit(1)
    
    # Prüfen ob STL-Ordner existiert
    if not os.path.exists(stl_folder):
        print(f"Fehler: STL-Ordner '{stl_folder}' nicht gefunden!")
        print(f"Bitte erstelle den Ordner und lege die STL-Dateien dort ab.")
        exit(1)
    
    # Konvertierung durchführen
    converter = RobotGLBConverter(json_file, stl_folder, output_file)
    converter.convert()
