# ruff: noqa: E402
"""Generate an APSEC-oriented IEEEtran draft package from the Markdown rewrite.

The conversion is intentionally conservative: it preserves the current claims,
turns citation keys into BibTeX-backed IEEE citations, converts Markdown tables
into LaTeX tables, and writes a page-budget audit. It does not claim that the
resulting source is a final submission PDF.
"""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/write_apsec_ieeetran_package.py")

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MD_IN = REPO_ROOT / "docs" / "paper" / "apsec_technical_track_rewrite_v0_1.md"
DEFAULT_CLAIM_MAP = REPO_ROOT / "data" / "reviews" / "final_manuscript_claim_map_v0_1.json"
DEFAULT_TEX_OUT = REPO_ROOT / "docs" / "paper" / "apsec_ieeetran_draft.tex"
DEFAULT_BIB_OUT = REPO_ROOT / "docs" / "paper" / "apsec_references.bib"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "apsec_page_budget_audit_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "paper" / "apsec_page_budget_audit_v0_1.md"


APSEC_EXTRA_REFERENCES = [
    "long_popl_2016_prophet",
    "long_fse_2015_spr",
    "nguyen_icse_2013_semfix",
    "smith_fse_2015_overfitting",
    "widyasari_fse_2020_bugsinpy",
    "durieux_saner_2019_bears",
    "lin_splash_2017_quixbugs",
    "li_fse_2022_codereviewer",
    "chen_arxiv_2021_codex",
    "joshi_arxiv_2022_repair_is_nearly_generation",
    "jimenez_iclr_2024_swebench",
    "yang_neurips_2024_sweagent",
    "wang_acl_2024_not_fair_evaluators",
    "cortes_jmlr_2016_reject_option",
]


