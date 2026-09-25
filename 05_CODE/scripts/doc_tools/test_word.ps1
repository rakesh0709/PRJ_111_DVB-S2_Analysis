try {
    $word = New-Object -ComObject "Word.Application"
    Write-Host "Word COM is available: $($word.Version)"
    $word.Quit()
} catch {
    Write-Host "Word COM not available: $($_.Exception.Message)"
}
