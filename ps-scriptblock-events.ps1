$eventIds = @(4104, 4105)
$logName = "Microsoft-Windows-PowerShell/Operational"
$outputFile = Join-Path -Path (Get-Location) -ChildPath "ps-script-events.txt"
Clear-Content -Path $outputFile -ErrorAction SilentlyContinue
$events = Get-WinEvent -LogName $logName -FilterHashtable @{Id=$eventIds}
foreach ($event in $events) {
    $eventDetails = @"
Event Time: $($event.TimeCreated)
Event ID: $($event.Id)
Provider Name: $($event.ProviderName)
Message: $($event.Message)

"@
    Add-Content -Path $outputFile -Value $eventDetails
}
Write-Output "Event details have been saved to $outputFile"