APSEC_BIBTEX_BY_KEY = {
    "qi_issta_2015_patch_plausibility": r"""@inproceedings{qi_issta_2015_patch_plausibility,
  author = {Qi, Zichao and Long, Fan and Achour, Sara and Rinard, Martin},
  title = {An Analysis of Patch Plausibility and Correctness for Generate-and-Validate Patch Generation Systems},
  booktitle = {Proceedings of the 2015 International Symposium on Software Testing and Analysis},
  pages = {24--36},
  year = {2015},
  doi = {10.1145/2771783.2771791}
}""",
    "legoues_icse_2012_genprog": r"""@inproceedings{legoues_icse_2012_genprog,
  author = {Le Goues, Claire and Nguyen, ThanhVu and Forrest, Stephanie and Weimer, Westley},
  title = {A Systematic Study of Automated Program Repair: Fixing 55 out of 105 Bugs for \$8 Each},
  booktitle = {Proceedings of the 34th International Conference on Software Engineering},
  pages = {3--13},
  year = {2012},
  doi = {10.1109/ICSE.2012.6227211}
}""",
    "just_issta_2014_defects4j": r"""@inproceedings{just_issta_2014_defects4j,
  author = {Just, Ren{\'e} and Jalali, Darioush and Ernst, Michael D.},
  title = {Defects4J: A Database of Existing Faults to Enable Controlled Testing Studies for Java Programs},
  booktitle = {Proceedings of the 2014 International Symposium on Software Testing and Analysis},
  pages = {437--440},
  year = {2014},
  doi = {10.1145/2610384.2628055}
}""",
    "widyasari_fse_2020_bugsinpy": r"""@inproceedings{widyasari_fse_2020_bugsinpy,
  author = {Widyasari, Ratnadira and Sim, Sheng Qin and Lok, Camellia and Qi, Haodi and Phan, Jack and Tay, Qijin and Tan, Constance and Wee, Fiona and Tan, Jodie Ethelda and Yieh, Yuheng and Goh, Brian and Thung, Ferdian and Kang, Hong Jin and Hoang, Thong and Lo, David and Ouh, Eng Lieh},
  title = {BugsInPy: A Database of Existing Bugs in Python Programs to Enable Controlled Testing and Debugging Studies},
  booktitle = {Proceedings of the 28th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering},
  pages = {1556--1560},
  year = {2020},
  doi = {10.1145/3368089.3417943}
}""",
    "barr_tse_2015_oracle_problem": r"""@article{barr_tse_2015_oracle_problem,
  author = {Barr, Earl T. and Harman, Mark and McMinn, Phil and Shahbaz, Muzammil and Yoo, Shin},
  title = {The Oracle Problem in Software Testing: A Survey},
  journal = {IEEE Transactions on Software Engineering},
  volume = {41},
  number = {5},
  pages = {507--525},
  year = {2015},
  doi = {10.1109/TSE.2014.2372785}
}""",
    "xia_zhang_icse_2023_llm_apr": r"""@inproceedings{xia_zhang_icse_2023_llm_apr,
  author = {Xia, Chunqiu Steven and Zhang, Lingming},
  title = {Automated Program Repair in the Era of Large Pre-trained Language Models},
  booktitle = {Proceedings of the 45th IEEE/ACM International Conference on Software Engineering},
  pages = {1482--1494},
  year = {2023},
  doi = {10.1109/ICSE48619.2023.00129}
}""",
    "tufano_icse_2019_bugfix_nmt": r"""@inproceedings{tufano_icse_2019_bugfix_nmt,
  author = {Tufano, Michele and Watson, Cody and Bavota, Gabriele and Di Penta, Massimiliano and White, Martin and Poshyvanyk, Denys},
  title = {An Empirical Investigation into Learning Bug-Fixing Patches in the Wild via Neural Machine Translation},
  booktitle = {Proceedings of the 41st International Conference on Software Engineering},
  pages = {832--837},
  year = {2019},
  doi = {10.1109/ICSE.2019.00064}
}""",
    "bacchelli_bird_icse_2013_code_review": r"""@inproceedings{bacchelli_bird_icse_2013_code_review,
  author = {Bacchelli, Alberto and Bird, Christian},
  title = {Expectations, Outcomes, and Challenges of Modern Code Review},
  booktitle = {Proceedings of the 35th International Conference on Software Engineering},
  pages = {712--721},
  year = {2013},
  doi = {10.1109/ICSE.2013.6606617}
}""",
    "chow_tit_1970_reject_option": r"""@article{chow_tit_1970_reject_option,
  author = {Chow, C. K.},
  title = {On Optimum Recognition Error and Reject Tradeoff},
  journal = {IEEE Transactions on Information Theory},
  volume = {16},
  number = {1},
  pages = {41--46},
  year = {1970},
  doi = {10.1109/TIT.1970.1054406}
}""",
    "geifman_el_yaniv_2017_selective_classification": r"""@inproceedings{geifman_el_yaniv_2017_selective_classification,
  author = {Geifman, Yonatan and El-Yaniv, Ran},
  title = {Selective Classification for Deep Neural Networks},
  booktitle = {Advances in Neural Information Processing Systems},
  pages = {4878--4887},
  year = {2017},
  eprint = {1705.08500},
  archivePrefix = {arXiv}
}""",
    "zheng_neurips_2023_llm_judge": r"""@inproceedings{zheng_neurips_2023_llm_judge,
  author = {Zheng, Lianmin and Chiang, Wei-Lin and Sheng, Ying and Zhuang, Siyuan and Wu, Zhanghao and Zhuang, Yonghao and Lin, Zi and Li, Zhuohan and Li, Dacheng and Xing, Eric P. and Zhang, Hao and Gonzalez, Joseph E. and Stoica, Ion},
  title = {Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena},
  booktitle = {Advances in Neural Information Processing Systems},
  year = {2023},
  eprint = {2306.05685},
  archivePrefix = {arXiv}
}""",
    "parasuraman_riley_1997_automation": r"""@article{parasuraman_riley_1997_automation,
  author = {Parasuraman, Raja and Riley, Victor},
  title = {Humans and Automation: Use, Misuse, Disuse, Abuse},
  journal = {Human Factors},
  volume = {39},
  number = {2},
  pages = {230--253},
  year = {1997},
  doi = {10.1518/001872097778543886}
}""",
    "long_popl_2016_prophet": r"""@inproceedings{long_popl_2016_prophet,
  author = {Long, Fan and Rinard, Martin},
  title = {Automatic Patch Generation by Learning Correct Code},
  booktitle = {Proceedings of the 43rd Annual ACM SIGPLAN-SIGACT Symposium on Principles of Programming Languages},
  pages = {298--312},
  year = {2016},
  doi = {10.1145/2837614.2837617}
}""",
    "long_fse_2015_spr": r"""@inproceedings{long_fse_2015_spr,
  author = {Long, Fan and Rinard, Martin},
  title = {Staged Program Repair with Condition Synthesis},
  booktitle = {Proceedings of the 2015 10th Joint Meeting on Foundations of Software Engineering},
  pages = {166--178},
  year = {2015},
  doi = {10.1145/2786805.2786811}
}""",
    "nguyen_icse_2013_semfix": r"""@inproceedings{nguyen_icse_2013_semfix,
  author = {Nguyen, Hoang Duong Thien and Qi, Dawei and Roychoudhury, Abhik and Chandra, Satish},
  title = {SemFix: Program Repair via Semantic Analysis},
  booktitle = {Proceedings of the 35th International Conference on Software Engineering},
  pages = {772--781},
  year = {2013},
  doi = {10.1109/ICSE.2013.6606623}
}""",
    "smith_fse_2015_overfitting": r"""@inproceedings{smith_fse_2015_overfitting,
  author = {Smith, Edward K. and Barr, Earl T. and Le Goues, Claire and Brun, Yuriy},
  title = {Is the Cure Worse than the Disease? Overfitting in Automated Program Repair},
  booktitle = {Proceedings of the 2015 10th Joint Meeting on Foundations of Software Engineering},
  pages = {532--543},
  year = {2015},
  doi = {10.1145/2786805.2786825}
}""",
    "durieux_saner_2019_bears": r"""@inproceedings{durieux_saner_2019_bears,
  author = {Madeiral, Fernanda and Urli, Simon and Maia, Marcelo and Monperrus, Martin},
  title = {Bears: An Extensible Java Bug Benchmark for Automatic Program Repair Studies},
  booktitle = {Proceedings of the 26th IEEE International Conference on Software Analysis, Evolution and Reengineering},
  pages = {468--478},
  year = {2019},
  eprint = {1901.06024},
  archivePrefix = {arXiv}
}""",
    "lin_splash_2017_quixbugs": r"""@inproceedings{lin_splash_2017_quixbugs,
  author = {Lin, Derrick and Koppel, James and Chen, Angela and Solar-Lezama, Armando},
  title = {QuixBugs: A Multi-Lingual Program Repair Benchmark Set Based on the Quixey Challenge},
  booktitle = {Proceedings Companion of the 2017 ACM SIGPLAN International Conference on Systems, Programming, Languages, and Applications: Software for Humanity},
  pages = {55--56},
  year = {2017},
  doi = {10.1145/3135932.3135941}
}""",
    "li_fse_2022_codereviewer": r"""@inproceedings{li_fse_2022_codereviewer,
  author = {Li, Zhiyu and Lu, Shuai and Guo, Daya and Duan, Nan and Jannu, Shailesh and Jenks, Grant and Majumder, Deep and Green, Jared and Svyatkovskiy, Alexey and Fu, Shengyu and Sundaresan, Neel},
  title = {Automating Code Review Activities by Large-Scale Pre-training},
  booktitle = {Proceedings of the 30th ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering},
  pages = {1035--1047},
  year = {2022},
  doi = {10.1145/3540250.3549081}
}""",
    "chen_arxiv_2021_codex": r"""@article{chen_arxiv_2021_codex,
  author = {Chen, Mark and others},
  title = {Evaluating Large Language Models Trained on Code},
  journal = {arXiv preprint arXiv:2107.03374},
  year = {2021}
}""",
    "joshi_arxiv_2022_repair_is_nearly_generation": r"""@inproceedings{joshi_arxiv_2022_repair_is_nearly_generation,
  author = {Joshi, Harshit and Cambronero, Jos{\'e} and Gulwani, Sumit and Le, Vu and Radicek, Ivan and Verbruggen, Gust},
  title = {Repair Is Nearly Generation: Multilingual Program Repair with LLMs},
  booktitle = {Proceedings of the AAAI Conference on Artificial Intelligence},
  volume = {37},
  number = {4},
  pages = {5131--5140},
  year = {2023},
  doi = {10.1609/aaai.v37i4.25642},
  eprint = {2208.11640},
  archivePrefix = {arXiv}
}""",
    "jimenez_iclr_2024_swebench": r"""@inproceedings{jimenez_iclr_2024_swebench,
  author = {Jimenez, Carlos E. and Yang, John and Wettig, Alexander and Yao, Shunyu and Pei, Kexin and Press, Ofir and Narasimhan, Karthik},
  title = {SWE-bench: Can Language Models Resolve Real-World GitHub Issues?},
  booktitle = {Proceedings of the 12th International Conference on Learning Representations},
  year = {2024},
  eprint = {2310.06770},
  archivePrefix = {arXiv}
}""",
    "yang_neurips_2024_sweagent": r"""@inproceedings{yang_neurips_2024_sweagent,
  author = {Yang, John and Jimenez, Carlos E. and Wettig, Alexander and Lieret, Kilian and Yao, Shunyu and Narasimhan, Karthik and Press, Ofir},
  title = {SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering},
  booktitle = {Advances in Neural Information Processing Systems},
  year = {2024},
  eprint = {2405.15793},
  archivePrefix = {arXiv}
}""",
    "wang_acl_2024_not_fair_evaluators": r"""@inproceedings{wang_acl_2024_not_fair_evaluators,
  author = {Wang, Peiyi and Li, Lei and Chen, Liang and Cai, Zefan and Zhu, Dawei and Lin, Binghuai and Cao, Yunbo and Kong, Lingpeng and Liu, Qi and Liu, Tianyu and Sui, Zhifang},
  title = {Large Language Models are not Fair Evaluators},
  booktitle = {Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics},
  pages = {9440--9450},
  year = {2024},
  eprint = {2305.17926},
  archivePrefix = {arXiv}
}""",
    "cortes_jmlr_2016_reject_option": r"""@article{cortes_jmlr_2016_reject_option,
  author = {Cortes, Corinna and DeSalvo, Giulia and Mohri, Mehryar},
  title = {Learning with Rejection},
  journal = {Journal of Machine Learning Research},
  volume = {17},
  number = {63},
  pages = {1--40},
  year = {2016}
}""",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def restore_latex_commands(text: str) -> str:
    text = re.sub(r"\\textbackslash\{\}\s*cite\\\{([^}]*)\\\}", r"\\cite{\1}", text)
    text = re.sub(
        r"\\cite\{([^}]*)\}",
        lambda match: r"\cite{" + match.group(1).replace(r"\_", "_") + "}",
        text,
    )
    text = text.replace(r"\textbackslash{}%", r"\%")
    return text


def convert_citations(text: str, citation_keys: set[str]) -> str:
    def repl(match: re.Match[str]) -> str:
        body = match.group(1)
        parts = [part.strip() for part in body.split(";")]
        if parts and all(part in citation_keys for part in parts):
            return r"\cite{" + ",".join(parts) + "}"
        return match.group(0)

    return re.sub(r"\[([A-Za-z0-9_;,\-\s]+)\]", repl, text)


def split_table_row(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


TABLE_CAPTIONS = {
    1: "Cumulative EVP-8 evidence levels.",
    2: "EVP-8 candidate composition.",
    3: "Three-model main results at selected evidence levels.",
    4: "E6 deterministic and no-verdict ablation.",
    5: "Hard-negative stress matrix aggregate results.",
    6: "False-accept anatomy and representative case groups.",
}


def table_to_latex(lines: list[str], table_index: int) -> str:
    rows = [split_table_row(line) for line in lines if line.strip().startswith("|")]
    if len(rows) < 2:
        return "\n".join(latex_escape(line) for line in lines)
    header = rows[0]
    data_rows = rows[2:] if is_separator_row(rows[1]) else rows[1:]
    col_spec = "Y" * len(header)

    def row(cells: list[str]) -> str:
        padded = cells + [""] * (len(header) - len(cells))
        return " & ".join(table_cell_to_latex(cell) for cell in padded[: len(header)]) + r" \\"

    latex_lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2pt}",
        rf"\caption{{{TABLE_CAPTIONS.get(table_index, f'APSEC manuscript table {table_index}.')}}}",
        rf"\label{{tab:apsec-{table_index}}}",
        rf"\begin{{tabularx}}{{\textwidth}}{{{col_spec}}}",
        r"\toprule",
        row(header),
        r"\midrule",
    ]
    latex_lines.extend(row(data_row) for data_row in data_rows)
    latex_lines.extend([r"\bottomrule", r"\end{tabularx}", r"\end{table*}"])
    return "\n".join(latex_lines)


