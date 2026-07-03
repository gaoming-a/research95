# CCF-C Citation Support Bank v0.1

## Scope

This is a paper-facing citation support bank for the current CCF-C route. It
uses the `nature-citation` claim-segmentation discipline, but not the
Nature/CNS-only venue restriction, because the target manuscript is a computer
science / software engineering paper. Sources should be primary CS, SE, ML, or
human-automation references suitable for CCF-C related work and threats.

Execution boundary:

- no experiment rerun;
- no API call;
- no raw model output read;
- no prompt text or patch text read;
- no invalid early-setting content reintroduced.

## Claim Segments and Support

| Segment | Paper location | Manuscript claim to support | Candidate sources | Support grade | Use boundary |
|---|---|---|---|---|---|
| S1 | Introduction / motivation | Test-passing or plausible patches are not necessarily correct, so patch review should distinguish visible evidence from hidden correctness labels. | Qi et al., ISSTA 2015; Le Goues et al., ICSE 2012; Just et al., ISSTA 2014 | strong for motivation | Supports why visible tests are insufficient; does not prove EVP-8 effectiveness. |
| S2 | Related work: APR evaluation | APR benchmarks and patch-generation studies commonly rely on controlled bug datasets and test-based validation, creating a known evaluation boundary. | Just et al., ISSTA 2014; Le Goues et al., ICSE 2012; Tufano et al., ICSE 2019 | moderate-to-strong | Use to position candidate-patch verification; avoid claiming the same dataset or task distribution. |
| S3 | Related work: LLMs and APR | Large pretrained models have been studied for automated program repair and code-editing tasks, but correctness verification remains a separate decision problem. | Xia and Zhang, ICSE 2023; Tufano et al., ICSE 2019 | moderate | Supports background only; does not support autonomous verifier reliability. |
| S4 | Related work: code review | Modern code review is a socio-technical decision process, not just a syntactic or test outcome check. | Bacchelli and Bird, ICSE 2013 | moderate | Use to justify merge-gate framing; do not overextend to all industrial review settings. |
| S5 | Method framing | A verifier with an escalation option is related to selective prediction / classification with reject option. | Chow, IEEE Trans. Information Theory 1970; Geifman and El-Yaniv, 2017 | strong conceptual support | Supports accept/reject/escalate framing; does not imply calibrated probabilities in this study. |
| S6 | Method / threats | The oracle problem means evaluator-only correctness labels must be treated as a validity boundary, not as model-visible evidence. | Barr et al., IEEE TSE 2015 | strong | Supports hidden-evaluator separation and threats-to-validity discussion. |
| S7 | Discussion: LLM-as-judge | LLM-based judging has known evaluation and reliability concerns, so LLM verifier results need controlled protocols and bounded claims. | Zheng et al., NeurIPS 2023 | moderate | Use for general LLM-as-judge caution; avoid claiming chatbot-arena results transfer to patch verification. |
| S8 | Discussion: automation reliance | Human-AI decision systems can suffer from over-reliance or misuse of automation outputs, motivating explicit evidence-boundary reporting. | Parasuraman and Riley, Human Factors 1997 | moderate | Supports anchoring/reliance concern; not a direct software-patch result. |

## Candidate Reference Records

| Key | Reference | Suggested use |
|---|---|---|
| `qi_issta_2015_patch_plausibility` | Zichao Qi, Fan Long, Sara Achour, and Martin Rinard. "An Analysis of Patch Plausibility and Correctness for Generate-and-Validate Patch Generation Systems." ISSTA 2015. DOI: `10.1145/2771783.2771791`. | Main citation for plausible patch != correct patch. |
| `legoues_icse_2012_genprog` | Claire Le Goues, ThanhVu Nguyen, Stephanie Forrest, and Westley Weimer. "A Systematic Study of Automated Program Repair: Fixing 55 out of 105 Bugs for $8 Each." ICSE 2012. DOI: `10.1109/ICSE.2012.6227211`. | Historical APR/test-based repair context. |
| `just_issta_2014_defects4j` | Rene Just, Darioush Jalali, and Michael D. Ernst. "Defects4J: A Database of Existing Faults to Enable Controlled Testing Studies for Java Programs." ISSTA 2014. DOI: `10.1145/2610384.2628055`. | Controlled fault benchmark / test-study context. |
| `barr_tse_2015_oracle_problem` | Earl T. Barr, Mark Harman, Phil McMinn, Muzammil Shahbaz, and Shin Yoo. "The Oracle Problem in Software Testing: A Survey." IEEE TSE 2015. DOI: `10.1109/TSE.2014.2372785`. | Oracle/label-boundary motivation and threats. |
| `xia_zhang_icse_2023_llm_apr` | Chunqiu Steven Xia and Lingming Zhang. "Automated Program Repair in the Era of Large Pre-trained Language Models." ICSE 2023. DOI: `10.1109/ICSE48619.2023.00129`. | LLM-for-APR related work and task distinction. |
| `tufano_icse_2019_bugfix_nmt` | Michele Tufano, Cody Watson, Gabriele Bavota, Massimiliano Di Penta, Martin White, and Denys Poshyvanyk. "An Empirical Investigation into Learning Bug-Fixing Patches in the Wild via Neural Machine Translation." ICSE 2019. DOI: `10.1109/ICSE.2019.00064`. | Neural bug-fix generation background. |
| `bacchelli_bird_icse_2013_code_review` | Alberto Bacchelli and Christian Bird. "Expectations, Outcomes, and Challenges of Modern Code Review." ICSE 2013. DOI: `10.1109/ICSE.2013.6606617`. | Code review / merge-gate framing. |
| `chow_tit_1970_reject_option` | C. K. Chow. "On Optimum Recognition Error and Reject Tradeoff." IEEE Transactions on Information Theory 1970. DOI: `10.1109/TIT.1970.1054406`. | Reject-option foundation for escalation. |
| `geifman_el_yaniv_2017_selective_classification` | Yonatan Geifman and Ran El-Yaniv. "Selective Classification for Deep Neural Networks." arXiv:1705.08500, 2017. | Modern selective-classification framing. |
| `zheng_neurips_2023_llm_judge` | Lianmin Zheng et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." NeurIPS 2023. arXiv:2306.05685. | LLM-as-judge reliability and evaluation context. |
| `parasuraman_riley_1997_automation` | Raja Parasuraman and Victor Riley. "Humans and Automation: Use, Misuse, Disuse, Abuse." Human Factors 1997. DOI: `10.1518/001872097778543886`. | Automation reliance / anchoring discussion. |

## Insertion Plan

1. Introduction should cite `qi_issta_2015_patch_plausibility`,
   `barr_tse_2015_oracle_problem`, and `bacchelli_bird_icse_2013_code_review`
   around the core problem statement.
2. Related Work should group references by APR evaluation, LLM-based repair,
   code review, and selective abstention rather than listing them as a flat
   bibliography.
3. Method should cite reject-option / selective-classification work only to
   justify the accept/reject/escalate decision space.
4. Threats should cite the oracle-problem survey and explicitly state that
   evaluator-only labels are a post-decision analysis join.
5. Discussion may use LLM-as-judge and automation-reliance sources to motivate
   bounded deployment caution, not to claim external validity.

## Unsupported or Over-strong Uses

- These references do not support a claim that the current EVP-8 verifier is
  reliable for autonomous patch correctness verification.
- They do not support LLM superiority over deterministic visible-tool baselines.
- They do not remove the need to report the 98-candidate cohort boundary,
  label distribution, and confidence intervals.
- They do not justify reintroducing the invalid early setting as a main result.
