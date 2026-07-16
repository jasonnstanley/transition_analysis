import subprocess
import sys
import shutil


def run(command):
    print()
    print("Running:", " ".join(command))
    subprocess.run(command, check=True)


def main():
    run([sys.executable, "run_models.py"])

    if shutil.which("pdflatex") is None:
        print()
        print("pdflatex not found. Skipping PDF build.")
        print("LaTeX file is still available at: paper\\model_report.tex")
        return

    run([
        "pdflatex",
        "-output-directory=paper",
        "paper\\model_report.tex"
    ])


if __name__ == "__main__":
    main()