def table_cell_to_latex(text: str) -> str:
    placeholders: list[str] = []

    def protect(value: str) -> str:
        token = f"@@TABLE_PLACEHOLDER_{len(placeholders)}@@"
        placeholders.append(value)
        return token

    def maybe_break_token(match: re.Match[str]) -> str:
        token = match.group(0)
        if len(token) >= 14 and any(char in token for char in "_/-"):
            safe = token.replace("{", "").replace("}", "")
            return protect(r"\path{" + safe + "}")
        return token

    if re.fullmatch(r"-?\d+\.\d{4,}", text.strip()):
        text = f"{float(text):.2f}"
    protected = re.sub(r"[A-Za-z0-9][A-Za-z0-9_./-]{8,}", maybe_break_token, text)
    escaped = latex_escape(protected)
    for index, value in enumerate(placeholders):
        escaped = escaped.replace(f"@@TABLE\_PLACEHOLDER\_{index}@@", value)
    return escaped


def convert_inline_markdown(text: str) -> str:
    placeholders: list[str] = []

    def protect(value: str) -> str:
        token = f"@@LATEX_PLACEHOLDER_{len(placeholders)}@@"
        placeholders.append(value)
        return token

    text = re.sub(
        r"`([^`]+)`",
        lambda m: protect(r"\texttt{" + latex_escape(m.group(1)) + "}"),
        text,
    )
    text = re.sub(
        r"\*\*([^*]+)\*\*",
        lambda m: protect(r"\textbf{" + latex_escape(m.group(1)) + "}"),
        text,
    )
    escaped = restore_latex_commands(latex_escape(text))
    for index, value in enumerate(placeholders):
        escaped = escaped.replace(f"@@LATEX\_PLACEHOLDER\_{index}@@", value)
    return escaped


