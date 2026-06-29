import subprocess, sys, tempfile, os, textwrap

def run(spec_text):
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
        f.write(spec_text); path = f.name
    r = subprocess.run([sys.executable, "validate_spec.py", path],
                       cwd=os.path.dirname(__file__) or ".",
                       capture_output=True, text=True)
    os.unlink(path)
    return r.returncode, r.stdout + r.stderr

def test_valid_spec_passes():
    spec = textwrap.dedent("""
    journal: Science
    article_type: Research Article
    word_limits: {abstract: 125, main_text: 4500, per_section: {}, references_max: 60}
    abstract: {max_words: 125, structured: false, sections: []}
    references: {style: Science, csl: science.csl, max_count: 60, format_notes: ""}
    figures: {max_count: 6, formats: [tiff, eps], min_dpi: 300, color_mode: RGB, max_dimensions: "", min_font_pt: 6}
    tables: {max_count: 4, formats: [docx], format_notes: ""}
    supplementary: {allowed: true, rules: ""}
    sections: [Abstract, Introduction, Results, Discussion, Methods]
    statements: [data_availability, code_availability]
    cover_letter: {required: true, elements: [significance]}
    forms: [author_contributions]
    file_formats: {manuscript: docx, figures: tiff, tables: docx}
    flagged: []
    """)
    code, out = run(spec)
    assert code == 0, out

def test_missing_key_fails():
    spec = "journal: Science\narticle_type: Research Article\n"
    code, out = run(spec)
    assert code != 0
    assert "missing" in out.lower()
