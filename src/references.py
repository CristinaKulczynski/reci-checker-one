import re
import xml.etree.ElementTree as ET
from structure import get_sections


def validate_vancouver_format(references_text):
    """
    Validates if references follow Vancouver style formatting.

    Vancouver style characteristics:
    - References numbered sequentially (1., 2., 3., etc.)
    - Author names: Surname Initials (without periods between initials)
    - Journal articles: Authors. Title. Journal abbreviation. Year;volume(issue):pages. DOI/URL
    - Multiple authors separated by commas
    - "et al." for more than 6 authors
    - Journal names abbreviated
    - Year, volume, issue, and page numbers in specific format
    """

    if not references_text or references_text.strip() == "":
        return False, "Seção de referências não encontrada ou vazia"

    # Remove both Portuguese and English reference headers
    text = re.sub(r'^[.\d\s]*REFER[ÊE]NCIAS?\s*\.?\s*', '',
                  references_text, flags=re.IGNORECASE)
    text = re.sub(r'^[.\d\s]*REFERENCE[S]?\s*\.?\s*',
                  '', text, flags=re.IGNORECASE)

    # Split by reference numbers (1-3 digits followed by period and space, then author name)
    # The lookahead checks for either:
    # - Uppercase letter (normal surnames: Smith, Jones)
    # - Lowercase word (2-4 letters) followed by space and uppercase (particles: dos Santos, van der Waals)
    # This avoids matching abbreviations like "5. ed." or "p. 123"
    # This handles when all text is on one line (normalized by get_sections)
    references = re.split(
        r'(?:^|\s+)(\d{1,3})\.\s+(?=[A-Z]|[a-zà-ú]{2,4}\s+[A-Z])', text.strip())

    paired_refs = []
    for i in range(1, len(references), 2):
        if i+1 < len(references):
            ref_content = references[i+1].strip()
            if ref_content:
                paired_refs.append(ref_content)

    references = paired_refs

    if len(references) == 0:
        return False, "Nenhuma referência identificada"

    issues = []
    valid_count = 0

    for i, ref in enumerate(references, 1):
        ref_issues = []

        # Check 1: Should have author names (at least one capital letter followed by letters)
        # Vancouver: Authors with surnames and initials
        author_pattern = r'[A-ZÀ-Ú][a-zà-ú]+\s+[A-ZÀ-Ú]{1,3}'
        if not re.search(author_pattern, ref):
            ref_issues.append("formato de autores inválido")

        # Check 2: Should have a title (text followed by period)
        # Titles in Vancouver end with a period
        title_pattern = r'\.\s+[A-ZÀ-Ú].+?\.'
        if not re.search(title_pattern, ref):
            ref_issues.append("título não identificado")

        # Check 3: Should have year (4 digits)
        year_pattern = r'\b(19|20)\d{2}\b'
        if not re.search(year_pattern, ref):
            ref_issues.append("ano não identificado")

        # Check 4: For journal articles, check for volume/issue/pages pattern
        # Vancouver format: Year;volume(issue):pages or Year Month;volume(issue):pages
        journal_pattern = r'(19|20)\d{2}[^;]*;[\d]+\([\d]+\):[\d]+[-–]?[\d]*'
        has_journal_format = re.search(journal_pattern, ref)

        # Check 5: Should have DOI or URL (most modern references)
        doi_url_pattern = r'(https?://|doi\.org/|DOI:|https://doi\.org/)'
        has_doi_or_url = re.search(doi_url_pattern, ref, re.IGNORECASE)

        # Check 6: Should have period at the end
        if not ref.strip().endswith('.'):
            ref_issues.append("falta ponto final")

        # Check 7: Check for "et al." format (Vancouver uses "et al.")
        # If "et al." is present, it should be formatted correctly
        if 'et al' in ref.lower():
            if not re.search(r'et al\.', ref):
                ref_issues.append("'et al.' sem ponto")

        # A reference is considered valid if it has:
        # - Authors
        # - Title
        # - Year
        # - Either journal format OR URL/DOI
        # - Proper ending punctuation
        if len(ref_issues) <= 2:  # Allow up to 2 minor issues
            valid_count += 1
        else:
            issues.append(f"Ref {i}: {', '.join(ref_issues)}")

    total_refs = len(references)
    compliance_rate = (valid_count / total_refs) * 100 if total_refs > 0 else 0

    if compliance_rate == 100:
        return True, f"{valid_count}/{total_refs} referências em formato Vancouver"
    else:
        issue_summary = "; ".join(issues[:3])
        if len(issues) > 3:
            issue_summary += f" (e mais {len(issues)-3} problemas)"
        return False, f"Apenas {valid_count}/{total_refs} em formato adequado. {issue_summary}"