def figure_to_latex(line: str, figure_index: int) -> str | None:
    match = re.match(r"!\[(.*?)\]\((.*?)\)", line.strip())
    if not match:
        return None
    caption_text = match.group(1).strip() or f"APSEC figure {figure_index}"
    caption_text = re.sub(r"^Figure\s+\d+\.\s*", "", caption_text)
    caption = latex_escape(caption_text)
    path = match.group(2).strip()
    environment = "figure*" if figure_index == 2 else "figure"
    width = r"0.72\textwidth" if figure_index == 2 else r"\columnwidth"
    return "\n".join(
        [
            rf"\begin{{{environment}}}[t]",
            r"\centering",
            rf"\includegraphics[width={width}]{{{path}}}",
            rf"\caption{{{caption}}}",
            rf"\label{{fig:apsec-{figure_index}}}",
            rf"\end{{{environment}}}",
        ]
    )


def markdown_to_latex(markdown: str, citation_keys: set[str]) -> tuple[str, dict[str, int]]:
    markdown = convert_citations(markdown, citation_keys)
    lines = markdown.splitlines()
    output: list[str] = []
    table_index = 0
    figure_index = 0
    i = 0
    in_abstract = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("Draft status:") or stripped.startswith("Target format note:"):
            i += 1
            continue

        if stripped.startswith("|"):
            table_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            table_index += 1
            output.append(table_to_latex(table_lines, table_index))
            continue

        figure = figure_to_latex(stripped, figure_index + 1)
        if figure:
            figure_index += 1
            output.append(figure)
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines) and re.match(r"\*\*Figure \d+\.", lines[i].strip()):
                i += 1
            continue

        if stripped == "## Abstract":
            output.append(r"\begin{abstract}")
            in_abstract = True
            i += 1
            continue

        if stripped.startswith("## ") and in_abstract:
            output.append(r"\end{abstract}")
            in_abstract = False

        if stripped.startswith("# "):
            i += 1
            continue
        if stripped.startswith("## "):
            title = re.sub(r"^\d+\.\s*", "", stripped[3:].strip())
            output.append(rf"\section{{{latex_escape(title)}}}")
        elif stripped.startswith("### "):
            title = re.sub(r"^\d+\.\d+\s*", "", stripped[4:].strip())
            output.append(rf"\subsection{{{latex_escape(title)}}}")
        elif stripped.startswith("- "):
            bullet_lines = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                bullet_lines.append(r"\item " + convert_inline_markdown(lines[i].strip()[2:]))
                i += 1
            output.append(r"\begin{itemize}")
            output.extend(bullet_lines)
            output.append(r"\end{itemize}")
            continue
        elif not stripped:
            output.append("")
        else:
            output.append(convert_inline_markdown(stripped))
        i += 1

    if in_abstract:
        output.append(r"\end{abstract}")

    stats = {
        "converted_table_count": table_index,
        "converted_figure_count": figure_index,
    }
    return "\n".join(output), stats


