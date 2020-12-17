# Web Monitor

This package exports a script which allow the user to watch web pages for changes from a `cron` script. One cron job to get it running:


`0 0-23/8 * * * XDG_RUNTIME_DIR=/run/user/$(id -u) web-monitor`