def extract_doi_and_urls(references_text):
    """
    Extracts and validates DOI and electronic addresses from references.

    Returns tuple: (has_all_dois_or_urls, message, details_list)
    """
    if not references_text or references_text.strip() == "":
        return False, "Seção de referências não encontrada ou vazia", []

    # Remove both Portuguese and English reference headers
    text = re.sub(r'^[.\d\s]*REFER[ÊE]NCIAS?\s*\.?\s*', '',
                  references_text, flags=re.IGNORECASE)
    text = re.sub(r'^[.\d\s]*REFERENCE[S]?\s*\.?\s*',
                  '', text, flags=re.IGNORECASE)

    # Split by reference numbers (1-3 digits followed by period and space, then author name)
    # The lookahead checks for either:
    # - Uppercase letter (normal surnames: Smith, Jones)
    # - Lowercase word (2-4 letters) followed by space and uppercase (particles: dos Santos, van der Waals)
    # This avoids matching abbreviations like "5. ed." or "p. 123"
    # This handles when all text is on one line (normalized by get_sections)
    references = re.split(
        r'(?:^|\s+)(\d{1,3})\.\s+(?=[A-Z]|[a-zà-ú]{2,4}\s+[A-Z])', text.strip())

    # After split, we get: ['', '1', 'ref1_content', '2', 'ref2_content', ...]
    # Need to pair each number with its content
    paired_refs = []
    for i in range(1, len(references), 2):
        if i+1 < len(references):
            ref_content = references[i+1].strip()
            if ref_content:
                paired_refs.append(ref_content)

    references = paired_refs

    if len(references) == 0:
        return False, "Nenhuma referência identificada", []

    details = []
    refs_with_doi_or_url = 0

    # Patterns for DOI and URLs
    doi_pattern = r'(https?://)?doi\.org/[^\s]+'
    doi_direct_pattern = r'DOI:\s*[^\s]+'
    url_pattern = r'https?://[^\s]+'
    available_from_pattern = r'Available from:\s*(https?://[^\s]+)'

    for i, ref in enumerate(references, 1):
        has_doi = False
        has_url = False
        extracted_info = []

        # Check for DOI (various formats)
        doi_match = re.search(doi_pattern, ref, re.IGNORECASE)
        if doi_match:
            has_doi = True
            extracted_info.append(f"DOI: {doi_match.group(0)}")

        if not has_doi:
            doi_direct_match = re.search(
                doi_direct_pattern, ref, re.IGNORECASE)
            if doi_direct_match:
                has_doi = True
                extracted_info.append(f"{doi_direct_match.group(0)}")

        # Check for URLs
        url_match = re.search(url_pattern, ref, re.IGNORECASE)
        if url_match and not has_doi:  # Don't double-count DOI URLs
            has_url = True
            extracted_info.append(f"URL: {url_match.group(0)}")

        # Check for "Available from:" pattern
        available_match = re.search(available_from_pattern, ref, re.IGNORECASE)
        if available_match and not has_doi and not has_url:
            has_url = True
            extracted_info.append(f"URL: {available_match.group(1)}")

        # Check for "Disponível em:" pattern (Portuguese)
        disponivel_pattern = r'Disponível em:\s*(https?://[^\s]+)'
        disponivel_match = re.search(disponivel_pattern, ref, re.IGNORECASE)
        if disponivel_match and not has_doi and not has_url:
            has_url = True
            extracted_info.append(f"URL: {disponivel_match.group(1)}")

        if has_doi or has_url:
            refs_with_doi_or_url += 1
            details.append({
                "ref_num": i,
                "has_identifier": True,
                "info": ", ".join(extracted_info)
            })
        else:
            details.append({
                "ref_num": i,
                "has_identifier": False,
                "info": "Sem DOI ou URL identificado"
            })

    total_refs = len(references)
    all_have_identifier = refs_with_doi_or_url == total_refs

    if all_have_identifier:
        message = f"Todas as {total_refs} referências possuem DOI ou URL"
        return True, message, details
    else:
        missing = total_refs - refs_with_doi_or_url
        missing_refs = [str(d["ref_num"])
                        for d in details if not d["has_identifier"]]
        message = f"{refs_with_doi_or_url}/{total_refs} referências com DOI/URL. Faltam nas refs: {', '.join(missing_refs[:5])}"
        if len(missing_refs) > 5:
            message += f" (e mais {len(missing_refs) - 5})"
        return False, message, details


