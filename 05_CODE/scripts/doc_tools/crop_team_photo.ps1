Add-Type -AssemblyName System.Drawing

$rootDir = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$srcPath = Join-Path $rootDir "07_DOCUMENTATION\RESEARCH_PAPER\assets\team_presentation.jpg"
$dstPath = Join-Path $rootDir "07_DOCUMENTATION\RESEARCH_PAPER\assets\team_presentation_cropped.jpg"

$bmp = New-Object System.Drawing.Bitmap($srcPath)

# We want to crop out the GPS overlay.
# The original image is 1600 x 1200.
# The overlay is at the bottom, below y = 780.
# Let's crop Rectangle(0, 0, 1600, 780)
$cropRect = New-Object System.Drawing.Rectangle(0, 0, 1600, 780)
$croppedBmp = $bmp.Clone($cropRect, $bmp.PixelFormat)

# Save with high quality JPEG
$encoder = [System.Drawing.Imaging.Encoder]::Quality
$encoderParams = New-Object System.Drawing.Imaging.EncoderParameters(1)
$encoderParams.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter($encoder, [long]95)
$codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }

$croppedBmp.Save($dstPath, $codec, $encoderParams)

Write-Host "Cropped image saved successfully to $dstPath"
Write-Host "Cropped dimensions: $($croppedBmp.Width) x $($croppedBmp.Height)"

$croppedBmp.Dispose()
$bmp.Dispose()
