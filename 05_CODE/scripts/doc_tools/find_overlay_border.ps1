Add-Type -AssemblyName System.Drawing

$rootDir = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$srcPath = Join-Path $rootDir "07_DOCUMENTATION\RESEARCH_PAPER\assets\team_presentation.jpg"
$bmp = New-Object System.Drawing.Bitmap($srcPath)

for ($y = 770; $y -le 805; $y++) {
    $c1 = $bmp.GetPixel(400, $y)
    $c2 = $bmp.GetPixel(800, $y)
    $c3 = $bmp.GetPixel(1200, $y)
    Write-Host "y=$y | x400: ($($c1.R),$($c1.G),$($c1.B)) | x800: ($($c2.R),$($c2.G),$($c2.B)) | x1200: ($($c3.R),$($c3.G),$($c3.B))"
}

$bmp.Dispose()
