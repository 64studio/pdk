# Installation

These instructions have been tested on Debian Stretch/Buster/Sid on amd64 systems only.
We recommend running PDK inside a clean virtual machine.

```
$ sudo apt install apt-transport-https
$ echo 'deb https://apt.64studio.net stretch main' | sudo tee /etc/apt/sources.list.d/64studio.list
$ wget -qO - https://apt.64studio.net/archive-keyring.asc | sudo apt-key add -
$ sudo apt update
$ sudo apt install pdk pdk-mediagen
```


# Create APT Repository Key

A seperate key may be used to sign each project.
To enable automated builds later, either do not set a passphrase when you generate the key (less secure), or automate signing with gpg-preset-passphrase running on each boot.
Ignore the rng-tools error "Cannot find a hardware RNG device to use".

```
$ sudo apt-get install rng-tools
$ sudo rngd -r /dev/urandom
$ gpg --gen-key
```

Next: [Getting Started](GettingStarted.md)
