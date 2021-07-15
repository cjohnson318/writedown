# writedown

This is very much a work in progress.

The general idea is that you organize notes by "context" on a daily basis. A
context might be `client/project`, `home/insurance`, or `music/bebop`, etc.
There is a default context called `daily` for quick, general notes.

Notes stored on disk in a user-defined root directory. The "contexts" described
above are represented by relative paths from this root directory. By default,
the root directory is `~/notes`, so the `daily` context would map to the
`~/notes/daily/` directory. The individual daily notes are simply markdown
files named by the currrent date as `%Y-%m-%d.md`.

When you run the `wd` command with a context, it will create or open a markdown
file in the appropriate directory.

## Installation

Git clone this project, and `cd` into the project.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r src/requirements.txt
```

Add the following to your `.bashrc`, `.zshrc`, etc., replacing `/path/to` with
the path to wherever you git cloned the `writedown` project.

```bash
alias le="/path/to/writedown/venv/bin/python3 /path/to/writedown/src/app.py wd"
```

Add a config file at `~/.writedown/config.yaml` with the keys,
  - `ROOT`
  - `DEFAULT_EDITOR`
  - `DEFAULT_CONTEXT`

Here is an example,

```yaml
ROOT: /Users/someuser/notes
DEFAULT_EDITOR: vim
DEFAULT_CONTEXT: daily
```

This instructs the application to create or use the directory `~/notes` in my
home directory, use `vim` for editing, and have a default directory for quick,
unorganized notes called `daily`.

## Features

### Making a quick note

To create a quick note in your default context:

```bash
wd
```

This will open an editor that creates orr edits a markdown file for the current
day.

To add a note to a specific context, provide that context starting with a
forward slash:

```bash
wd client/project
```

### See your directory tree

To see the overall structure of your root directory:

```bash
wd -d
wd --dirs
```

This will use the \*nix `tree` utility, assuming it is installed.

To see the content of all of your notes under a specific context:

### Show (concatenate) all of your notes for a context

```bash
wd -s client/project
wd --show client/project
```

You will see the date of each note, and its contents, ordered so that the
latest notes are on the top.

This output can be piped into `cat`, `grep`, etc. for further processing.

### Todo list functionality

This uses the [todo.txt](http://todotxt.org/) syntax.

Open `todo.txt`, using the `-t` flag. This will open a vim editor.

```bash
wd -t
wd --todo
```

Query `todo.txt` by priority,

```bash
wd -q p
wd -q priority
```

Query `todo.txt` by project(s), with priority or not,

```bash
wd -q +home
wd -q p +home +garden
```

Query `todo.txt` by context.

```bash
wd -q @phone
wd -q p @phone +home
```

> Here, context refers to the context described by
> [todo.txt](http://todotxt.org/), not the way I use context above. I added
> todo list functionality to this project after I started losing track of todos
> in individual notes. I decided that I needed to separate note taking from
> todos. I decided on using the `todo.txt` syntax because it was easy to parse,
> easy to use, and already established.
