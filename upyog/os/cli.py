from upyog.imports import *
from upyog.os.read_files import *
from upyog.utils import *
from upyog.cli import Param as P, call_parse


@call_parse
def move_files(
    i: P("Input folders to move the files from", str, nargs="+", metavar="INP") = None,
    o: P("Path to the output folders", str) = None,
    move: P("Move files (desctructively)", action="store_true") = False,
):
    """
    File Mover

    Move files from an arbitrary number of input folders to a _single_ output folder.

    The input folders are scanned recursively.
    If the output folder doesn't exist, it is created
    """
    recurse = True
    files = flatten([get_files(p, recurse=recurse) for p in i])
    out_dir = Path(o)
    if not out_dir.exists():
        rich.print(f"Creating output folder: {out_dir}")
        out_dir.mkdir(exist_ok=True, parents=True)

    mover = shutil.move if move else shutil.copy

    for file in track(files):
        mover(file, out_dir)
