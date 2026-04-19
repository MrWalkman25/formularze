import re
from core.pdf_layout_parser import build_text_lines, build_label_phrases

POLISH_GOV_FORM_LABELS = {
    "meta_instructions": [
        "wypełnij wielkimi literami",
        "wypełniać dużymi drukowanymi literami",
        "wypełnij kolorem czarnym lub niebieskim",
        "pola wyboru zaznacz znakiem x",
        "zaznaczyć właściwy kwadrat",
        "zaznacz właściwe pole",
        "niepotrzebne skreślić",
        "to pole jest dobrowolne",
        "należy wypełnić tylko wówczas, gdy",
        "podaj, jeśli nie masz nadanego numeru pesel",
        "podaj, jeśli nie ma nadanego nip",
        "podaj, jeśli nie ma nadanego nip, regon",
        "podaj, jeśli nie ma nadanego nip, regon, pesel",
        "podaj, jeśli twój adres jest inny niż polski",
        "podaj, jeśli adres jest inny niż polski",
    ],

    "submission_context": [
        "miejsce złożenia zgłoszenia",
        "miejsce złożenia wniosku",
        "naczelnik urzędu skarbowego",
        "urząd skarbowy",
        "adresat",
        "dane organu gminy, do którego kierowany jest wniosek",
        "nazwa organu gminy",
        "typ wniosku",
        "tryb złożenia wniosku",
        "status",
        "numer dokumentu",
    ],

    "person_identity_core": [
        "dane składającego",
        "dane wnioskodawcy",
        "dane podatnika",
        "dane identyfikacyjne",
        "twoje dane",
        "imię",
        "imiona",
        "imię pierwsze",
        "pierwsze imię",
        "drugie imię",
        "nazwisko",
        "nazwisko rodowe",
        "poprzednie nazwisko",
        "imię ojca",
        "imię matki",
        "data urodzenia",
        "miejsce urodzenia",
        "obywatelstwo",
        "nazwa albo imię i nazwisko",
        "nazwa",
    ],

    "identity_numbers": [
        "identyfikator podatkowy nip",
        "identyfikator podatkowy",
        "nip",
        "numer nip",
        "regon",
        "pesel",
        "numer pesel",
        "pesel/krs",
        "krs",
        "rodzaj, seria i numer dokumentu",
        "seria i numer dowodu osobistego",
        "numer i seria paszportu",
        "dokument potwierdzający tożsamość",
        "rodzaj, seria i numer dokumentu potwierdzającego tożsamość",
        "inny numer identyfikacyjny",
    ],

    "address_primary": [
        "adres miejsca zamieszkania",
        "adres zamieszkania",
        "adres korespondencyjny",
        "adres do doręczeń",
        "adres elektroniczny",
        "adres skrzynki epuap",
        "adres skrzynki e-doręczenia",
        "ostatnie znane miejsce zameldowania",
        "adres zameldowania na pobyt stały",
        "adres zameldowania na pobyt czasowy",
    ],

    "address_parts": [
        "kraj",
        "województwo",
        "powiat",
        "gmina",
        "miejscowość",
        "ulica",
        "nr domu",
        "numer domu",
        "nr lokalu",
        "numer lokalu",
        "kod pocztowy",
        "nazwa państwa",
        "skrytka pocztowa",
    ],

    "contact_fields": [
        "dane kontaktowe",
        "telefon",
        "numer telefonu",
        "fax",
        "faks",
        "e-mail",
        "email",
        "adres e-mail",
        "adres poczty elektronicznej",
        "strona internetowa",
    ],

    "contact_optout_or_flags": [
        "rezygnacja z telefonu",
        "rezygnacja z faksu",
        "rezygnacja z e-mail",
        "rezygnacja z email",
        "adres do doręczeń",
        "utrata aktualności ostatnio wskazanego adresu do doręczeń",
        "tak",
        "nie",
    ],

    "business_identity": [
        "nazwa firmy",
        "nazwa skrócona",
        "firma przedsiębiorcy",
        "data rozpoczęcia wykonywania działalności",
        "data rozpoczęcia działalności",
        "miejsce wykonywania działalności",
        "stałe miejsce wykonywania działalności",
        "dodatkowe miejsce wykonywania działalności",
        "przeważający kod pkd",
        "kody pkd",
        "pkd",
        "liczba pracowników",
    ],

    "social_security_context": [
        "dane płatnika składek",
        "dane osoby ubezpieczonej",
        "ubezpieczony wnioskuje o",
        "zatrudnienie / tytuł ubezpieczenia trwa nadal",
        "zasiłek chorobowy",
        "zasiłek opiekuńczy",
        "świadczenie rehabilitacyjne",
        "za okres",
        "podaj okres zwolnienia",
    ],

    "banking": [
        "rachunek bankowy",
        "rachunek osobisty",
        "numer rachunku",
        "numer rachunku bankowego",
        "iban",
    ],

    "representation": [
        "w czyim imieniu jest składany wniosek",
        "we własnym imieniu",
        "jako pełnomocnik",
        "dane pełnomocnika",
        "dane identyfikacyjne pełnomocnika",
        "dane kontaktowe pełnomocnika",
        "pełnomocnik",
        "dokument stwierdzający udzielenie pełnomocnictwa",
    ],

    "dates_and_date_masks": [
        "data",
        "data wypełnienia wniosku",
        "od kiedy",
        "z dnia",
        "dzień - miesiąc - rok",
        "dd / mm / rrrr",
        "dd-mm-rrrr",
        "dd/mm/rrrr",
        "daty od-do",
        "od",
        "do",
        "okres",
    ],

    "signature_block": [
        "oświadczenia, podpisy",
        "czytelny podpis",
        "podpis wnioskodawcy",
        "podpis pełnomocnika",
        "podpis wnioskodawcy albo pełnomocnika",
        "podpis urzędnika",
        "miejscowość",
        "data",
        "podpis",
        "pieczęć i podpis",
    ],

    "checkbox_binary_pairs": [
        "tak",
        "nie",
        "1. tak",
        "2. nie",
        "występuję o",
        "ubezpieczony wnioskuje o",
        "czy masz ustalone prawo do",
        "czy wierzyciel jest osobą fizyczną",
        "pierwsza deklaracja",
        "zmiana",
        "aktualizacja danych",
        "adres do doręczeń tak nie",
    ],

    "high_value_masked_fields": [
        "nip",
        "regon",
        "pesel",
        "kod pocztowy",
        "data urodzenia",
        "data",
        "numer dokumentu",
        "numer rachunku",
        "rachunek bankowy",
        "pkd",
    ],

    "field_type_hints": {
        "checkbox": [
            "tak",
            "nie",
            "rezygnacja z telefonu",
            "rezygnacja z faksu",
            "rezygnacja z e-mail",
            "rezygnacja z email",
            "we własnym imieniu",
            "jako pełnomocnik",
            "pierwsza deklaracja",
            "zmiana",
            "aktualizacja danych",
            "adres do doręczeń",
            "z rejestru mieszkańców",
            "z rejestru pesel",
        ],
        "date": [
            "data",
            "data urodzenia",
            "data wypełnienia wniosku",
            "z dnia",
            "od kiedy",
            "dd / mm / rrrr",
            "dd-mm-rrrr",
            "dd/mm/rrrr",
            "dzień - miesiąc - rok",
        ],
        "masked_text": [
            "nip",
            "regon",
            "pesel",
            "kod pocztowy",
            "numer dokumentu",
            "numer rachunku",
            "rachunek bankowy",
            "iban",
            "pkd",
        ],
        "text": [
            "imię",
            "imiona",
            "nazwisko",
            "nazwisko rodowe",
            "imię ojca",
            "imię matki",
            "miejsce urodzenia",
            "obywatelstwo",
            "ulica",
            "nr domu",
            "numer domu",
            "nr lokalu",
            "numer lokalu",
            "miejscowość",
            "powiat",
            "gmina",
            "województwo",
            "kraj",
            "nazwa państwa",
            "telefon",
            "numer telefonu",
            "e-mail",
            "email",
            "nazwa firmy",
            "nazwa skrócona",
            "miejsce wykonywania działalności",
            "adres skrzynki epuap",
            "adres skrzynki e-doręczenia",
        ],
        "multiline_text": [
            "treść wniosku",
            "uzasadnienie potrzeby uzyskania danych",
            "inne dane",
            "inne",
            "opisz jakim",
        ]
    },

    "semantic_aliases": {
        "id_nip": ["nip", "identyfikator podatkowy nip", "numer nip"],
        "id_regon": ["regon"],
        "id_pesel": ["pesel", "numer pesel", "nr pesel"],
        "person_first_name": ["imię", "imię pierwsze", "pierwsze imię"],
        "person_middle_name": ["drugie imię"],
        "person_last_name": ["nazwisko"],
        "person_birth_surname": ["nazwisko rodowe"],
        "person_father_name": ["imię ojca"],
        "person_mother_name": ["imię matki"],
        "person_birth_date": ["data urodzenia"],
        "person_birth_place": ["miejsce urodzenia"],
        "person_citizenship": ["obywatelstwo"],
        "address_country": ["kraj", "nazwa państwa"],
        "address_province": ["województwo"],
        "address_county": ["powiat"],
        "address_commune": ["gmina"],
        "address_city": ["miejscowość"],
        "address_street": ["ulica"],
        "address_building_no": ["nr domu", "numer domu"],
        "address_apartment_no": ["nr lokalu", "numer lokalu"],
        "address_zip": ["kod pocztowy"],
        "contact_phone": ["telefon", "numer telefonu"],
        "contact_fax": ["fax", "faks"],
        "contact_email": ["e-mail", "email", "adres e-mail"],
        "contact_epuap": ["adres skrzynki epuap"],
        "contact_edoreczenia": ["adres skrzynki e-doręczenia"],
        "bank_account": ["rachunek bankowy", "rachunek osobisty", "numer rachunku", "iban"],
        "business_name": ["nazwa firmy", "firma przedsiębiorcy"],
        "business_short_name": ["nazwa skrócona"],
        "business_start_date": ["data rozpoczęcia wykonywania działalności", "data rozpoczęcia działalności"],
        "business_pkd": ["pkd", "kody pkd", "przeważający kod pkd"],
        "checkbox_yes": ["tak", "1. tak"],
        "checkbox_no": ["nie", "2. nie"],
        "optout_phone": ["rezygnacja z telefonu"],
        "optout_fax": ["rezygnacja z faksu"],
        "optout_email": ["rezygnacja z e-mail", "rezygnacja z email"],
        "signature": ["czytelny podpis", "podpis", "podpis wnioskodawcy", "podpis pełnomocnika"],
        "fill_date": ["data wypełnienia wniosku", "data"],
        "fill_place": ["miejscowość"],
    }
}

