import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import numpy as np
from pathlib import Path

class RobotURDFConverter:
    def __init__(self, json_file, output_file="robot.urdf", mesh_package="package://robot_description"):
        """
        Konvertiert eine Robot JSON-Datei in eine URDF-Datei
        
        Args:
            json_file: Pfad zur JSON-Datei
            output_file: Name der Ausgabe-URDF-Datei
            mesh_package: Package-Pfad für Mesh-Referenzen
        """
        self.json_file = json_file
        self.output_file = output_file
        self.mesh_package = mesh_package
        self.link_counter = 0
        self.joint_counter = 0
        
    def load_json(self):
        """Lädt die JSON-Datei"""
        with open(self.json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def grad_to_rad(self, grad):
        """Konvertiert Gradiant (400 = 360°) zu Radiant"""
        return grad * (2 * np.pi / 400)
    
    def sanitize_name(self, name):
        """Bereinigt Namen für URDF (keine Leerzeichen, Sonderzeichen)"""
        name = name.replace(' ', '_')
        name = name.replace('-', '_')
        name = name.replace('/', '_')
        name = ''.join(c for c in name if c.isalnum() or c == '_')
        return name
    
    def create_origin_element(self, geometry):
        """Erstellt ein URDF origin-Element aus Geometrie-Daten"""
        origin = ET.Element('origin')
        
        # Position
        xyz = geometry.get('xyz', {})
        x = xyz.get('X', 0.0) / 1000.0  # mm zu m
        y = xyz.get('Y', 0.0) / 1000.0
        z = xyz.get('Z', 0.0) / 1000.0
        origin.set('xyz', f"{x} {y} {z}")
        
        # Rotation
        rpy = geometry.get('rpy', {})
        roll = rpy.get('R', 0.0)
        pitch = rpy.get('P', 0.0)
        yaw = rpy.get('Y', 0.0)
        
        # Einheit konvertieren
        unit_rpy = geometry.get('unitRPY', 'grad')
        if unit_rpy == 'grad':
            roll = self.grad_to_rad(roll)
            pitch = self.grad_to_rad(pitch)
            yaw = self.grad_to_rad(yaw)
        elif unit_rpy == 'deg':
            roll = np.radians(roll)
            pitch = np.radians(pitch)
            yaw = np.radians(yaw)
        
        origin.set('rpy', f"{roll} {pitch} {yaw}")
        
        return origin
    
    def create_inertial_element(self, mass_kg):
        """Erstellt ein URDF inertial-Element"""
        inertial = ET.Element('inertial')
        
        # Masse
        mass_elem = ET.SubElement(inertial, 'mass')
        mass_elem.set('value', str(mass_kg))
        
        # Origin (Schwerpunkt)
        origin = ET.SubElement(inertial, 'origin')
        origin.set('xyz', "0 0 0")
        origin.set('rpy', "0 0 0")
        
        # Trägheitsmoment (vereinfacht als Box)
        inertia = ET.SubElement(inertial, 'inertia')
        # Vereinfachte Werte für kleine Teile
        i_val = mass_kg * 0.001
        inertia.set('ixx', str(i_val))
        inertia.set('ixy', "0")
        inertia.set('ixz', "0")
        inertia.set('iyy', str(i_val))
        inertia.set('iyz', "0")
        inertia.set('izz', str(i_val))
        
        return inertial
    
    def create_visual_element(self, stl_file, color_rgba=None):
        """Erstellt ein URDF visual-Element"""
        visual = ET.Element('visual')
        
        # Origin
        origin = ET.SubElement(visual, 'origin')
        origin.set('xyz', "0 0 0")
        origin.set('rpy', "0 0 0")
        
        # Geometry
        geometry = ET.SubElement(visual, 'geometry')
        mesh = ET.SubElement(geometry, 'mesh')
        mesh.set('filename', f"{self.mesh_package}/stl_files/{stl_file}")
        mesh.set('scale', "0.001 0.001 0.001")  # mm zu m
        
        # Material (optional)
        if color_rgba:
            material = ET.SubElement(visual, 'material')
            material.set('name', f"color_{self.link_counter}")
            color = ET.SubElement(material, 'color')
            r, g, b, a = color_rgba
            color.set('rgba', f"{r/255} {g/255} {b/255} {a/255}")
        
        return visual
    
    def create_collision_element(self, stl_file):
        """Erstellt ein URDF collision-Element"""
        collision = ET.Element('collision')
        
        # Origin
        origin = ET.SubElement(collision, 'origin')
        origin.set('xyz', "0 0 0")
        origin.set('rpy', "0 0 0")
        
        # Geometry
        geometry = ET.SubElement(collision, 'geometry')
        mesh = ET.SubElement(geometry, 'mesh')
        mesh.set('filename', f"{self.mesh_package}/stl_files/{stl_file}")
        mesh.set('scale', "0.001 0.001 0.001")  # mm zu m
        
        return collision
    
    def create_link(self, component, parent_name=None):
        """Erstellt URDF link- und joint-Elemente"""
        links = []
        joints = []
        
        name = self.sanitize_name(component.get('Name', f'link_{self.link_counter}'))
        self.link_counter += 1
        
        # Link erstellen
        link = ET.Element('link')
        link.set('name', name)
        
        # Masse
        geometry = component.get('Geometry', {})
        mass_g = geometry.get('mass', 0.0)
        mass_kg = mass_g / 1000.0 if mass_g > 0 else 0.01  # Mindestens 10g
        
        # Inertial
        link.append(self.create_inertial_element(mass_kg))
        
        # Visual (wenn STL vorhanden)
        stl_file = component.get('Data3D')
        if stl_file:
            material = component.get('Material', {})
            color_info = material.get('Color', {})
            rgba = color_info.get('rgba')
            
            visual = self.create_visual_element(stl_file, rgba)
            link.append(visual)
            
            # Collision
            collision = self.create_collision_element(stl_file)
            link.append(collision)
        
        links.append(link)
        
        # Joint erstellen (wenn Parent vorhanden)
        if parent_name:
            joint = ET.Element('joint')
            joint_name = f"{parent_name}_to_{name}"
            joint.set('name', joint_name)
            
            # Joint-Typ bestimmen
            joint_type = geometry.get('JointType', 'fixed').lower()
            if joint_type == 'continuous':
                joint.set('type', 'continuous')
            elif joint_type == 'revolute':
                joint.set('type', 'revolute')
            elif joint_type == 'prismatic':
                joint.set('type', 'prismatic')
            else:
                joint.set('type', 'fixed')
            
            # Parent und Child
            parent_elem = ET.SubElement(joint, 'parent')
            parent_elem.set('link', parent_name)
            
            child_elem = ET.SubElement(joint, 'child')
            child_elem.set('link', name)
            
            # Origin (Transformation)
            origin = self.create_origin_element(geometry)
            joint.append(origin)
            
            # Axis (für revolute/continuous/prismatic joints)
            if joint_type in ['continuous', 'revolute', 'prismatic']:
                axis = ET.SubElement(joint, 'axis')
                # Standard: Z-Achse für Rotation
                axis.set('xyz', "0 0 1")
                
                # Limits für revolute joints
                if joint_type == 'revolute':
                    limit = ET.SubElement(joint, 'limit')
                    limit.set('lower', "-3.14159")
                    limit.set('upper', "3.14159")
                    limit.set('effort', "100")
                    limit.set('velocity', "1")
            
            joints.append(joint)
        
        # Rekursiv alle Kinder verarbeiten
        components = component.get('Components', [])
        for child in components:
            child_links, child_joints = self.create_link(child, name)
            links.extend(child_links)
            joints.extend(child_joints)
        
        return links, joints
    
    def convert(self):
        """Hauptfunktion zur Konvertierung"""
        print(f"Lade JSON-Datei: {self.json_file}")
        robot_data = self.load_json()
        
        robot_name = self.sanitize_name(robot_data.get('Name', 'robot'))
        print(f"Robot: {robot_data.get('Name', 'Unbekannt')}")
        print(f"SerienNr: {robot_data.get('SerialNumber', 'N/A')}")
        
        # Root-Element erstellen
        robot = ET.Element('robot')
        robot.set('name', robot_name)
        
        # Base-Link erstellen
        base_link = ET.Element('link')
        base_link.set('name', 'base_link')
        
        # Minimale Inertial für base_link
        base_link.append(self.create_inertial_element(0.1))
        
        robot.append(base_link)
        
        print("\nVerarbeite Komponenten...")
        
        # Alle Komponenten verarbeiten
        components = robot_data.get('Components', [])
        all_links = []
        all_joints = []
        
        for component in components:
            links, joints = self.create_link(component, 'base_link')
            all_links.extend(links)
            all_joints.extend(joints)
        
        # Links und Joints zum Robot hinzufügen
        for link in all_links:
            robot.append(link)
        
        for joint in all_joints:
            robot.append(joint)
        
        # XML formatieren und speichern
        print(f"\nExportiere zu: {self.output_file}")
        xml_str = minidom.parseString(ET.tostring(robot, encoding='unicode')).toprettyxml(indent="  ")
        
        # Entferne leere Zeilen
        xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        print(f"✓ Erfolgreich exportiert!")
        print(f"  - Anzahl Links: {len(all_links) + 1}")  # +1 für base_link
        print(f"  - Anzahl Joints: {len(all_joints)}")
        
        # Statistiken nach Joint-Typ
        joint_types = {}
        for joint in all_joints:
            jtype = joint.get('type')
            joint_types[jtype] = joint_types.get(jtype, 0) + 1
        
        print("\n  Joint-Typen:")
        for jtype, count in joint_types.items():
            print(f"    - {jtype}: {count}")
        
        print("\n📝 Hinweise:")
        print("  - Meshes werden erwartet in: stl_files/")
        print("  - Anpassen des package-Pfads eventuell nötig")
        print("  - Achsen-Definitionen für revolute Joints prüfen")
        print("  - Trägheitsmomente sind vereinfacht")


# Verwendung
if __name__ == "__main__":
    import os
    
    # Pfade anpassen
    json_file = "RobiControl_new.json"
    output_file = "lcamp_robot.urdf"
    
    # Optional: Package-Pfad anpassen
    mesh_package = "package://lcamp_robot_description"
    
    # Prüfen ob JSON existiert
    if not os.path.exists(json_file):
        print(f"Fehler: JSON-Datei '{json_file}' nicht gefunden!")
        exit(1)
    
    # Konvertierung durchführen
    converter = RobotURDFConverter(json_file, output_file, mesh_package)
    converter.convert()
    
    print(f"\n✅ URDF-Datei erstellt: {output_file}")
    print("\n📦 Nächste Schritte:")
    print("  1. Erstelle Ordner 'stl_files/' und kopiere alle STL-Dateien hinein")
    print("  2. Passe Package-Namen in der URDF an (package://...)")
    print("  3. Prüfe Joint-Achsen und Limits")
    print("  4. Teste mit: check_urdf lcamp_robot.urdf")