def item_66(manuscript_text):
    description = "Apresentam-se nas Normas de Vancouver."
    status = "NA"
    comments = ""

    sections = get_sections(manuscript_text)
    references = sections.get("REFERENCES")

    if not references:
        status = "NA"
        comments = "Seção de referências não encontrada"
    else:
        is_valid, message = validate_vancouver_format(references)

        if is_valid:
            status = "A"
            comments = message
        else:
            status = "NA"
            comments = message

    return {
        "item": 66,
        "description": description,
        "status": status,
        "comments": comments
    }


def item_69(xml_path):
    description = "Estão em fonte 12, espaçamento simples, justificado."

    try:
        tree = ET.parse(xml_path)
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        paragraphs = tree.findall('.//w:p', ns)

        # Find references section boundaries
        ref_start = _find_references_start(paragraphs, ns)
        if ref_start is None:
            return {"item": 69, "description": description, "status": "NA",
                    "comments": "Seção de referências não encontrada"}

        ref_end = _find_references_end(paragraphs, ref_start, ns)

        # Validate each reference
        issues = []
        total_refs = 0

        for para in paragraphs[ref_start:ref_end]:
            text = ''.join([t.text for t in para.findall(
                './/w:t', ns) if t.text]).strip()

            # Only check numbered references
            if not text or not re.match(r'^\d+\.', text):
                continue

            total_refs += 1
            ref_issues = _check_reference_format(para, ns, total_refs)
            issues.extend(ref_issues)

        if total_refs == 0:
            return {"item": 69, "description": description, "status": "NA",
                    "comments": "Nenhuma referência numerada encontrada"}

        # Build result
        if not issues:
            return {"item": 69, "description": description, "status": "A",
                    "comments": f"{total_refs} referências formatadas corretamente"}

        summary = f"{total_refs} referências. Problemas: {'; '.join(issues[:3])}"
        if len(issues) > 3:
            summary += f" (e mais {len(issues) - 3})"

        return {"item": 69, "description": description, "status": "NA", "comments": summary}

    except Exception as e:
        return {"item": 69, "description": description, "status": "-",
                "comments": f"Erro: {str(e)}"}


def _find_references_start(paragraphs, ns):
    """Find the index where references section starts."""
    for i, para in enumerate(paragraphs):
        text = ''.join([t.text for t in para.findall(
            './/w:t', ns) if t.text]).strip()
        if re.match(r'^\d*\s*REFER[ÊE]NCIAS?\s*$|^\d*\s*REFERENCES?\s*$', text, re.IGNORECASE):
            return i + 1
    return None


def _find_references_end(paragraphs, start_idx, ns):
    """Find the index where references section ends."""
    for i in range(start_idx, len(paragraphs)):
        text = ''.join([t.text for t in paragraphs[i].findall(
            './/w:t', ns) if t.text]).strip()
        if re.match(r'^CONTRIBUI[ÇC][ÕO]ES?\s*$|^CONTRIBUTIONS?\s*$', text, re.IGNORECASE):
            return i
    return len(paragraphs)


def _check_reference_format(para, ns, ref_num):
    """Check font size, spacing, and alignment for a reference paragraph."""
    issues = []

    # Check font size (24 half-points = 12pt)
    font_sizes = {sz.get(f'{{{ns["w"]}}}val')
                  for sz in para.findall('.//w:sz', ns) if sz.get(f'{{{ns["w"]}}}val')}

    if font_sizes:
        if len(font_sizes) > 1:
            issues.append(f"Ref {ref_num}: fontes mistas")
        elif '24' not in font_sizes:
            size = int(list(font_sizes)[0]) / 2
            issues.append(f"Ref {ref_num}: fonte {size}pt")

    # Check spacing (must be simple/single)
    spacing = para.find('.//w:spacing', ns)
    if spacing is not None:
        line_rule = spacing.get(f'{{{ns["w"]}}}lineRule')
        line_val = spacing.get(f'{{{ns["w"]}}}line')
        if (line_rule == "auto" and line_val and line_val != "240") or \
           (line_rule and line_rule != "auto"):
            issues.append(f"Ref {ref_num}: espaçamento incorreto")

    # Check alignment (must be 'both' = justified)
    jc = para.find('.//w:jc', ns)
    alignment = jc.get(f'{{{ns["w"]}}}val') if jc is not None else None
    if alignment != 'both':
        align_name = {'left': 'esquerda', 'right': 'direita',
                      'center': 'centro'}.get(alignment, 'não especificado')
        issues.append(f"Ref {ref_num}: {align_name}")

    return issues