def normalize_label_text(text: str) -> str:
    text = text.lower().strip()

    # Unifikacja typowych separatorів i dashy
    text = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")

    # Ujednolicenia częstych wariantów
    text = re.sub(r"\be[\-\s]?mail\b", "email", text)
    text = re.sub(r"\bnr\.\b", "nr", text)
    text = re.sub(r"\bnr(?=\s)", "nr", text)

    # Usuwamy wiodące numeratory: 1., 2), a), (1), (a)
    text = re.sub(r"^\(\s*(?:\d+|[a-z])\s*\)\s*", "", text)
    text = re.sub(r"^(?:\d+|[a-z])[\.\)]\s*", "", text)

    # Oczyszczanie końcowej interpunkcji
    text = re.sub(r"[\s:;,.]+$", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _tokenize_label(text: str) -> list[str]:
    if not text:
        return []
    return [t for t in re.split(r"[^\wąćęłńóśźż]+", text, flags=re.IGNORECASE) if t]


def _build_alias_index() -> tuple[dict[str, list[tuple[str, str]]], dict[str, set[str]]]:
    by_field = {}
    by_type = {}

    for field_id, aliases in POLISH_GOV_FORM_LABELS["semantic_aliases"].items():
        normalized_aliases = []
        for alias in aliases:
            n_alias = normalize_label_text(alias)
            normalized_aliases.append((alias, n_alias))
        by_field[field_id] = normalized_aliases

    for ftype, labels in POLISH_GOV_FORM_LABELS["field_type_hints"].items():
        by_type[ftype] = {normalize_label_text(label) for label in labels}

    return by_field, by_type


SEMANTIC_ALIAS_INDEX, FIELD_TYPE_HINT_INDEX = _build_alias_index()

def get_field_type_hint(normalized: str) -> str:
    for ftype, labels in FIELD_TYPE_HINT_INDEX.items():
        if normalized in labels:
            return ftype
    return "text"

def is_meta_instruction(normalized: str) -> bool:
    for instr in POLISH_GOV_FORM_LABELS["meta_instructions"]:
        if normalized == instr or instr in normalized:
            return True
    return False

def match_semantic_label(normalized: str) -> dict | None:
    if not normalized:
        return None

    best = None
    phrase_tokens = set(_tokenize_label(normalized))

    for field_id, aliases in SEMANTIC_ALIAS_INDEX.items():
        for raw_alias, alias in aliases:
            strategy = None
            score = 0.0

            if normalized == alias:
                score = 100.0
                strategy = "exact"
            elif alias and alias in normalized:
                score = 90.0
                strategy = "contains"
            elif normalized and normalized in alias:
                score = 88.0
                strategy = "reverse_contains"
            else:
                prefix_bonus = 0.0
                if normalized.startswith(alias) or alias.startswith(normalized):
                    prefix_bonus = 8.0
                elif normalized.endswith(alias) or alias.endswith(normalized):
                    prefix_bonus = 6.0

                alias_tokens = set(_tokenize_label(alias))
                if phrase_tokens and alias_tokens:
                    intersection = phrase_tokens & alias_tokens
                    union = phrase_tokens | alias_tokens
                    if union:
                        jaccard = len(intersection) / len(union)
                        overlap = len(intersection) / max(1, min(len(phrase_tokens), len(alias_tokens)))
                        score = max(jaccard * 100, overlap * 85) + prefix_bonus
                        strategy = "token_overlap" if prefix_bonus == 0 else "prefix_overlap"

            if strategy is None:
                continue

            # Wielopoziomowe progi akceptacji
            accepted = False
            if strategy == "exact":
                accepted = True
            elif strategy in {"contains", "reverse_contains"} and score >= 84:
                accepted = True
            elif strategy in {"prefix_overlap", "token_overlap"} and score >= 54:
                accepted = True

            if not accepted:
                continue

            if best is None or score > best["score"]:
                best = {
                    "field_id": field_id,
                    "alias": raw_alias,
                    "normalized_alias": alias,
                    "score": round(score, 2),
                    "strategy": strategy,
                }

    return best


def _iter_line_ngrams(line: dict, max_n: int = 6):
    words = line.get("words", [])
    if not words:
        return

    total = len(words)
    for start in range(total):
        for n in range(1, max_n + 1):
            end = start + n
            if end > total:
                break
            group = words[start:end]
            text = " ".join(w["text"] for w in group)
            yield {
                "x0": min(w["x0"] for w in group),
                "y0": min(w["y0"] for w in group),
                "x1": max(w["x1"] for w in group),
                "y1": max(w["y1"] for w in group),
                "text": text,
                "words": group,
                "source_line_text": line["text"],
                "source": f"ngram_{n}",
            }


def _build_phrase_candidates(lines: list[dict]) -> list[dict]:
    base_phrases = build_label_phrases(lines)
    candidates = []
    seen = set()

    for phrase in base_phrases:
        p = phrase.copy()
        p["source"] = "phrase_builder"
        candidates.append(p)

    for line in lines:
        # pełny tekst linii jako dodatkowy kandydat
        line_candidate = {
            "x0": line["x0"],
            "y0": line["y0"],
            "x1": line["x1"],
            "y1": line["y1"],
            "text": line["text"],
            "words": line["words"],
            "source_line_text": line["text"],
            "source": "full_line",
        }
        candidates.append(line_candidate)
        candidates.extend(_iter_line_ngrams(line, max_n=6))

    deduped = []
    for phrase in candidates:
        n_text = normalize_label_text(phrase["text"])
        key = (
            n_text,
            round(phrase["x0"], 1),
            round(phrase["y0"], 1),
            round(phrase["x1"], 1),
            round(phrase["y1"], 1),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(phrase)

    return deduped

def _rects_overlap(r1: dict, r2: dict) -> bool:
    return not (r1["x1"] <= r2["x0"] or r1["x0"] >= r2["x1"] or 
                r1["y1"] <= r2["y0"] or r1["y0"] >= r2["y1"])


def _candidate_key(candidate: dict, page_index: int) -> tuple:
    return (
        page_index,
        candidate["field_type"],
        normalize_label_text(candidate["label"]),
        round(candidate["x0"], 0),
        round(candidate["y0"], 0),
        round(candidate["x1"], 0),
        round(candidate["y1"], 0),
    )


def _fallback_geometry_for_label(phrase: dict, field_type: str) -> tuple[float, float, float, float]:
    px0, py0, px1, py1 = phrase["x0"], phrase["y0"], phrase["x1"], phrase["y1"]
    label_h = max(8.0, py1 - py0)
    label_w = max(20.0, px1 - px0)

    if field_type == "checkbox":
        size = max(14.0, label_h * 0.95)
        return px1 + 6, py0 + (label_h - size) / 2, px1 + 6 + size, py0 + (label_h + size) / 2

    if field_type == "date":
        width = max(110.0, label_w * 1.8)
        return px1 + 8, py0 - 1, px1 + 8 + width, py1 + 1

    if field_type == "masked_text":
        width = max(150.0, label_w * 2.2)
        return px1 + 8, py0 - 1, px1 + 8 + width, py1 + 1

    # text + multiline_text
    width = max(140.0, label_w * 2.0)
    height = label_h * (1.1 if field_type == "text" else 2.0)
    return px1 + 8, py0 - 1, px1 + 8 + width, py0 - 1 + height

def detect_field_candidates(words: list[dict], pdf_path: str = None, page_index: int = 0) -> list[dict]:
    from core.pdf_layout_parser import get_graphics, get_layout_lines, get_acroform_widgets

    candidates = []
    seen_keys = set()
    widget_rects = []

    # Krok 1: Próba pobrania natywnych pól z formularza AcroForm
    if pdf_path:
        widgets = get_acroform_widgets(pdf_path, page_index)
        if widgets:
            for w in widgets:
                widget_candidate = {
                    "x0": w["x0"],
                    "y0": w["y0"],
                    "x1": w["x1"],
                    "y1": w["y1"],
                    "label": w["field_name"],
                    "field_type": w["field_type"],
                    "is_high_value": False,
                    "page_index": page_index,
                    "debug": {
                        "source_text": w["field_name"],
                        "normalized_text": normalize_label_text(w["field_name"]),
                        "matched_field_id": w["field_name"],
                        "matched_alias": None,
                        "score": 100.0,
                        "page_index": page_index,
                        "matching_strategy": "acroform_widget",
                        "candidate_source": "acroform_widget",
                    },
                }
                candidates.append(widget_candidate)
                seen_keys.add(_candidate_key(widget_candidate, page_index))
                widget_rects.append(widget_candidate)

    # Krok 2: Fallback (Heurystyczny Rule-based Detector)
    lines = build_text_lines(words)
    phrases = _build_phrase_candidates(lines)
    graphics = []
    h_lines = []
    v_lines = []
    
    if pdf_path:
        graphics = get_graphics(pdf_path, page_index)
        h_lines, v_lines = get_layout_lines(pdf_path, page_index)

    for phrase in phrases:
        normalized_phrase = normalize_label_text(phrase["text"])
        
        # Ignorujemy instrukcje meta
        if is_meta_instruction(normalized_phrase):
            continue
            
        semantic_match = match_semantic_label(normalized_phrase)
        if not semantic_match:
            continue
        field_id = semantic_match["field_id"]
        field_type = get_field_type_hint(semantic_match["normalized_alias"])

        px0, py0, px1, py1 = phrase["x0"], phrase["y0"], phrase["x1"], phrase["y1"]
        label_height = py1 - py0
        label_width = px1 - px0

        is_high_value = normalized_phrase in POLISH_GOV_FORM_LABELS["high_value_masked_fields"] or \
                        any(normalized_phrase in aliases for aliases in POLISH_GOV_FORM_LABELS["semantic_aliases"].values() if any(a in POLISH_GOV_FORM_LABELS["high_value_masked_fields"] for a in aliases))

        geometry_strategy = "line_fallback"
        if field_type == "checkbox":
            nearest = find_nearest_rect(phrase, graphics)
            
            if nearest:
                candidate_x0 = nearest["x0"] - 1
                candidate_y0 = nearest["y0"] - 1
                candidate_x1 = nearest["x1"] + 1
                candidate_y1 = nearest["y1"] + 1
                geometry_strategy = "nearest_rect"
            else:
                candidate_x0, candidate_y0, candidate_x1, candidate_y1 = _fallback_geometry_for_label(phrase, field_type)
        else:
            left, top, right, bottom = find_cell_bounds_from_lines(phrase, h_lines, v_lines)
            
            if left != -1 and top != -1 and right != 10000 and bottom != 10000:
                candidate_x0 = max(px1 + 4, left + 2)
                candidate_y0 = top + 2
                candidate_x1 = right - 2
                candidate_y1 = bottom - 2
                geometry_strategy = "layout_cell"
                
                if candidate_x0 >= candidate_x1:
                    candidate_x0, candidate_y0, candidate_x1, candidate_y1 = _fallback_geometry_for_label(phrase, field_type)
                    geometry_strategy = "fallback_invalid_cell"
            else:
                candidate_x0, candidate_y0, candidate_x1, candidate_y1 = _fallback_geometry_for_label(phrase, field_type)

        new_candidate = {
            "x0": candidate_x0,
            "y0": candidate_y0,
            "x1": candidate_x1,
            "y1": candidate_y1,
            "label": field_id,
            "field_type": field_type,
            "is_high_value": is_high_value,
            "page_index": page_index,
            "debug": {
                "source_text": phrase["text"],
                "normalized_text": normalized_phrase,
                "matched_field_id": field_id,
                "matched_alias": semantic_match["alias"],
                "score": semantic_match["score"],
                "page_index": page_index,
                "matching_strategy": semantic_match["strategy"],
                "candidate_source": phrase.get("source", "unknown"),
                "geometry_strategy": geometry_strategy,
            },
        }

        # Priorytet dla natywnych widgetów AcroForm
        if any(_rects_overlap(new_candidate, w) for w in widget_rects):
            continue

        c_key = _candidate_key(new_candidate, page_index)
        if c_key in seen_keys:
            continue
        seen_keys.add(c_key)
        candidates.append(new_candidate)

    return candidates

def find_cell_bounds_from_lines(phrase: dict, h_lines: list[dict], v_lines: list[dict]) -> tuple[float, float, float, float]:
    px0, py0, px1, py1 = phrase["x0"], phrase["y0"], phrase["x1"], phrase["y1"]
    pmx = (px0 + px1) / 2
    pmy = (py0 + py1) / 2
    
    top_line_y = -1
    for l in h_lines:
        if l["x0"] - 5 <= pmx <= l["x1"] + 5:
            if l["y"] <= py0 + 8 and l["y"] > top_line_y:
                top_line_y = l["y"]
                
    bottom_line_y = 10000
    for l in h_lines:
        if l["x0"] - 5 <= pmx <= l["x1"] + 5:
            if l["y"] >= py1 - 8 and l["y"] < bottom_line_y:
                bottom_line_y = l["y"]
                
    left_line_x = -1
    for l in v_lines:
        if l["y0"] - 5 <= pmy <= l["y1"] + 5:
            if l["x"] <= px0 + 8 and l["x"] > left_line_x:
                left_line_x = l["x"]
                
    right_line_x = 10000
    for l in v_lines:
        if l["y0"] - 5 <= pmy <= l["y1"] + 5:
            if l["x"] >= px1 - 8 and l["x"] < right_line_x:
                right_line_x = l["x"]
                
    return left_line_x, top_line_y, right_line_x, bottom_line_y

def find_nearest_rect(phrase: dict, graphics: list[dict], max_dist: float = 35.0) -> dict:
    if not graphics:
        return None

    px0, py0, px1, py1 = phrase["x0"], phrase["y0"], phrase["x1"], phrase["y1"]
    pmx = (px0 + px1) / 2
    pmy = (py0 + py1) / 2
    
    best_rect = None
    min_dist = float("inf")

    for r in graphics:
        rmx = (r["x0"] + r["x1"]) / 2
        rmy = (r["y0"] + r["y1"]) / 2

        dist_left = abs(r["x1"] - px0) + abs(rmy - pmy) * 1.5
        dist_right = abs(r["x0"] - px1) + abs(rmy - pmy) * 1.5
        dist_bottom = abs(rmx - pmx) + abs(r["y0"] - py1) * 0.8

        d = min(dist_left, dist_right, dist_bottom)

        if d < min_dist and d < max_dist:
            min_dist = d
            best_rect = r

    return best_rect
