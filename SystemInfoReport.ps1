# Get Basic Information
$Username = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name.Split('\')[1]
$Hostname = $env:COMPUTERNAME
$MainAdapter = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | Sort-Object -Property InterfaceMetric | Select-Object -First 1
$IPAddress = (Get-NetIPAddress -InterfaceIndex $MainAdapter.ifIndex -AddressFamily IPv4).IPAddress

# Construct the output filename
$outputHtmlFile = "${Hostname}_${Username}_${IPAddress}.html"

# Start HTML
$html = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced System Information Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #dddddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        h2 { color: #4CAF50; }
    </style>
</head>
<body>
"@

# Basic Information
$html += "<h2>Basic Information</h2><table><tr><th>Item</th><th>Value</th></tr>"
$html += "<tr><td>Username</td><td>$Username</td></tr>"
$html += "<tr><td>Hostname</td><td>$Hostname</td></tr>"
$html += "<tr><td>IP Address</td><td>$IPAddress</td></tr></table>"

# Group Memberships
$html += "<h2>Group Memberships</h2><table><tr><th>Group Name</th></tr>"
$Groups = [System.Security.Principal.WindowsIdentity]::GetCurrent().Groups | ForEach-Object { $_.Translate([System.Security.Principal.NTAccount]) }
$Groups | ForEach-Object { 
    $html += "<tr><td>$_</td></tr>"
}
$html += "</table>"

# User Privileges
$html += "<h2>User Privileges</h2><table><tr><th>Privilege Name</th><th>Description</th><th>Status</th></tr>"
$Privileges = whoami /priv | Select-String -Pattern "^Se.*" | ForEach-Object { $_ -replace "\s{2,}", " " }
$Privileges | ForEach-Object {
    if ($_ -match "^(.*?) (.*?) (.*?)$") {
        $privName = $matches[1].Trim()
        $privDesc = $matches[2].Trim()
        $privStatus = $matches[3].Trim()
        $html += "<tr><td>$privName</td><td>$privDesc</td><td>$privStatus</td></tr>"
    }
}
$html += "</table>"

# Existing Users and Groups
$ExistingUsers = Get-LocalUser
$ExistingGroups = Get-LocalGroup
$html += "<h2>Existing Users</h2><table><tr><th>User Name</th><th>Status</th></tr>"
$ExistingUsers | ForEach-Object { 
    $html += "<tr><td>$($_.Name)</td><td>$($_.Enabled)</td></tr>"
}
$html += "</table>"

$html += "<h2>Existing Groups</h2><table><tr><th>Group Name</th></tr>"
$ExistingGroups | ForEach-Object { 
    $html += "<tr><td>$($_.Name)</td></tr>"
}
$html += "</table>"

# Operating System Information
$OSInfo = Get-CimInstance -ClassName Win32_OperatingSystem
$OSVersion = $OSInfo.Version
$OSArchitecture = $OSInfo.OSArchitecture
$html += "<h2>Operating System</h2><table><tr><th>Property</th><th>Value</th></tr>"
$html += "<tr><td>Operating System</td><td>$($OSInfo.Caption)</td></tr>"
$html += "<tr><td>Version</td><td>$OSVersion</td></tr>"
$html += "<tr><td>Architecture</td><td>$OSArchitecture</td></tr></table>"

# Network Information
$NetworkAdapters = Get-NetAdapter | Where-Object {$_.Status -eq "Up"}
$html += "<h2>Network Information</h2><table><tr><th>Adapter</th><th>IP Address</th><th>MAC Address</th></tr>"
$NetworkAdapters | ForEach-Object {
    $AdapterInfo = $_
    $IPAddress = (Get-NetIPAddress -InterfaceIndex $AdapterInfo.ifIndex -AddressFamily IPv4).IPAddress
    $html += "<tr><td>$($AdapterInfo.Name)</td><td>$IPAddress</td><td>$($AdapterInfo.MacAddress)</td></tr>"
}
$html += "</table>"

# ARP Table
$ARPEntries = Get-NetNeighbor -AddressFamily IPv4 | Where-Object { $_.State -eq 'Reachable' }
$html += "<h2>ARP Table</h2><table><tr><th>IP Address</th><th>MAC Address</th><th>State</th></tr>"
$ARPEntries | ForEach-Object {
    $html += "<tr><td>$($_.IPAddress)</td><td>$($_.LinkLayerAddress)</td><td>$($_.State)</td></tr>"
}
$html += "</table>"

# Listening Ports
$ListeningPorts = Get-NetTCPConnection -State Listen | Select-Object LocalAddress, LocalPort, OwningProcess
$html += "<h2>Listening Ports</h2><table><tr><th>Local Address</th><th>Local Port</th><th>Process ID</th></tr>"
$ListeningPorts | ForEach-Object { 
    $html += "<tr><td>$($_.LocalAddress)</td><td>$($_.LocalPort)</td><td>$($_.OwningProcess)</td></tr>" 
}
$html += "</table>"

# Installed Applications
$InstalledApps = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName, DisplayVersion, Publisher
$html += "<h2>Installed Applications</h2><table><tr><th>Name</th><th>Version</th><th>Publisher</th></tr>"
$InstalledApps | ForEach-Object { 
    $html += "<tr><td>$($_.DisplayName)</td><td>$($_.DisplayVersion)</td><td>$($_.Publisher)</td></tr>" 
}
$html += "</table>"

# Running Processes
$RunningProcesses = Get-Process | Select-Object Name, Id, CPU
$html += "<h2>Running Processes</h2><table><tr><th>Name</th><th>ID</th><th>CPU</th></tr>"
$RunningProcesses | ForEach-Object { 
    $html += "<tr><td>$($_.Name)</td><td>$($_.Id)</td><td>$($_.CPU)</td></tr>" 
}
$html += "</table>"

# System Uptime
try {
    $Uptime = (Get-CimInstance -ClassName Win32_OperatingSystem).LastBootUpTime
    if ($Uptime) {
        $uptimeFormatted = [Management.ManagementDateTimeConverter]::ToDateTime($Uptime).ToString("yyyy-MM-dd HH:mm:ss")
    } else {
        $uptimeFormatted = "Unavailable"
    }
} catch {
    $uptimeFormatted = "Error retrieving uptime"
}
$html += "<h2>System Uptime</h2><table><tr><th>Last Boot Time</th></tr>"
$html += "<tr><td>$uptimeFormatted</td></tr></table>"

# Scheduled Tasks
$ScheduledTasks = Get-ScheduledTask | Select-Object TaskName, TaskPath, State
$html += "<h2>Scheduled Tasks</h2><table><tr><th>Task Name</th><th>Path</th><th>Status</th></tr>"
$ScheduledTasks | ForEach-Object { 
    $html += "<tr><td>$($_.TaskName)</td><td>$($_.TaskPath)</td><td>$($_.State)</td></tr>" 
}
$html += "</table>"

# AMSI, AppLocker, and AV Information
$html += "<h2>Security Features</h2><table><tr><th>Feature</th><th>Status</th></tr>"

# AMSI Status
try {
    $amsiStatus = Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\AMSI' -Name 'Enable' -ErrorAction Stop
    $amsiStatus = if($amsiStatus.Enable -eq 1){"Enabled"}else{"Disabled"}
} catch {
    $amsiStatus = "Not Configured"
}
$html += "<tr><td>AMSI</td><td>$amsiStatus</td></tr>"

# AppLocker Rules
try {
    $appLockerRules = Get-AppLockerPolicy -Effective -ErrorAction Stop
    if ($null -eq $appLockerRules) { 
        $html += "<tr><td>AppLocker</td><td>No Policy Found</td></tr>" 
    } else { 
        $html += "<tr><td>AppLocker</td><td>Rules Found</td></tr>" 
    }
} catch {
    $html += "<tr><td>AppLocker</td><td>Error Retrieving Policy</td></tr>"
}

# Antivirus Information
$avProducts = Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct
if ($avProducts) {
    $avProducts | ForEach-Object {
        $html += "<tr><td>Antivirus</td><td>$($_.displayName) - $($_.productState)</td></tr>"
    }
} else {
    $html += "<tr><td>Antivirus</td><td>No Product Found</td></tr>"
}

$html += "</table>"

# User Shell History
$html += "<h2>User Shell History</h2>"

$html += "<h3>PowerShell History</h3>"
$PSHistoryPath = "$env:APPDATA\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt"
if (Test-Path $PSHistoryPath) {
    $PSHistory = Get-Content $PSHistoryPath
    $html += "<pre>"
    $PSHistory | ForEach-Object { $html += "$_`n" }
    $html += "</pre>"
} else {
    $html += "<p>No PowerShell history found.</p>"
}

$html += "<h3>CMD History</h3>"
try {
    $CMDHistory = doskey /history
    if ($CMDHistory) {
        $html += "<pre>$CMDHistory</pre>"
    } else {
        $html += "<p>No CMD history found.</p>"
    }
} catch {
    $html += "<p>Error retrieving CMD history.</p>"
}

# End HTML
$html += @"
</body>
</html>
"@

# Output to HTML file
$html | Out-File -FilePath $outputHtmlFile

# Inform the user
Write-Output "HTML report has been generated and saved to $outputHtmlFile"
