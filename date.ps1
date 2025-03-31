$dateFilePath = "C:\date.txt"

$todayDate = (Get-Date).ToString("dd/MM/yyyy")

if (Test-Path $dateFilePath) {
    # Read the first line of the file
    $firstLine = Get-Content -Path $dateFilePath -TotalCount 1

    if ($firstLine -eq $todayDate) {
        Write-Output "OK - La première ligne contient la date du jour."
        exit 0
    } else {
        Write-Output "WARNING - La première ligne ne contient pas la date du jour."
        exit 1
    }
} else {
    Write-Output "CRITICAL - Le fichier date.txt n'existe pas."
    exit 2
}