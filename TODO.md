# TODO

## Implement subcommands `gui`, `cmd` and `stop`

    Choose CLI or GUI mode and handle passing args

    [x] subcommands `gui`, `cmd` and `stop`
    [x] call `cli` with args:

        --duration=0, in minutes
        --refresh_interval=60, Default = 60 sec
        --method="NumLock" / "ThreadExecState"


## Settings panel

    [ ] change theme
    [x] start with windows - implemented .bat and .vbs files
    [-] save settings to user profile - 
        [x] window position + last used method, 
        [ ] use system or custom theme etc. 
        [ ] when, minimizing to system tray, show "Don't ask again" dialog

## Tests and CI/CD

    [ ] unit test
    [ ] flake8, mypy, tox
    [ ] git hooks
    [ ] github actions


## Update README

     [ ] Usage / how-to install section

## Create v1.0.0
    [ ]


## Bugs

    [x] prevent multiple app instances