def item_71(manuscript_text):
    description = "Apresentam DOI nas referências ou endereço eletrônico."
    status = "NA"
    comments = ""

    sections = get_sections(manuscript_text)
    references = sections.get("REFERENCES")

    if not references:
        status = "NA"
        comments = "Seção de referências não encontrada"
    else:
        has_all, message, details = extract_doi_and_urls(references)

        if has_all:
            status = "A"
            comments = message
        else:
            status = "NA"
            comments = message

    return {
        "item": 71,
        "description": description,
        "status": status,
        "comments": comments
    }


def validate_author_format(references_text):
    if not references_text or references_text.strip() == "":
        return False, "Seção de referências não encontrada ou vazia"

    # Remove both Portuguese and English reference headers
    text = re.sub(r'^[.\d\s]*REFER[ÊE]NCIAS?\s*\.?\s*', '',
                  references_text, flags=re.IGNORECASE)
    text = re.sub(r'^[.\d\s]*REFERENCE[S]?\s*\.?\s*',
                  '', text, flags=re.IGNORECASE)

    # Split by reference numbers (1-3 digits followed by period and space, then author name)
    # The lookahead checks for either:
    # - Uppercase letter (normal surnames: Smith, Jones)
    # - Lowercase word (2-4 letters) followed by space and uppercase (particles: dos Santos, van der Waals)
    # This avoids matching abbreviations like "5. ed." or "p. 123"
    # This handles when all text is on one line (normalized by get_sections)
    references = re.split(
        r'(?:^|\s+)(\d{1,3})\.\s+(?=[A-Z]|[a-zà-ú]{2,4}\s+[A-Z])', text.strip())

    paired_refs = []
    for i in range(1, len(references), 2):
        if i+1 < len(references):
            ref_content = references[i+1].strip()
            if ref_content:
                paired_refs.append(ref_content)

    references = paired_refs

    if len(references) == 0:
        return False, "Nenhuma referência identificada"

    issues = []
    valid_count = 0

    correct_author_pattern = r'[A-ZÀ-Ú][a-zà-úç]+\s+[A-ZÀ-Ú]{1,3}(?![.])'

    # Match initials with periods that are part of author format, not sentence-ending periods
    # Look for: Surname Initial. followed by either another Initial or a comma (next author)
    # This avoids matching "Gilbert R." where the period ends the author list
    incorrect_period_pattern = r'[A-ZÀ-Ú][a-zà-úç]+\s+[A-ZÀ-Ú]\.\s*(?:[A-ZÀ-Ú]\.|,)'

    # Match lowercase surnames, but exclude valid name particles (de, da, do, dos, das, del, della, van, von, etc.)
    # These particles are correct in Portuguese, Spanish, Dutch, German names
    name_particles = r'\b(?:de|da|do|dos|das|del|della|di|van|von|der|den|het|ter|te|ten|el|la|las|los)\b'
    lowercase_surname_pattern = r'\b(?!(?:de|da|do|dos|das|del|della|di|van|von|der|den|het|ter|te|ten|el|la|las|los)\b)[a-zà-úç]+\s+[A-ZÀ-Ú]{1,3}\b'

    for i, ref in enumerate(references, 1):
        ref_issues = []

        # Extract just the author section by finding where the title starts
        # Authors end at: period + space + capitalized word (3+ chars) or after "et al."
        # This prevents matching words in the article title
        author_end_match = re.search(
            r'(et\s+al\.?|[A-ZÀ-Ú]{1,3}\.)\s+([A-ZÀ-Ú][a-zà-ú]{3,})', ref)
        if author_end_match:
            # End just before the title word starts
            author_section = ref[:author_end_match.start(
            ) + len(author_end_match.group(1)) + 1]
        else:
            # Fallback to first 150 chars if we can't find a clear boundary
            author_section = ref[:150]

        if re.search(incorrect_period_pattern, author_section):
            ref_issues.append("iniciais com pontos")

        if re.search(lowercase_surname_pattern, author_section):
            ref_issues.append("sobrenome em minúscula")

        has_correct_authors = re.search(correct_author_pattern, author_section)

        if not has_correct_authors:
            if not ref_issues:
                ref_issues.append("formato de autores não identificado")

        if not ref_issues:
            valid_count += 1
        else:
            issues.append(f"Ref {i}: {', '.join(ref_issues)}")

    total_refs = len(references)
    compliance_rate = (valid_count / total_refs) * 100 if total_refs > 0 else 0

    if compliance_rate == 100:
        return True, f"{valid_count}/{total_refs} referências com formatação correta de autores"
    else:
        issue_summary = "; ".join(issues[:5])
        if len(issues) > 5:
            issue_summary += f" (e mais {len(issues)-5} problemas)"
        return False, f"Apenas {valid_count}/{total_refs} com formato adequado. {issue_summary}"


