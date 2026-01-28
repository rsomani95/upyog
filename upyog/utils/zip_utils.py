from upyog.imports import *

def zip_folder(path: PathLike):
    path = Path(path)
    assert path.is_dir()
    assert path.exists()

    return shutil.make_archive(path, "zip", path)

def compose_files_into_zip_archive(
    files: List[PathLike],
    output_path: PathLike,
):
    import tempfile

    output_path = Path(output_path)
    assert output_path.suffix == ".zip", f"output_path must end with .zip, got {output_path}"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        for file in files:
            shutil.copy(file, tmp_path)

        archive_path = shutil.make_archive(str(output_path.with_suffix("")), "zip", tmp_path)

    return archive_path
