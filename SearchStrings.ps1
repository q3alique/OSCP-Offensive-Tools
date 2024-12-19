<#
.SYNOPSIS
    A PowerShell script to search for files and strings matching specified terms.

.DESCRIPTION
    Searches for files in a specified folder (or all folders) that match given terms. 
    It can also search within the contents of these files for matching strings.
#>

function Print-Logo {
    Write-Host @"
   / \__
  (    @\___
  /         O
 /   (_____/
 /_____/   U
"@ -ForegroundColor Yellow
    Write-Host "string sEaRchIng tool 1.0.1 by q3alique" -ForegroundColor Cyan -Bold
}

function Get-SearchTerms {
    $defaultTerms = @('password', 'pass', 'credentials', 'config', 'creds')
    Write-Host "`nDefault list of terms:" -ForegroundColor Cyan
    $defaultTerms | ForEach-Object { Write-Host " - $_" -ForegroundColor Cyan }
    $choice = Read-Host "Do you want to use the default list of terms? (yes/no)"
    if ($choice -eq 'yes') {
        return $defaultTerms
    } else {
        $terms = Read-Host "Enter your own list of terms separated by spaces"
        return $terms -split '\s+'
    }
}

function Find-FilesWithTerms {
    param (
        [string[]]$Terms,
        [string]$Folder,
        [bool]$Recursive = $true
    )
    $foundFiles = @()
    $inaccessibleFiles = @()

    $rootFolder = if ($Folder -eq 'current') {
        Get-Location
    } elseif ($Folder -eq 'all') {
        "C:\"
    } else {
        $Folder
    }

    $searchOption = if ($Recursive) { "-Recurse" } else { "" }

    Get-ChildItem -Path $rootFolder -File $searchOption -ErrorAction SilentlyContinue |
    ForEach-Object {
        $filePath = $_.FullName
        try {
            foreach ($term in $Terms) {
                if ($_.Name -like "*$term*") {
                    $foundFiles += $filePath
                    break
                }
            }
        } catch {
            $inaccessibleFiles += $filePath
        }
    }

    # Save results to files
    $foundFiles | Out-File -FilePath "found_files.txt"
    $inaccessibleFiles | Out-File -FilePath "inaccessible_files.txt"
}

function Search-StringsInFiles {
    param (
        [string[]]$Terms
    )
    $results = @()

    if (-Not (Test-Path "found_files.txt")) {
        Write-Host "No 'found_files.txt' file found. Skipping string search." -ForegroundColor Red
        return
    }

    Get-Content "found_files.txt" | ForEach-Object {
        $filePath = $_
        try {
            Get-Content -Path $filePath -ErrorAction SilentlyContinue |
            ForEach-Object -Begin { $lineNumber = 1 } -Process {
                foreach ($term in $Terms) {
                    if ($_ -match [regex]::Escape($term)) {
                        $results += "${filePath}:${lineNumber}: $_"
                        break
                    }
                }
                $lineNumber++
            }
        } catch {
            Write-Host "Error accessing file: $filePath" -ForegroundColor Yellow
        }
    }

    # Save results
    $results | Out-File -FilePath "matched_strings.txt"
}

function Main {
    Print-Logo

    # Menu
    Write-Host "`nOptions:" -ForegroundColor Yellow
    Write-Host "1. Examine current folder" -ForegroundColor Yellow
    Write-Host "2. Examine all folders" -ForegroundColor Yellow
    Write-Host "3. Specify a folder to examine" -ForegroundColor Yellow

    $choice = Read-Host "Enter your choice (1, 2, or 3)"
    $folderChoice = switch ($choice) {
        '1' { 'current' }
        '2' { 'all' }
        '3' { Read-Host "Enter the folder path to examine" }
        default { Write-Host "Invalid choice. Exiting." -ForegroundColor Red; exit }
    }

    # Get search terms
    $terms = Get-SearchTerms

    # Get search options
    $recursive = (Read-Host "Do you want to examine recursively? (yes/no)").ToLower() -eq 'yes'

    # Find files containing the terms in the name
    Write-Host "Searching for files..." -ForegroundColor Yellow
    Find-FilesWithTerms -Terms $terms -Folder $folderChoice -Recursive $recursive

    # Search for strings in the found files
    Write-Host "Searching for matching strings within files..." -ForegroundColor Yellow
    Search-StringsInFiles -Terms $terms

    Write-Host "`nMatching strings have been saved to 'matched_strings.txt'." -ForegroundColor Green
}

# Run the main function
Main
