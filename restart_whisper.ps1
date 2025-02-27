while ($true) {
    $process = Start-Process -FilePath "cmd" -ArgumentList "/c python D:\python\voice_to_text\whisper\work.py" -NoNewWindow -PassThru
    $process.WaitForExit()
    $EXIT_CODE = $process.ExitCode
    if ($EXIT_CODE -ne 0) {
        Write-Host "Program crashed with exit code $EXIT_CODE, removing problematic file and restarting"
        if ((Test-Path D:\python\voice_to_text\whisper\errors.log) -and ((Get-Content D:\python\voice_to_text\whisper\errors.log) -ne $null)) {
            $PROBLEM_FILE = Get-Content D:\python\voice_to_text\whisper\errors.log -Tail 1
            Remove-Item $PROBLEM_FILE -ErrorAction SilentlyContinue
        }
    }
    else {
        Write-Host "Program finished successfully, no actions needed"
        break
    }
}