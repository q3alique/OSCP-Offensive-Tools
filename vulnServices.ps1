function Get-ModifiableServiceFile {
    [CmdletBinding()]
    Param()

    # Get the current user and their groups
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $userGroups = $currentUser.Groups | ForEach-Object { $_.Translate([System.Security.Principal.NTAccount]).Value }

    # Escape special characters in user groups for regex
    $escapedGroups = $userGroups | ForEach-Object { [regex]::Escape($_) }

    # Get all services
    $services = Get-WMIObject -Class win32_service | Where-Object { $_ -and $_.pathname }

    # Iterate over services and check permissions
    foreach ($service in $services) {
        $serviceName = $service.Name
        $servicePath = $service.PathName
        $serviceStartName = $service.StartName

        # Extract the binary path considering quotes and spaces
        if ($servicePath -match '^"([^"]+)"') {
            $binaryPath = $matches[1]
        } else {
            $binaryPath = $servicePath.Split(" ")[0]
        }

        if (Test-Path -Path $binaryPath) {
            $permissions = icacls $binaryPath 2>&1

            foreach ($line in $permissions) {
                foreach ($group in $escapedGroups) {
                    if ($line -match "${group}:\((.*)\)") {
                        $rights = $matches[1]
                        if ($rights -match "F" -or $rights -match "W") {
                            $output = New-Object PSObject
                            $output | Add-Member -MemberType NoteProperty -Name 'ServiceName' -Value $serviceName
                            $output | Add-Member -MemberType NoteProperty -Name 'Path' -Value $binaryPath
                            $output | Add-Member -MemberType NoteProperty -Name 'Permissions' -Value $line
                            $output.PSObject.TypeNames.Insert(0, 'PowerUp.ModifiableServiceFile')
                            $output

                            Write-Output "Service: $serviceName, State: $($service.State)"
                            Write-Output "Path: $binaryPath"
                            Write-Output $line
                            Write-Output "----------------------------------------"
                        }
                    }
                }
            }
        } else {
            Write-Warning "Binary path not found for service '$serviceName': $binaryPath"
        }
    }
}

# Run the function
Get-ModifiableServiceFile