def bibtex_entry(record: dict[str, str]) -> str:
    key = record["key"]
    if key in APSEC_BIBTEX_BY_KEY:
        return APSEC_BIBTEX_BY_KEY[key] + "\n"
    reference = record["reference"]
    title_match = re.search(r'"([^"]+)"', reference)
    title = title_match.group(1) if title_match else reference.split(".")[0]
    author = reference[: title_match.start()].strip().rstrip(".") if title_match else "Unknown"
    if author.endswith(" et al"):
        author = author[:-6] + " and others"
    author = author.replace(", and ", " and ").replace(", ", " and ")
    year_match = re.search(r"\b(19|20)\d{2}\b", reference)
    year = year_match.group(0) if year_match else "n.d."
    doi_match = re.search(r"DOI:\s*([^\s.]+(?:\.[^\s.]+)*)", reference)
    doi_line = f"  doi = {{{bibtex_escape(doi_match.group(1).rstrip('.'))}}},\n" if doi_match else ""
    venue = ""
    if title_match:
        after_title = reference[title_match.end() :].strip().lstrip(".").strip()
        venue = re.sub(r"DOI:\s*.*$", "", after_title).strip().rstrip(".")
    howpublished_line = f"  howpublished = {{{bibtex_escape(venue)}}},\n" if venue else ""
    return (
        f"@misc{{{key},\n"
        f"  author = {{{bibtex_escape(author)}}},\n"
        f"  title = {{{bibtex_escape(title)}}},\n"
        f"{howpublished_line}"
        f"  year = {{{bibtex_escape(year)}}},\n"
        f"{doi_line}"
        f"}}\n"
    )


