# TODO

## Implement CLI args:

    subcommand, required: gui / cmd 

Args:

    --duration=0, in minutes
    --refresh_interval=60, Default = 60 sec
    --method="NumLock" / "ThreadExecState (TES ?)"
    --suspend-on-start=True


## Implement cmd subcommand
    Choose CLI or GUI mode by passing args


## Settings panel


    [ ] change theme

    [x] start with windows - implemented .bat and .vbs files

    [-] save settings to user profile - 
    
        [x] window position + last used method, 
        [ ] use system or custom theme etc. 
        [ ] minimize to system tray (Don't ask again)

## Tests and CI/CD

    - unit test
    - flake8, mypy, tox
    - git hooks
    - github actions


## Update README

     - Usage / how-to install section

## Create v1.0.0
    [ ]


## Bugs

    - [ ] prevent multiple app instances
