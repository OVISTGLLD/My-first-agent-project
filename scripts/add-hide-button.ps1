$f = 'D:\Photography\index.html'
$c = [IO.File]::ReadAllText($f, [Text.Encoding]::UTF8)
$old = 'exportEdits()")">导出数据库</button>'
$new = 'exportEdits()")">导出数据库</button><button class="btn btn-outline" style="border-bottom-color:#c30;color:#c30;margin-left:24px;" onclick="window.hideFromArchive(\''+p.file+'\')")">从档案中隐藏</button>'
if ($c.Contains($old)) {
    $c = $c.Replace($old, $new)
    [IO.File]::WriteAllText($f, $c, [Text.Encoding]::UTF8)
    Write-Host "Done - button added"
} else {
    Write-Host "NOT FOUND - trying alternate"
    $old2 = 'exportEdits()")">导出数据库</button>'
    if ($c.Contains($old2)) {
        Write-Host "Found alternate"
    }
}