#!/usr/bin/env python3

import glob
import os
import platform
import re
import shlex
import subprocess
import zipfile


def kicad_version(cli):
    cmd = f"{cli} --version"
    try:
        out = subprocess.run(shlex.split(cmd),
                             capture_output=True,
                             check=True,
                             text=True).stdout.strip()
        rev = out[0]
    except subprocess.CalledProcessError:
        rev = None

    return rev


def gitrev():
    git_cmd = "git rev-parse --short HEAD"
    try:
        rev = subprocess.run(shlex.split(git_cmd),
            capture_output=True,
            check=True,
            text=True
            ).stdout.strip()
    except subprocess.CalledProcessError: 
        rev = None

    return rev


def render_document(doc, gitrev):
    outdir = f"./output-{gitrev}"
    if "sch" == doc:
        print("> Rendering schematic... ", end='')
    else:
        print("> Rendering PCB file... ", end='')

    with open(f"emonHP.kicad_{doc}", 'r') as f_in:
        with open(f"{outdir}/emonHP.kicad_{doc}", 'w') as f_out:
            found_gitrev = False
            for ln in f_in:
                if not found_gitrev:
                    if re.search("gitrev", ln):
                        ln = ln.replace("gitrev", gitrev)
                        found_gitrev = True
                f_out.write(ln)
    print("Done!")


def get_gerber_names(outdir):
    """ Get the filenames of the gerber files """
    return glob.glob(f"{outdir}/*.g*")

if __name__ == "__main__":
    
    host_is_mac = re.match("macOS", platform.platform())
    if host_is_mac:
        kicad_cli = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
        kicad_script = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/plugins"
    else:
        kicad_cli = "kicad-cli"
        kicad_script = "/usr/share/kicad/plugins"

    kicad_version = kicad_version(kicad_cli)
    if not kicad_version:
        print("> Did not find kicad-cli. Exiting.")
        exit(1)
    elif kicad_version != '7':
        print(f"> WARNING: Only tested with KiCad 7, found KiCad {kicad_version}.")

    print("> Generating emonHP manufacturing files...")

    # Get the git revision
    gitrev = gitrev()
    if not gitrev:
        print("> Failed to get git SHA. Exiting.")
        exit(1)
    
    # Create output directory (with checks)
    outdir = f"./output-{gitrev}"
    print(f">   - outputs are in {outdir}")

    if os.path.exists(outdir):
        while True:
            r = input(">   - output folder already exists. Continue? (Y/N) ")
            r = r.upper()
            if r == 'N':
                exit(0)
            elif r == 'Y':
                break

    os.makedirs(outdir, exist_ok=True)

    # Copy the schematic and PCB files, replacing the <gitrev> tag
    render_document("sch", gitrev)
    render_document("pcb", gitrev)

    # Render the schematics and PCB layout into PDFs
    # https://docs.kicad.org/7.0/en/cli/cli.html#schematic
    print("> Rendering schematic into PDF file... ", end='')
    sch_pdf_cmd = f"{kicad_cli} sch export pdf -o {outdir}/emonHP-schematic.pdf {outdir}/emonHP.kicad_sch"
    subprocess.run(shlex.split(sch_pdf_cmd),
                   capture_output=True)
    print("Done!")

    print("> Rendering PCB floorplan into PDF file... ", end='')
    pcb_pdf_cmd = f"{kicad_cli} pcb export pdf -o {outdir}/emonHP-floorplan.pdf -l F.Paste,F.Silkscreen,Edge.Cuts,F.Mask --black-and-white --ev {outdir}/emonHP.kicad_pcb"
    subprocess.run(shlex.split(pcb_pdf_cmd),
                   capture_output=True)
    print("Done!")

    # Render the 3D model of the board
    print("> Exporting 3D model... ", end='')
    pcb_3d_cmd = f"{kicad_cli} pcb export step -f -o {outdir}/emonHP-3d-render.step {outdir}/emonHP.kicad_pcb"
    subprocess.run(shlex.split(pcb_3d_cmd),
                   capture_output=True)
    print("Done!")
                
    # Make the BoM; first export XML then process with one of the KiCad scripts
    print("> Generating BoM... ", end='')
    bom_xml_cmd = f"{kicad_cli} sch export python-bom -o {outdir}/bom-tmp.xml {outdir}/emonHP.kicad_sch"
    bom_csv_cmd = f"python3 {kicad_script}/bom_csv_grouped_by_value_with_fp.py {outdir}/bom-tmp.xml {outdir}/emonHP-bom.csv"
    subprocess.run(shlex.split(bom_xml_cmd),
                   capture_output=True)
    subprocess.run(shlex.split(bom_csv_cmd),
                   capture_output=True)
    os.remove(f"{outdir}/bom-tmp.xml")
    print("Done!")
    
    # Export and zip the gerbers files
    print("> Exporting Gerbers... ", end='')
    gerber_cmd = f"{kicad_cli} pcb export gerbers -o {outdir}/ -l F.Cu,F.Paste,F.Silkscreen,F.Mask,B.Cu,B.Paste,B.Silkscreen,B.Mask,In1.Cu,In2.Cu --ev --subtract-soldermask {outdir}/emonHP.kicad_pcb"
    zip_cmd = f"zip {outdir}/emonHP-gerbers.zip {outdir}/*.g*"
    subprocess.run(shlex.split(gerber_cmd), capture_output=True)
    gerbers = get_gerber_names(outdir)

    with zipfile.ZipFile(f"{outdir}/emonHP-gerbers.zip", 'w') as z:
        for gerber in gerbers:
            z.write(gerber)
            os.remove(gerber)
    print("Done!")

