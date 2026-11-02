"""
run_project.py
--------------
ONE-CLICK entry point for the whole project.

    python run_project.py

What it does
  1. Creates the dataset if  dataset/library_loans_sample.csv  is missing.
  2. Runs the full analysis (src/analysis.py).
  3. Saves the 5 charts inside the  visualizations/  folder.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))   # so Python can find our src files

import analysis                                      # noqa: E402  (src/analysis.py)
import generate_dataset                              # noqa: E402  (src/generate_dataset.py)


def main():
    print("LIBRARY USAGE AND BOOK CIRCULATION ANALYSIS")
    print("Student: Mohd Talish Ansari | BCA Artificial Intelligence | Semester 1")

    if not os.path.exists(analysis.DATA_PATH):
        print("\nDataset not found - creating it now...")
        generate_dataset.main()

    analysis.run_analysis()

    print("\nAll done! Charts are saved in the 'visualizations' folder.")


if __name__ == "__main__":
    main()