def item_72(manuscript_text):
    description = "Referencia-se o(s) autor(e)s pelo sobrenome. A letra inicial é maiúscula, seguida do(s) nome(s) abreviado(s) e sem o ponto."
    status = "NA"
    comments = ""

    sections = get_sections(manuscript_text)
    references = sections.get("REFERENCES")

    if not references:
        status = "NA"
        comments = "Seção de referências não encontrada"
    else:
        is_valid, message = validate_author_format(references)

        if is_valid:
            status = "A"
            comments = message
        else:
            status = "NA"
            comments = message

    return {
        "item": 72,
        "description": description,
        "status": status,
        "comments": comments
    }


def validate_et_al_usage(references_text):
    """
    Validates that references with "et al" have at least 3 author names before it.

    Returns tuple: (is_valid, message)
    """
    if not references_text or references_text.strip() == "":
        return False, "Seção de referências não encontrada ou vazia"

    # Remove both Portuguese and English reference headers
    text = re.sub(r'^[.\d\s]*REFER[ÊE]NCIAS?\s*\.?\s*', '',
                  references_text, flags=re.IGNORECASE)
    text = re.sub(r'^[.\d\s]*REFERENCE[S]?\s*\.?\s*',
                  '', text, flags=re.IGNORECASE)

    # Split by reference numbers (1-3 digits followed by period and space, then author name)
    # The lookahead checks for either:
    # - Uppercase letter (normal surnames: Smith, Jones)
    # - Lowercase word (2-4 letters) followed by space and uppercase (particles: dos Santos, van der Waals)
    # This avoids matching abbreviations like "5. ed." or "p. 123"
    # This handles when all text is on one line (normalized by get_sections)
    references = re.split(
        r'(?:^|\s+)(\d{1,3})\.\s+(?=[A-Z]|[a-zà-ú]{2,4}\s+[A-Z])', text.strip())

    paired_refs = []
    for i in range(1, len(references), 2):
        if i+1 < len(references):
            ref_content = references[i+1].strip()
            if ref_content:
                paired_refs.append(ref_content)

    references = paired_refs

    if len(references) == 0:
        return False, "Nenhuma referência identificada"

    issues = []
    refs_with_et_al = 0
    valid_et_al_count = 0

    # Author pattern that handles both Vancouver formats:
    # 1. "Surname Initials" (e.g., "Smith AB", "Jones CD")
    # 2. "Surname, Initials." (e.g., "Smith, A. B.", "Aguilar, R. S.")
    author_pattern = r'[A-ZÀ-Ú][a-zà-úç]+(?:\s+[A-ZÀ-Ú]{1,3}(?![.])|,\s+[A-ZÀ-Ú]\.?\s*[A-ZÀ-Ú]?\.?\s*[A-ZÀ-Ú]?\.?)'

    for i, ref in enumerate(references, 1):
        if re.search(r'et\s+al\.?', ref, re.IGNORECASE):
            refs_with_et_al += 1

            et_al_match = re.search(r'(.+?)\s+et\s+al\.?', ref, re.IGNORECASE)
            if et_al_match:
                before_et_al = et_al_match.group(1)

                authors = re.findall(author_pattern, before_et_al)
                author_count = len(authors)

                if author_count >= 3:
                    valid_et_al_count += 1
                else:
                    issues.append(
                        f"Ref {i}: apenas {author_count} autor(es) antes de 'et al' (mínimo: 3)")

    if refs_with_et_al == 0:
        return True, "Nenhuma referência usa 'et al'"

    if valid_et_al_count == refs_with_et_al:
        return True, f"{refs_with_et_al} referência(s) com 'et al' formatadas corretamente"
    else:
        issue_summary = "; ".join(issues[:5])
        if len(issues) > 5:
            issue_summary += f" (e mais {len(issues)-5} problemas)"
        return False, f"{valid_et_al_count}/{refs_with_et_al} com 'et al' adequado. {issue_summary}"


def item_73(manuscript_text):
    description = "Citam pelo menos três nomes dos autores antes da expressão 'et al'."
    status = "NA"
    comments = ""

    sections = get_sections(manuscript_text)
    references = sections.get("REFERENCES")

    if not references:
        status = "NA"
        comments = "Seção de referências não encontrada"
    else:
        is_valid, message = validate_et_al_usage(references)

        if is_valid:
            status = "A"
            comments = message
        else:
            status = "NA"
            comments = message

    return {
        "item": 73,
        "description": description,
        "status": status,
        "comments": comments
    }
