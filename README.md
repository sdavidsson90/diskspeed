## Considerations for timing things

### Multiple measures for time
Consider `time`:

```
real    0m2.034s
user    0m1.876s
sys     0m0.120s
```

* Real: time from initial command execution to completion
* User: CPU time (user scripts, applications)
* Sys: Kernel tasks (file i/o, network, devices, processes, memory, )

Do also note that `real` time can be greater than `user` + `sys`, when processes are multithreaded.

### Multiple versions of time
Do also note that the first hit for time i ususally the shell builtin, but that there is usually also a program called `/usr/bin/time`.

```
❯ type -a time
time is a reserved word
time is /usr/bin/time
```

They all differ in their output but measure the same:

ZSH built-in: `zsh -c "time ls"`
bash built-in: `bash -c "time ls"`
MacOS BSD time: `/usr/bin/time ls`
GNU time: `gtime ls`

### In the context of building a disk speed measurement with Python

Disk speed is I/O - a kernel task. We want high precision

time.perf_counter() for higher precision

