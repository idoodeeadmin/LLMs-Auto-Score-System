$ErrorActionPreference = 'Stop'

$docxPath = 'C:\Users\idood\Downloads\LLMs-Auto-Score-System-main\docs_and_tests\LLMs_Auto_Score_Systems_Pro1_1-5_edited.docx'
$pdfPath = 'C:\Users\idood\Downloads\LLMs-Auto-Score-System-main\qa_docx_correct\LLMs_Auto_Score_Systems_Pro1_1-5_edited.pdf'
$jsonPath = 'C:\Users\idood\Downloads\LLMs-Auto-Score-System-main\qa_docx_correct\pagination.json'
New-Item -ItemType Directory -Force -Path (Split-Path $pdfPath) | Out-Null

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$doc = $null
try {
    $doc = $word.Documents.Open($docxPath, $false, $false)
    $doc.Repaginate()

    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    foreach ($tof in $doc.TablesOfFigures) { $tof.Update() }
    $doc.Fields.Update() | Out-Null
    foreach ($story in $doc.StoryRanges) {
        $range = $story
        while ($null -ne $range) {
            $range.Fields.Update() | Out-Null
            $range = $range.NextStoryRange
        }
    }

    $doc.Repaginate()
    $doc.Save()
    $doc.ExportAsFixedFormat($pdfPath, 17)

    $paragraphPages = @()
    $paragraphIndex = 0
    $paragraphCount = $doc.Paragraphs.Count
    foreach ($paragraph in $doc.Paragraphs) {
        $paragraphIndex++
        $text = ($paragraph.Range.Text -replace '[\r\a]', '').Trim()
        if (($paragraphIndex -gt ($paragraphCount - 30)) -and ($text.Length -gt 0)) {
            $paragraphPages += [pscustomobject]@{
                Index = $paragraphIndex
                Text = $text
                Page = $paragraph.Range.Information(3)
            }
        }
    }

    $tablePages = @()
    for ($i = [Math]::Max(1, $doc.Tables.Count - 1); $i -le $doc.Tables.Count; $i++) {
        $tablePages += [pscustomobject]@{
            Table = $i
            StartPage = $doc.Tables.Item($i).Range.Information(3)
            EndPage = $doc.Tables.Item($i).Range.Characters.Last.Information(3)
        }
    }

    [pscustomobject]@{
        TotalPages = $doc.ComputeStatistics(2)
        ParagraphPages = $paragraphPages
        BiographyTables = $tablePages
    } | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 $jsonPath
}
finally {
    if ($null -ne $doc) { $doc.Close($false) }
    $word.Quit()
    if ($null -ne $doc) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) }
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
