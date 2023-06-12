# Disable screen-lock and sleep on Windows

Python GUI application to turn on/off screen-lock and sleep on Windows

Uses `SetThreadExecutionState` with `ES_CONTINUOUS` see [SetThreadExecutionState](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setthreadexecutionstate)


## TODO:


### Implement CLI args:

    subcommand, required: gui / cmd 

Args:

    --duration=0, in minutes
    --refresh_interval=60, Default = 60 sec
    --method="NumLock" / "ThreadExecState (TES ?)"
    --suspend-on-start=True


### Implement cmd subcommand
    Choose CLI or GUI mode by passing args


### Settings panel

    [ ] minimize to system tray (Don't ask again)

    [ ] change theme

    [x] start with windows - implemented .bat and .vbs files

    [ ] save settings to user profile, remember window position + last used method, theme etc. 

### Tests and CI/CD

    - unit test
    - flake8, mypy, tox
    - git hooks
    - github actions


### Update README

     - Usage / how-to install section

### Create v1.0.0
    [ ]