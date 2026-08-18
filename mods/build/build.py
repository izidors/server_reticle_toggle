#!/usr/bin/env python3

from pathlib import Path
import argparse
import re
import subprocess
import tempfile
import zipfile


MOD_ID = "promiseofapocalypse.server_reticle_toggle"

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
DIST_DIR = ROOT / "dist"

MOD_SOURCE = (
    SRC_DIR
    / "res"
    / "scripts"
    / "client"
    / "gui"
    / "mods"
    / "mod_server_reticle_toggle.py"
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build WoT Server Reticle Toggle"
    )

    parser.add_argument(
        "--python27",
        required=True,
        help="Path to Python 2.7 executable"
    )

    return parser.parse_args()


def get_mod_version():
    if not MOD_SOURCE.exists():
        raise RuntimeError(
            "Mod source not found: %s" % MOD_SOURCE
        )

    source = MOD_SOURCE.read_text(
        encoding="utf-8"
    )

    match = re.search(
        r"^MOD_VERSION\s*=\s*['\"]([^'\"]+)['\"]",
        source,
        re.MULTILINE
    )

    if not match:
        raise RuntimeError(
            "MOD_VERSION not found in %s"
            % MOD_SOURCE
        )

    return match.group(1)


def compile_python(
    python27,
    source,
    destination
):
    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    code = (
        "import py_compile;"
        "py_compile.compile("
        "r'%s',"
        "r'%s',"
        "doraise=True)"
    ) % (
        str(source),
        str(destination)
    )

    subprocess.check_call([
        python27,
        "-c",
        code
    ])


def build():
    args = parse_args()

    python27 = Path(args.python27)

    if not python27.exists():
        raise RuntimeError(
            "Python 2.7 not found: %s"
            % python27
        )

    version = get_mod_version()

    output_file = (
        DIST_DIR
        / ("%s_%s.wotmod" % (
            MOD_ID,
            version
        ))
    )

    # source_files = list(
    #     SRC_DIR.rglob("mod_*.py")
    #)

    source_files = [
    MOD_SOURCE
    ]

    if not source_files:
        raise RuntimeError(
            "No mod_*.py files found under %s"
            % MOD_SOURCE
        )

    DIST_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if output_file.exists():
        output_file.unlink()

    print(
        "Building %s v%s"
        % (
            MOD_ID,
            version
        )
    )

    with tempfile.TemporaryDirectory() as temp_name:

        temp_dir = Path(temp_name)

        for source in source_files:

            relative = source.relative_to(
                SRC_DIR
            )

            destination = (
                temp_dir
                / relative.parent
                / (
                    source.stem
                    + ".pyc"
                )
            )

            print(
                " compiling %s"
                % relative
            )

            compile_python(
                str(python27),
                source,
                destination
            )

        with zipfile.ZipFile(
            output_file,
            "w",
            compression=zipfile.ZIP_STORED
        ) as archive:

            files = [
                path
                for path in temp_dir.rglob("*")
                if path.is_file()
            ]

            directories = set()

            for file_path in files:

                relative = file_path.relative_to(
                    temp_dir
                )

                parent = relative.parent

                while str(parent) != ".":

                    directories.add(
                        parent.as_posix()
                        + "/"
                    )

                    parent = parent.parent

            for directory in sorted(
                directories
            ):
                archive.writestr(
                    directory,
                    b""
                )

            for file_path in files:

                relative = file_path.relative_to(
                    temp_dir
                )

                archive_name = (
                    relative.as_posix()
                )

                print(
                    " + %s"
                    % archive_name
                )

                archive.write(
                    file_path,
                    archive_name
                )

    print()
    print(
        "Created: %s"
        % output_file
    )

    print(
        "Size:    %s bytes"
        % output_file.stat().st_size
    )


if __name__ == "__main__":
    build()