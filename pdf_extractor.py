import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple
import fitz  # install with 'pip install pymupdf'
import re

def _parse_highlight(annot: fitz.Annot, wordlist: List[Tuple[float, float, float, float, str, int, int, int]]) -> str:
    points = annot.vertices
    quad_count = int(len(points) / 4)
    sentences = []
    for i in range(quad_count):
        # where the highlighted part is
        r = fitz.Quad(points[i * 4 : i * 4 + 4]).rect
        words = [w for w in wordlist if fitz.Rect(w[:4]).intersects(r)]
        sentences.append(" ".join(w[4] for w in words))
    sentence = " ".join(sentences)
    return sentence


def handle_page(page):
    wordlist = page.get_text("words")  # list of words on page
    wordlist.sort(key=lambda w: (w[1], w[0]))  # ascending y, then x
    highlights = []
    annot = page.first_annot
    while annot:
        if annot.type[0] == 8:
            highlights.append(_parse_highlight(annot, wordlist))
        annot = annot.next
    return highlights


def extract_info(lst):
    # Regular expression to match the required information
    regex1 = r'(?P<Name_of_Insured>[A-Z][a-z]+ [A-Z][a-z]+)\D+(?P<Policy_Number>\d+)\D+(?P<Effective_Date>[A-Z][a-z]+\s\d{1,2},\s\d{4})\D+(?P<Expiry_Date>[A-Z][a-z]+\s\d{1,2},\s\d{4})'
    regex2 = r'(?P<Effective_Date>\d{4}/\d{2}/\d{2}),\s*(?P<Expiry_Date>\d{4}/\d{2}/\d{2}),\s*(?P<Name_of_Insured>[A-Z][a-z]+\s[A-Z][a-z]+).*?\b(?P<Policy_Number>\d{6,})\b'

    # Extract the information from the list using regex1
    data_str = ' '.join(lst)
    match = re.search(regex1, data_str)
    if match:
        data_dict = match.groupdict()
        return data_dict

    # If regex1 did not match, try regex2
    match = re.search(regex2, data_str)
    if match:
        data_dict = match.groupdict()
        return data_dict

    # If neither regex matched, return None
    return None


def main(filepath: str) -> dict:
    doc = fitz.open(filepath)
    highlights = []
    for page in doc:
        highlights += handle_page(page)
    return extract_info(highlights)


def process_pdf(filepath: str):
    result = main(filepath)
    if result:
        # Prepare the formatted output
        output = ''
        output += '----------------------------------------------------------------------------------------\n'
        output += 'Sample PDF Output:\n\n'
        output += f"Name of Insured: {result['Name_of_Insured']}\n"
        output += f"Policy Number: {result['Policy_Number']}\n"
        output += f"Effective Date: {result['Effective_Date']}\n"
        output += f"Expiry Date: {result['Expiry_Date']}\n"
        output += '----------------------------------------------------------------------------------------\n'
        output += "Extracted Information (Dictionary):\n"
        output += str(result)

        # Create the GUI window
        window = tk.Tk()
        window.title("PDF Extractor")

        # Create a label to display the output
        output_label = tk.Label(window, text=output, justify="left")
        output_label.pack(padx=10, pady=10)

        # Create a button to close the application
        close_button = tk.Button(window, text="Close", command=window.quit)
        close_button.pack(padx=10, pady=10)

        # Run the GUI event loop
        window.mainloop()


# Prompt the user to select a PDF file
from tkinter import filedialog

file_path = filedialog.askopenfilename(title="Select a PDF file")

if file_path:
    process_pdf(file_path)
else:
    messagebox.showerror("Error", "No PDF file selected.")
