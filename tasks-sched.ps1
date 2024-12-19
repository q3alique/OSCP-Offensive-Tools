Get-ScheduledTask | ForEach-Object {
    $task = $_
    $taskInfo = Get-ScheduledTaskInfo -TaskName $task.TaskName -TaskPath $task.TaskPath
    $task.Actions | Where-Object { $_.Execute -like "*.exe" } | ForEach-Object {
        [PSCustomObject]@{
            TaskName     = $task.TaskName
            NextRunTime  = $taskInfo.NextRunTime
            Author       = $task.Principal.UserId
            TaskToRun    = "$($_.Execute) $($_.Arguments)"
        }
    }
} | Format-List | Out-String -Width 4096 | Out-File "ScheduledTasks.txt"
