while ($true) {
    $process = Start-Process -FilePath "cmd" -ArgumentList "/c python D:\python\voice_to_text\whisper\work.py" -NoNewWindow -PassThru
    $process.WaitForExit()
    $EXIT_CODE = $process.ExitCode
    if ($EXIT_CODE -ne 0) {
        Write-Host "Program crashed with exit code $EXIT_CODE, restarting"
    }
    else {
        Write-Host "Program finished successfully, no actions needed"
        break
    }
}