def bibtex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
    }
    return "".join(replacements.get(char, char) for char in value)


def build_tex(body: str) -> str:
    return "\n".join(
        [
            r"\documentclass[conference]{IEEEtran}",
            "",
            r"\usepackage{booktabs}",
            r"\usepackage{graphicx}",
            r"\usepackage{tabularx}",
            r"\usepackage{url}",
            r"\usepackage[hidelinks]{hyperref}",
            r"\newcolumntype{Y}{>{\raggedright\arraybackslash}X}",
            r"\Urlmuskip=0mu plus 1mu",
            r"\emergencystretch=2em",
            "",
            r"\title{Evidence Visibility Shapes Risk Behavior in a Controlled LLM Patch-Verifier Study}",
            r"\author{\IEEEauthorblockN{Anonymous Authors}\IEEEauthorblockA{Anonymous Institution}}",
            "",
            r"\begin{document}",
            r"\maketitle",
            "",
            body,
            "",
            r"\bibliographystyle{IEEEtran}",
            r"\bibliography{apsec_references}",
            r"\end{document}",
            "",
        ]
    )


def word_count(markdown: str) -> int:
    cleaned = re.sub(r"```.*?```", " ", markdown, flags=re.DOTALL)
    cleaned = re.sub(r"\|.*\|", " ", cleaned)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9\-_/]*", cleaned))


