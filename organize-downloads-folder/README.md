# Capti

A simple file orchestration tool to manage and organize your files. Best
suitable for everyday mudane task like cataloging your file base on extensions
/ prefix name ,add filters for specific file , create file listeners and more.

# Dependencies

- pyyaml
- python [3.11]

# Configurations

- sample format :

```yaml
folder: "/home/lusamreth/Downloads"
mode: "copy"
blocks:
  - name: "picture-block"
    ext:
      - jpeg
      - png
    directory: "Pictures"
    skip: "Telegram Desktops"
```

There are 3 majors components in config : ** folder,mode,blocks **

## block

The block contains all the associate setting related to a cluster of extensions
or filter (name,type,date). It can be customize with additional paramsasuch as
skip and directory to achieve the desire behavoir.

## name

An unique identifier for each individual block. It will be useful to use for
making custom hooks for a specific events / combine operations.

## folder

contains the root of the directory that the crawler will see. From the it will
scan the directory via a scantree generators.

# TODO LIST :

- create a reversible state using checksum (for backups)
- create a skip scanner of folder / files
- add "move / delete" function
