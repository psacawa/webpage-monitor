# Web Monitor

This package exports a script which allow the user to watch web pages for changes from a `cron` script. One way to get it running:


`* * * * * XDG_RUNTIME_DIR=/run/user/$(id -u) web-monitor`
