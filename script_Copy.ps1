
# Variable für den Projektnamen

param(
    [string]$projektName = "LCAMP-DHBW",
    [string]$projektCommit = "Version_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

)


# Configurator Binaries

$config_dest= "LCAMPConfigurator/bin"




# Ordner kopieren (inkl. Unterordner und Dateien)
# Binarys

# Export_URDF
Write-Host "Copy Export_URDF form: $projektName  Export_URDF"
$config_source = "..\$projektName\Export_URDF\bin\Release\net8.0"
Copy-Item -Path $config_source -Destination $config_dest -Recurse -Force

# Export_PartList
Write-Host "Copy Export_PartList form: $projektName  Export_PartList"
$config_source = "..\$projektName\Export_PartList\bin\Release\net8.0"
Copy-Item -Path $config_source -Destination $config_dest -Recurse -Force

# ImportRobot
Write-Host "Copy ImportRobot form: $projektName  ImportRobot"
$config_source = "..\$projektName\ImportRobot\bin\Release\net8.0"
Copy-Item -Path $config_source -Destination $config_dest -Recurse -Force



# LCAMPProcess
Write-Host "Copy LCAMPConfigurator form: $projektName  Process"
$config_source = "..\$projektName\LCAMP_Processes\bin\Release\net8.0-windows"
Copy-Item -Path $config_source -Destination $config_dest -Recurse -Force

# STL Viewer
Write-Host "Copy LCAMPConfigurator form: $projektName STLViewer"
$config_source = "..\$projektName\STLViewer\bin\Release\net8.0-windows8.0"

# LCAMPConfigurator
Write-Host "Copy LCAMPConfigurator form: $projektName  Configurator"
$config_source = "..\$projektName\LCAMPConfigurator\bin\Release\net8.0-windows"
Copy-Item -Path $config_source -Destination $config_dest -Recurse -Force


Write-Host "Copy LCAMPConfigurator form: $projektName  Configurator"
$config_source = "..\$projektName\LCAMPConfigurator\bin\Release\net8.0"
Copy-Item -Path $config_source -Destination $config_dest -Recurse -Force




# LCAMPConfigurator Daten
Write-Host "Copy Configurator Daten"
$config_daten_source = "..\$projektName\LCAMPConfigurator\Daten"
$config_daten_dest= "LCAMPConfigurator/LCAMPConfigurator/Daten"
# Ordner kopieren (inkl. Unterordner und Dateien)
Copy-Item -Path $config_daten_source -Destination $config_daten_dest -Recurse -Force


Write-Host "Copy Proces Daten"
$process_data_source = "..\$projektName\LCAMP_Processes\Daten"
$process_data_dest = "./LCAMP_Process/Daten"
# Ordner kopieren (inkl. Unterordner und Dateien)
Copy-Item -Path $process_data_source -Destination $process_data_dest -Recurse -Force


Write-Host "Copy Daten"
$daten_source = "..\$projektName\Daten"
$daten_dest = "Daten"
# Ordner kopieren (inkl. Unterordner und Dateien)
Copy-Item -Path $daten_source -Destination $daten_dest -Recurse -Force

Write-Host "Copy Templates"
$template_source = "..\$projektName\Templates"
$template_dest = "Templates"
# Ordner kopieren (inkl. Unterordner und Dateien)
Copy-Item -Path $template_source -Destination $template_dest -Recurse -Force

Write-Host "Copy Output"
$output_source = "..\$projektName\Output"
$output_dest = "Output"
# Ordner kopieren (inkl. Unterordner und Dateien)
Copy-Item -Path $output_source -Destination $output_dest -Recurse -Force

Write-Host "Copy Package"
$output_source = "..\$projektName\Package"
$output_dest = "Package"
# Ordner kopieren (inkl. Unterordner und Dateien)
Copy-Item -Path $output_source -Destination $output_dest -Recurse -Force

Pause


