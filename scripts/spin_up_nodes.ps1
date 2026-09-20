param (
    [int]$Count = 5
)

$SourcePath = Split-Path -Parent $PSScriptRoot
Write-Host "Source path: $SourcePath"

$BasePort = 8100
$PortsInUse = Get-NetTCPConnection | Select-Object -ExpandProperty LocalPort

for ($i = 1; $i -le $Count; $i++) {
    # Find next available port
    while ($PortsInUse -contains $BasePort) {
        $BasePort++
    }
    $Port = $BasePort
    $BasePort++
    
    $NodeId = "node-generated-$([guid]::NewGuid().ToString().Substring(0,8))"
    $DestPath = Join-Path -Path (Split-Path -Parent $SourcePath) -ChildPath "data_$NodeId"
    
    Write-Host "Spinning up node $i of $($Count): $NodeId on Port $Port..."
    
    # Exclude copying node_modules to save time/space, just copy source files
    New-Item -ItemType Directory -Force -Path $DestPath | Out-Null
    Copy-Item -Path "$SourcePath\*" -Destination $DestPath -Recurse -Exclude "node_modules", "data_*", ".git" -Force
    
    # Sibling nodes inherit the encrypted .env copy, but we pass process overrides to PowerShell
    # This avoids storing unencrypted variables or attempting to modify encrypted .env on disk.
    
    # Start the node in the background using npm run dev
    Write-Host "  Starting node..."
    
    # Build PowerShell command to set environment variables and launch the dev server
    $LaunchCmd = "cd `"$DestPath`"; `$env:NODE_ID='$NodeId'; `$env:PORT='$Port'; `$env:LAT='$(39.7392 + (Get-Random -Maximum 10 -Minimum -10)/100)'; `$env:LNG='$(-104.9903 + (Get-Random -Maximum 10 -Minimum -10)/100)'; `$env:ACN_DECRYPT_KEY='solomonletishitsubeyuel'; npm install; npm start"
    
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit -Command `"$LaunchCmd`"" -WindowStyle Minimized
    
    Start-Sleep -Seconds 2
}

Write-Host "Successfully spun up $Count new nodes."
