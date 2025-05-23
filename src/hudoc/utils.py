import logging
import os
import urllib.parse
import uuid
from datetime import datetime
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup


def escape_latex(text):
    latex_special_chars = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }
    for char, escaped in latex_special_chars.items():
        text = text.replace(char, escaped)
    return text


def get_document_text(doc_id, base_url, library):
    url = f"{base_url}?library={library}&id={urllib.parse.quote(doc_id)}"
    logging.info(f"Fetching document content for {doc_id} from {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch content for {doc_id}: {str(e)}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    for script in soup(["script", "style"]):
        script.extract()

    # Extract text from top-level text containers, avoiding nested duplicates
    text_elements = soup.find_all(["p", "li", "h1", "h2", "h3"])
    seen_texts = set()
    text_lines = []
    for element in text_elements:
        text = element.get_text(separator=" ", strip=True)
        if text and text not in seen_texts:
            seen_texts.add(text)
            text_lines.append(text)

    # Join paragraphs with double newlines for readability
    text = "\n\n".join(text_lines)
    return text if text.strip() else None


def save_text(
    text,
    doc_id,
    title,
    description,
    output_dir,
    hudoc_type,
    verdict_date=None,
    evid=False,
):
    """Save the document text in plain text or evid format.

    Args:
        text (str): Document text to save.
        doc_id (str): Document ID.
        title (str): Document title.
        description (str): Document description (GREVIO only).
        output_dir (str): Directory to save the file.
        hudoc_type (str): Type of HUDOC database ('echr' or 'grevio').
        verdict_date (str, optional): Verdict date in YYYY-MM-DD format.
        evid (bool): If True, save in evid format (LaTeX and YAML); else plain text.

    """
    prefix = "echr_case" if hudoc_type == "echr" else "grevio_doc"
    safe_id = doc_id.replace("/", "_").replace(":", "_").replace(" ", "_")
    filename = f"{prefix}_{safe_id}.txt"

    if evid:
        save_evid(
            text,
            doc_id,
            title,
            description,
            output_dir,
            hudoc_type,
            filename,
            verdict_date,
        )
    else:
        filepath = os.path.join(output_dir, filename)
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Title: {title}\n")
                if description and hudoc_type == "grevio":
                    f.write(f"Description: {description}\n\n")
                f.write(text)
            logging.info(f"Saved content for {doc_id} to {filepath}")
        except OSError as e:
            logging.error(f"Failed to save file for {doc_id}: {str(e)}")


def save_evid(
    text,
    doc_id,
    title,
    description,
    output_dir,
    hudoc_type,
    filename,
    verdict_date=None,
):
    print(title)
    subdir = str(uuid.uuid4())
    subdir_path = os.path.join(output_dir, subdir)
    latex_file = os.path.join(subdir_path, "label.tex")
    yaml_file = os.path.join(subdir_path, "info.yml")
    safe_id = doc_id.replace("/", "_").replace(":", "_").replace(" ", "_")

    # Escape text for LaTeX
    escaped_text = escape_latex(text)

    # Create YAML metadata
    id_key = "itemid" if hudoc_type == "echr" else "greviosectionid"
    date = verdict_date or datetime.now().strftime("%Y-%m-%d")

    # Create LaTeX content with full text
    latex_content = (
        r"""\documentclass[parskip=full]{article}
\nonstopmode

%% HEADER
\usepackage{xargs}
\usepackage{xcolor}
\usepackage{hyperref}
\hypersetup{
  colorlinks=true,
  linkcolor=blue,
  anchorcolor=blue,
  filecolor=magenta,
  urlcolor=cyan,
}
\usepackage{todonotes}
\usepackage{etoolbox}
\makeatletter
\pretocmd{\@startsection}{\gdef\thesectiontype{#1}}{}{}
\pretocmd{\@sect}{\@namedef{the\thesectiontype title}{#8}}{}{}
\pretocmd{\@ssect}{\@namedef{the\thesectiontype title}{#5}}{}{}
\makeatother

\newwrite\textfile
\immediate\openout\textfile=\jobname.csv
\immediate\write\textfile{label ; quote ; note ; section title ; section no ; page ; date ; opage}

\newcommandx{\lb}[3]{\immediate\write\textfile{#1 \space; #2 \space; #3 \space; \thesectiontitle \space;  \thesection  \space;  \thepage  \space;  \pdate \space; \thesubsectiontitle}%
  \csdef{#1}{#2}%
  \hypertarget{#1}{\textcolor{blue}{#2}}\todo[color=blue!10!white,caption={\small#1; #3; #2}]{#1: #3}%
}

\newcommandx{\cc}[1]{
  \hyperlink{#1}{\csuse{#1}}
}

\newcommand{\sdate}[1]{%
  \def\localdate{#1}%
}

\newcommand{\pdate}{%
  \localdate%
}

\usepackage{scrextend}
%% HEADER

\begin{document}
\maketitle

\tableofcontents
\listoftodos[Labels]

\sdate{"""
        + date
        + r"""}

\section{"""
        + safe_id
        + r"""}
\subsection{0}

"""
        + escaped_text
        + r"""

\end{document}"""
    )

    yaml_content = {
        "authors": hudoc_type,
        "dates": date,
        "label": f"{description}",
        "original_name": filename,
        "tags": ["hudoc", "echr", "grevio", "rss", "document"],
        "time_added": datetime.now().strftime("%Y-%m-%d"),
        "title": doc_id or "Untitled",
        "url": f'https://hudoc.{hudoc_type}.coe.int/eng#{{"{id_key}":["{doc_id}"]}}',
        "uuid": subdir,
    }

    try:
        Path(subdir_path).mkdir(parents=True, exist_ok=True)
        with open(latex_file, "w", encoding="utf-8") as f:
            f.write(latex_content)
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(yaml_content, f, allow_unicode=True, default_style="'")
        logging.info(f"Saved evid format for {doc_id} to {subdir_path}")
    except OSError as e:
        logging.error(f"Failed to save evid files for {doc_id}: {str(e)}")
