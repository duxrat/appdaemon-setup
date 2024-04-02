This repository contains a fork of [appdaemon](https://github.com/AppDaemon/appdaemon) with added:

- code for my automations at `/conf/apps`
- heavy customizations/wrappers for core elements of appdaemon API that make it more ergonomic/clean to write automations with (especially listening to changes in multiple events)
- deploy script in the `Makefile`

I managed to set up a workflow where appdaemon source code runs alongside automations code for easy customization/debugging. Most importantly, this way it's possible to run it directly in the IDE and have access to the debugger while developing on the local copy of automations.

Once happy with automations, deploy script copies their code into whatever server is running it. Apps are loaded conditionally based on HA input_boolean's as configured in apps.yaml, so it's easy to switch them between dev and live mode.

---

AppDaemon is a loosely coupled, multi-threaded, sandboxed python
execution environment for writing automation apps for various types of Home Automation Software including [Home
Assistant](https://home-assistant.io/) and MQTT. It has a pluggable architecture allowing it to be integrated with
practically any event driven application.

It also provides a configurable dashboard (HADashboard)
suitable for wall mounted tablets.

## Getting started

For full instructions on installation and usage check out the [AppDaemon Project Documentation](http://appdaemon.readthedocs.io).

## Release Cycle Frequency

AppDaemon has reached a very stable point, works reliably and is fairly feature rich at this point
in its development. For that reason, releases have been slow in recent months. This does not mean that AppDaemon has been abandoned -
 it is used every day by the core developers and has an active discord server [here](https://discord.gg/qN7c7JcFjk) - please join us for tips
and tricks, AppDaemon discussions and general home automation.

## Contributing

This is an active open-source project. We are always open to people who want to use the code or contribute to it. Thank you for being involved!
Have a look at the [official documentation](https://appdaemon.readthedocs.io/en/latest/DEV.html) for more information.
