Add-Type -AssemblyName System.Drawing

$rootDir = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$srcPath = Join-Path $rootDir "07_DOCUMENTATION\RESEARCH_PAPER\assets\team_presentation.jpg"
$dstPath = Join-Path $rootDir "07_DOCUMENTATION\RESEARCH_PAPER\assets\team_presentation_cropped.jpg"

$bmp = New-Object System.Drawing.Bitmap($srcPath)
Write-Host "Image Size: $($bmp.Width) x $($bmp.Height)"

# Scan from bottom to find the top of the dark/white GPS overlay box
# In GPS Map Camera, the banner at the bottom has a distinct sharp border
# Let's inspect along multiple x columns: 400, 800, 1200
for ($y = 1190; $y -ge 700; $y -= 10) {
    $c = $bmp.GetPixel(800, $y)
    Write-Host "y=$y Color: R=$($c.R) G=$($c.G) B=$($c.B)"
}

$bmp.Dispose()
