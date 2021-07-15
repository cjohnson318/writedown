import argparse
import datetime
import pathlib
import subprocess
from typing import Dict, List

from icecream import ic
import yaml

ic.configureOutput(includeContext=True)
ic.disable()

CONFIG_DIRECTORY = '.writedown'

def get_config() -> Dict:
    '''Load YAML config file.
    '''
    home_dir = pathlib.Path.home()
    config_dir = pathlib.PurePath(home_dir, CONFIG_DIRECTORY, 'config.yaml')
    loader = yaml.SafeLoader
    config = yaml.load(open(str(config_dir), 'r'), Loader=loader)
    return config

def get_default_context() -> str:
    '''Get name of default context: 'daily'.
    '''
    result = config.get('DEFAULT_CONTEXT')
    if result is None:
        raise RuntimeError('"DEFAULT_CONTEXT" is not defined in "~/.writedown/config.yaml"')
    return result

def create_home(config: Dict) -> pathlib.Path:
    '''Create root directory if it does not exist.
    '''
    home = pathlib.Path(config.get('ROOT'))
    if not home.exists():
        home.mkdir(parents=True)
    return home

def create_dir(path: pathlib.Path) -> None:
    '''Create a new context if it does not exist.
    '''
    parent = pathlib.Path(path).parent
    if not pathlib.Path(parent).exists():
        pathlib.Path(parent).mkdir(parents=True)

def create_path(args) -> str:
    '''Create a path to today's file in a given context.
    '''
    location = None
    if args.context is None:
        location = pathlib.Path(home, get_default_context())
    else:
        location = pathlib.Path(home, args.context)
    filename = datetime.date.today().strftime('%Y-%m-%d')
    path = pathlib.Path(home, location, filename + '.md')
    result = str(path)
    return result

def get_tree():
    '''Use `tree` command to print out directory structure, sans `*.md`.
    '''
    subprocess.call(['tree', '-I', '*.md', home])

def open_editor(path: str):
    editor = config.get('DEFAULT_EDITOR')
    if editor == 'vim' or editor is None:
        normal_G = '+normal G$'
        start_insert = '+startinsert'
        cmd = [editor, normal_G, start_insert, path]
    else:
        cmd = [editor, path]
    subprocess.call(cmd)

def get_editor(args):
    '''Open the configured editor, or vim by default.
    '''
    if args.context is None:
        path = create_path(args)
        create_dir(path)
    else:
        if pathlib.Path(home, args.context).is_file():
            path = str(pathlib.Path(home, args.context))
        elif pathlib.Path(home, args.context + '.md').is_file():
            path = str(pathlib.Path(home, args.context + '.md'))
        else:
            path = create_path(args)
            create_dir(path)
    open_editor(path)

def get_parent_context(path: pathlib.Path, item: pathlib.Path) -> str:
    '''Return a string describing a context, or path, relative to notes home.
    '''
    home_path_parents = len(home.parents)
    current_path_parents = len(item.parents)
    show_parents = current_path_parents - home_path_parents - 1
    parents = [item.parents[i].name for i in range(show_parents)]
    parents = ' /' + '/'.join(parents[::-1])
    return parents

def show_context(args):
    '''Print all markdown in a directory.
    '''
    if args.show == 'todo':
        show_todo()
        return
    path = pathlib.Path(home, args.show)
    if path.is_file():
        raise ValueError(f'The path {str(path)} points to a file. Specify a directory instead.')
    elif path.is_dir():
        print(f'# {path.resolve()}\n')
        items = [it for it in path.rglob('*') if it.is_file() and it.suffix=='.md']
        items = sorted(items, key=lambda x: x.name)
        for item in items:
            parents = get_parent_context(path, item)
            print(f'## {item.name[:-3]}{parents}\n')
            with open(item.resolve()) as fh:
                for line in fh:
                    print(line.rstrip())
                print()

def get_file(args):
    '''Open a specific file
    '''
    if pathlib.Path(home, args.file + '.md').is_file():
        path = str(pathlib.Path(home, args.file + '.md'))
    else:
        path = str(pathlib.Path(home, args.file))
    open_editor(path)

def get_todo():
    '''Open todo.txt
    '''
    path = pathlib.Path(home, 'todo.txt')
    open_editor(path)

def show_todo():
    '''Show todos
    '''
    with open(pathlib.Path(home, 'todo.txt'), 'r') as fh:
        for line in fh:
            print(line.rstrip())

def query_by_priority() -> List[str]:
    result = []
    with open(pathlib.Path(home, 'todo.txt'), 'r') as fh:
        for line in fh:
            if len(line) >= 3 and line[0] == '(' and line[2] == ')':
                result.append(line)
    result = sorted(result)
    return result

def collect_all_todos() -> List[str]:
    '''Collect all todos
    '''
    result = []
    with open(pathlib.Path(home, 'todo.txt'), 'r') as fh:
        for line in fh:
            task_done = len(line) >= 2 and line[:2] == 'x '
            if task_done:
                continue
            result.append(line)
    return result

def collect_all_done() -> List[str]:
    '''Collect all done tasks
    '''
    result = []
    with open(pathlib.Path(home, 'todo.txt'), 'r') as fh:
        for line in fh:
            task_done = len(line) >= 2 and line[:2] == 'x '
            if task_done:
                result.append(line)
    return result

def query_by_sigil(args, lines) -> List[str]:
    '''Query by project or (GTD) context
    '''
    result = []
    sigils = ['+', '@']
    categories = [item for item in args.query if item[0] in sigils]
    if len(categories) == 0:
        return lines
    for line in lines:
        for category in categories:
            if category in line:
                result.append(line)
                break
    return result

def get_query(args) -> None:
    '''Parse a query, a list of tokens representing project, context, priority
    '''
    result = []
    if 'p' in args.query or 'priority' in args.query:
        result = query_by_priority()
    elif 'done' in args.query:
        result = collect_all_done()
    else:
        result = collect_all_todos()
    result = query_by_sigil(args, result)
    for line in result:
        print(line.rstrip())

def app(args):
    '''Open an editor for today's file in a given context.
    '''
    ic(args)
    if args.show and args.todo:
        show_todo()
    elif args.show:
        show_context(args)
    elif args.dirs:
        get_tree()
    elif args.file:
        get_file(args)
    elif args.todo:
        get_todo()
    elif args.query:
        get_query(args)
    else:
        get_editor(args)

config = get_config()
home = create_home(config)

parser = argparse.ArgumentParser()
# subparsers = parser.add_subparsers(dest='command')

parser.add_argument(
    'context',
    nargs='?',
    help='location to create a note, relative to default ROOT',
)
parser.add_argument(
    '-d',
    '--dirs',
    action="store_true",
    help="show tree view of ROOT directory, sans `*.md`"
)
parser.add_argument(
    '-s',
    '--show',
    nargs='?',
    const='daily',
    help="show `*.md` at location `SHOW`",
)
parser.add_argument(
    '-f',
    '--file',
    help="open a sepcific file",
)
parser.add_argument(
    '-t',
    '--todo',
    action="store_true",
    help='open todo.txt',
)
parser.add_argument(
    '-q',
    '--query',
    nargs='+',
    help='run queries',
)
parser.set_defaults(func=app)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
    