# PowerShell 图片处理脚本
# 将 image-original 中的原图压缩后输出到 images 文件夹
# 使用 .NET Framework 内置的 System.Drawing（无需安装额外组件）

param(
    [string]$SourceDir = "image-original",
    [string]$TargetDir = "images",
    [int]$MaxSize = 2000,
    [int]$Quality = 80
)

Add-Type -AssemblyName System.Drawing

$sourcePath = Join-Path $PSScriptRoot ".." $SourceDir
$targetPath = Join-Path $PSScriptRoot ".." $TargetDir

New-Item -ItemType Directory -Force -Path $targetPath | Out-Null
New-Item -ItemType Directory -Force -Path $sourcePath | Out-Null

$processed = 0
$skipped = 0
$errors = 0

Get-ChildItem -Path $sourcePath -File | ForEach-Object {
    $ext = $_.Extension.ToLower()
    if ($ext -notin '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif') {
        return
    }

    $targetName = [System.IO.Path]::ChangeExtension($_.Name, '.jpg')
    $targetFile = Join-Path $targetPath $targetName

    if (Test-Path $targetFile) {
        Write-Host "跳过（已存在）: $targetName"
        $skipped++
        return
    }

    try {
        $img = [System.Drawing.Image]::FromFile($_.FullName)
        $w = $img.Width
        $h = $img.Height

        # 长边限制
        if ($w -ge $h) {
            if ($w -gt $MaxSize) {
                $ratio = $MaxSize / $w
                $h = [int]($h * $ratio)
                $w = $MaxSize
            }
        } else {
            if ($h -gt $MaxSize) {
                $ratio = $MaxSize / $h
                $w = [int]($w * $ratio)
                $h = $MaxSize
            }
        }

        $bmp = New-Object System.Drawing.Bitmap $w, $h
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $g.DrawImage($img, 0, 0, $w, $h)

        # JPG 编码器
        $encoder = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
        $encoderParams = New-Object System.Drawing.Imaging.EncoderParameters(1)
        $encoderParams.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter @(
            [System.Drawing.Imaging.Encoder]::Quality,
            $Quality
        )

        $bmp.Save($targetFile, $encoder, $encoderParams)
        $bmp.Dispose()
        $img.Dispose()
        $g.Dispose()

        Write-Host "处理完成: $($_.Name) → $targetName ($w×$h)"
        $processed++
    } catch {
        Write-Host "错误: $($_.Name) - $_"
        $errors++
    }
}

Write-Host ""
Write-Host "--- 完成 ---"
Write-Host "处理: $processed 张"
Write-Host "跳过: $skipped 张"
Write-Host "错误: $errors 张"