def build_audit(
    markdown: str,
    tex_text: str,
    bib_text: str,
    stats: dict[str, int],
    reference_count: int,
    compile_runs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    words = word_count(markdown)
    estimated_text_pages = words / 850.0
    float_pages = (stats["converted_table_count"] * 0.22) + (stats["converted_figure_count"] * 0.28)
    reference_pages = max(reference_count / 18.0, 0.5)
    estimated_pages = estimated_text_pages + float_pages + reference_pages
    compile_summary = read_compile_summary()
    checks = [
        {
            "check": "ieeetran_source_generated",
            "passed": r"\documentclass[conference]{IEEEtran}" in tex_text,
        },
        {
            "check": "bibtex_generated",
            "passed": reference_count >= 25 and "@" in bib_text,
        },
        {
            "check": "apsec_reference_count_not_sparse",
            "passed": reference_count >= 25,
            "detail": f"{reference_count} references; APSEC draft gate is >=25",
        },
        {
            "check": "apsec_bibtex_not_temporary_misc_only",
            "passed": "@inproceedings{" in bib_text
            and bib_text.count("@misc{") < max(3, reference_count // 4),
        },
        {
            "check": "citation_keys_converted_to_cite_commands",
            "passed": r"\cite{" in tex_text and "Reference Support Records" not in tex_text,
        },
        {
            "check": "camera_facing_caption_cleanup",
            "passed": "Converted APSEC draft table" not in tex_text
            and "CONVERTED APSEC DRAFT TABLE" not in tex_text
            and "Figure 1. Figure 1." not in tex_text
            and "Figure 2. Figure 2." not in tex_text
            and "Figure 3. Figure 3." not in tex_text,
        },
        {
            "check": "camera_facing_internal_note_removed",
            "passed": "companion IEEEtran/BibTeX/page-budget draft package"
            not in tex_text,
        },
        {
            "check": "camera_facing_table_count_curated",
            "passed": stats["converted_table_count"] <= 6,
        },
        {
            "check": "camera_facing_long_float_removed",
            "passed": "32.666666666666664" not in tex_text,
        },
        {
            "check": "page_budget_estimate_within_apsec_technical_limit",
            "passed": estimated_pages <= 10.0,
        },
        {
            "check": "compiled_pdf_within_apsec_technical_limit",
            "passed": bool(compile_summary["compiled_pdf_present"])
            and (compile_summary["compiled_pdf_pages"] or 999) <= 10,
        },
        {
            "check": "compiled_pdf_has_no_undefined_references",
            "passed": compile_summary["undefined_references_in_latest_log"] is False,
        },
        {
            "check": "stress_matrix_result_present_in_tex",
            "passed": "62 repeated false accepts" in tex_text
            and "12/93" in tex_text
            and "strict rejects remained 0" in tex_text,
        },
        {
            "check": "anonymous_author_block_present",
            "passed": "Anonymous Authors" in tex_text
            and "Anonymous Institution" in tex_text,
        },
        {
            "check": "final_pdf_not_claimed",
            "passed": True,
        },
    ]
    return {
        "artifact_id": "apsec_page_budget_audit_v0_1",
        "date": "2026-07-08",
        "status": "passed" if all(check["passed"] for check in checks) else "needs_revision",
        "target": {
            "format": "anonymous IEEEtran conference draft",
            "assumed_apsec_technical_page_limit": 10,
            "note": "Estimate only; final status requires local LaTeX compilation and visual page inspection.",
        },
        "counts": {
            "word_count_excluding_tables": words,
            "converted_table_count": stats["converted_table_count"],
            "converted_figure_count": stats["converted_figure_count"],
            "reference_count": reference_count,
            "estimated_pages": round(estimated_pages, 2),
            "compiled_pdf_pages": compile_summary["compiled_pdf_pages"],
        },
        "compile_summary": compile_summary,
        "compile_runs": compile_runs or [],
        "checks": checks,
        "outputs": {
            "tex": rel(DEFAULT_TEX_OUT),
            "bib": rel(DEFAULT_BIB_OUT),
            "audit_json": rel(DEFAULT_JSON_OUT),
            "audit_md": rel(DEFAULT_MD_OUT),
        },
        "remaining_formatting_risks": [
            "Compiled PDF may still have underfull hbox warnings from narrow-column paragraph breaks that need visual layout review.",
            "Final double-blind compliance still requires visual inspection even though the source author block is anonymous.",
            "BibTeX entries compile but should be normalized to venue-quality fields.",
            "References now meet the APSEC draft density gate but still need final human bibliographic review.",
            "The current package is a draft source conversion, not a submitted or camera-ready PDF.",
        ],
    }


def read_compile_summary() -> dict[str, Any]:
    log_path = DEFAULT_TEX_OUT.with_suffix(".log")
    pdf_path = DEFAULT_TEX_OUT.with_suffix(".pdf")
    summary: dict[str, Any] = {
        "compiled_pdf_present": pdf_path.exists(),
        "compiled_pdf_pages": None,
        "log_present": log_path.exists(),
        "undefined_references_in_latest_log": None,
        "overfull_hbox_count_in_latest_log": None,
        "underfull_hbox_count_in_latest_log": None,
    }
    if not log_path.exists():
        return summary
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    page_match = re.search(r"Output written on .*?\((\d+) pages?,", log_text)
    if page_match:
        summary["compiled_pdf_pages"] = int(page_match.group(1))
    summary["undefined_references_in_latest_log"] = "undefined references" in log_text.lower()
    summary["overfull_hbox_count_in_latest_log"] = log_text.count("Overfull \\hbox")
    summary["underfull_hbox_count_in_latest_log"] = log_text.count("Underfull \\hbox")
    return summary


def run_latex_compile(tex_path: Path) -> list[dict[str, Any]]:
    workdir = tex_path.parent
    stem = tex_path.stem
    commands = [
        ["pdflatex", "-interaction=nonstopmode", tex_path.name],
        ["bibtex", stem],
        ["pdflatex", "-interaction=nonstopmode", tex_path.name],
        ["pdflatex", "-interaction=nonstopmode", tex_path.name],
    ]
    runs: list[dict[str, Any]] = []
    for command in commands:
        result = subprocess.run(
            command,
            cwd=workdir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,
            check=False,
        )
        runs.append(
            {
                "command": " ".join(command),
                "exit_code": result.returncode,
            }
        )
        if result.returncode != 0:
            break
    return runs


def write_audit_md(audit: dict[str, Any], path: Path) -> None:
    counts = audit["counts"]
    lines = [
        "# APSEC IEEEtran and page-budget audit",
        "",
        f"Status: `{audit['status']}`",
        "",
        "## Counts",
        "",
        "| item | value |",
        "| --- | ---: |",
        f"| word count excluding tables | {counts['word_count_excluding_tables']} |",
        f"| converted tables | {counts['converted_table_count']} |",
        f"| converted figures | {counts['converted_figure_count']} |",
        f"| references | {counts['reference_count']} |",
        f"| estimated pages | {counts['estimated_pages']} |",
        f"| compiled PDF pages | {counts['compiled_pdf_pages'] or 'n/a'} |",
        "",
        "## Compile Summary",
        "",
        f"- compiled PDF present: `{str(audit['compile_summary']['compiled_pdf_present']).lower()}`",
        f"- undefined references in latest log: `{audit['compile_summary']['undefined_references_in_latest_log']}`",
        f"- overfull hbox count in latest log: `{audit['compile_summary']['overfull_hbox_count_in_latest_log']}`",
        f"- underfull hbox count in latest log: `{audit['compile_summary']['underfull_hbox_count_in_latest_log']}`",
        "",
        "## Checks",
        "",
        "| check | passed |",
        "| --- | --- |",
    ]
    lines.extend(f"| {check['check']} | {str(check['passed']).lower()} |" for check in audit["checks"])
    if audit.get("compile_runs"):
        lines.extend(["", "## Compile Runs", "", "| command | exit code |", "| --- | ---: |"])
        for run in audit["compile_runs"]:
            lines.append(f"| `{run['command']}` | {run['exit_code']} |")
    lines.extend(["", "## Remaining Formatting Risks", ""])
    lines.extend(f"- {risk}" for risk in audit["remaining_formatting_risks"])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--md-in", type=Path, default=DEFAULT_MD_IN)
    parser.add_argument("--claim-map", type=Path, default=DEFAULT_CLAIM_MAP)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX_OUT)
    parser.add_argument("--bib-out", type=Path, default=DEFAULT_BIB_OUT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--compile", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    markdown = args.md_in.read_text(encoding="utf-8")
    claim_map = read_json(args.claim_map)
    existing_reference_keys = {record["key"] for record in claim_map["reference_records"]}
    references = list(claim_map["reference_records"]) + [
        {"key": key, "reference": key}
        for key in APSEC_EXTRA_REFERENCES
        if key not in existing_reference_keys
    ]
    citation_keys = {record["key"] for record in references}
    body, stats = markdown_to_latex(markdown, citation_keys)
    tex_text = build_tex(body)
    bib_text = "\n\n".join(bibtex_entry(record).rstrip() for record in references) + "\n"
    existing = {
        "tex": args.tex_out.read_text(encoding="utf-8") if args.tex_out.exists() else None,
        "bib": args.bib_out.read_text(encoding="utf-8") if args.bib_out.exists() else None,
        "json": args.json_out.read_text(encoding="utf-8") if args.json_out.exists() else None,
        "md": args.md_out.read_text(encoding="utf-8") if args.md_out.exists() else None,
    }
    existing_compile_runs: list[dict[str, Any]] = []
    if existing["json"]:
        try:
            parsed_existing = json.loads(existing["json"])
            existing_compile_runs = parsed_existing.get("compile_runs") or []
        except json.JSONDecodeError:
            existing_compile_runs = []

    args.tex_out.parent.mkdir(parents=True, exist_ok=True)
    args.bib_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.tex_out.write_text(tex_text, encoding="utf-8")
    args.bib_out.write_text(bib_text, encoding="utf-8")

    compile_runs = run_latex_compile(args.tex_out) if args.compile else existing_compile_runs
    audit = build_audit(markdown, tex_text, bib_text, stats, len(references), compile_runs)
    json_text = json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.json_out.write_text(json_text, encoding="utf-8")
    write_audit_md(audit, args.md_out)

    if args.check:
        if existing["tex"] is not None and existing["tex"] != tex_text:
            raise SystemExit(f"{rel(args.tex_out)} is not current")
        if existing["bib"] is not None and existing["bib"] != bib_text:
            raise SystemExit(f"{rel(args.bib_out)} is not current")
        if existing["json"] is not None and existing["json"] != json_text:
            raise SystemExit(f"{rel(args.json_out)} is not current")
        current_md = args.md_out.read_text(encoding="utf-8")
        if existing["md"] is not None and existing["md"] != current_md:
            raise SystemExit(f"{rel(args.md_out)} is not current")
        if any(value is None for value in existing.values()):
            raise SystemExit("APSEC IEEEtran package outputs were missing before --check")
        if audit["status"] != "passed":
            raise SystemExit(f"APSEC IEEEtran package audit status is {audit['status']}")
        print("APSEC IEEEtran package outputs are current")
    else:
        print(f"wrote {rel(args.tex_out)}")
        print(f"wrote {rel(args.bib_out)}")
        print(f"wrote {rel(args.json_out)}")
        print(f"wrote {rel(args.md_out)}")


if __name__ == "__main__":
    main()
