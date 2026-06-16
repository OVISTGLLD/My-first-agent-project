$f = 'D:\Photography\index.html'
$c = [IO.File]::ReadAllText($f, [Text.Encoding]::UTF8)

# The exact text to find (inside navigateToSingle JS string)
$old = '</button></div></div></div>'';document.querySelectorAll'

# The replacement - insert hide button BEFORE export button's closing
$hide = '<button class="btn btn-outline" style="border-bottom-color:#c30;color:#c30;margin-left:24px;" onclick="window.hideFromArchive(\'+p.file+')">从档案中隐藏</button>'

if ($c -match [regex]::Escape('导出数据库</button>')) {
    Write-Host "Found export button"
} else {
    Write-Host "ERROR: export button not found"
}

# Check for broken button from earlier attempt
if ($c -match '<button class') {
    Write-Host "WARNING: Found broken HTML entity button from previous attempt - removing it"
    $c = $c -replace '<button class="btn btn-outline" style="border-bottom-color:#c30;color:#c30;margin-left:24px;" onclick="window.hideFromArchive\(\\'\+p\.file\+\\'\)">从档案中隐藏</button>', ''
    [IO.File]::WriteAllText($f, $c, [Text.Encoding]::UTF8)
    Write-Host "Removed broken button"
} else {
    Write-Host "No broken button found - inserting new one"
    # The old text pattern before insertion
    $pattern = '">导出数据库</button>'
    $replacement = '">导出数据库</button>' + $hide
    if ($c -match [regex]::Escape($pattern)) {
        $c = $c -replace [regex]::Escape($pattern), $replacement
        [IO.File]::WriteAllText($f, $c, [Text.Encoding]::UTF8)
        Write-Host "Button inserted successfully"
    } else {
        Write-Host "Pattern not found. Checking context..."
        # Debug: find the area around export button
        $idx = $c.IndexOf('导出数据库')
        if ($idx -gt 0) {
            $context = $c.Substring([Math]::Max(0, $idx - 100), 200)
            Write-Host "Context around export button:"
            Write-Host $context
        }
    }
}