# Disable screen-lock and sleep on Windows

Python GUI application to turn on/off screen-lock and sleep on Windows

Uses `SetThreadExecutionState` with `ES_CONTINUOUS` see [SetThreadExecutionState](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setthreadexecutionstate)


## TODO:

### Implement CLI args:

subcommand, required:
    gui / cmd 

Args:
    --duration=0, in minutes
    --refresh_interval=60, Default = 60 sec
    --method="NumLock" / 
    --suspend-on-start=True


### Implement cmd subcommand


### Add tests