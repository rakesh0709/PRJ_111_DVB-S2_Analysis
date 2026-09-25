$word = New-Object -ComObject "Word.Application"
$word.Visible = $false
$word.DisplayAlerts = 0 # wdAlertsNone
try {
    $docPath = Join-Path (Get-Location) "test_2col.docx"
    $doc = $word.Documents.Open($docPath, $false, $true, $false)
    Write-Host "Opened successfully. Paragraphs: $($doc.Paragraphs.Count), Sections: $($doc.Sections.Count)"
    $pdfPath = Join-Path (Get-Location) "test_2col.pdf"
    $doc.ExportAsFixedFormat($pdfPath, 17) # 17 = wdExportFormatPDF
    Write-Host "Exported to PDF successfully."
    $doc.Close([ref]0) # wdDoNotSaveChanges
} catch {
    Write-Host "Error: $($_.Exception.Message)"
} finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
