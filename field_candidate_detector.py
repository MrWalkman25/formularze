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
    text = text.strip().lower()
    text = re.sub(r"^\d+[\.\)]\s*", "", text)
    text = re.sub(r"^[a-zA-Z][\.\)]\s*", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[:;,\.]$", "", text)
    return text.strip()

def get_field_type_hint(normalized: str) -> str:
    for ftype, labels in POLISH_GOV_FORM_LABELS["field_type_hints"].items():
        if normalized in labels:
            return ftype
    return "text"

def is_meta_instruction(normalized: str) -> bool:
    for instr in POLISH_GOV_FORM_LABELS["meta_instructions"]:
        if normalized == instr or instr in normalized:
            return True
    return False

def get_semantic_field_id(normalized: str) -> str:
    best_id = normalized
    best_score = 0
    
    for f_id, aliases in POLISH_GOV_FORM_LABELS["semantic_aliases"].items():
        for alias in aliases:
            if normalized == alias:
                return f_id
            
            # Substring match
            if alias in normalized:
                if 80 > best_score:
                    best_score = 80
                    best_id = f_id
                    
            # Token overlap Jaccard
            phrase_tokens = set(normalized.split())
            alias_tokens = set(alias.split())
            
            if phrase_tokens and alias_tokens:
                intersection = phrase_tokens.intersection(alias_tokens)
                union = phrase_tokens.union(alias_tokens)
                score = (len(intersection) / len(union)) * 100
                if score > best_score and score >= 70:
                    best_score = score
                    best_id = f_id
                    
    return best_id

def _rects_overlap(r1: dict, r2: dict) -> bool:
    return not (r1["x1"] <= r2["x0"] or r1["x0"] >= r2["x1"] or 
                r1["y1"] <= r2["y0"] or r1["y0"] >= r2["y1"])

def detect_field_candidates(words: list[dict], pdf_path: str = None, page_index: int = 0) -> list[dict]:
    from core.pdf_layout_parser import get_graphics, get_layout_lines, get_acroform_widgets

    candidates = []

    # Krok 1: Próba pobrania natywnych pól z formularza AcroForm
    if pdf_path:
        widgets = get_acroform_widgets(pdf_path, page_index)
        if widgets:
            for w in widgets:
                candidates.append({
                    "x0": w["x0"],
                    "y0": w["y0"],
                    "x1": w["x1"],
                    "y1": w["y1"],
                    "label": w["field_name"],
                    "field_type": w["field_type"],
                    "is_high_value": False
                })

    # Krok 2: Fallback (Heurystyczny Rule-based Detector)
    lines = build_text_lines(words)
    phrases = build_label_phrases(lines)
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
            
        field_id = get_semantic_field_id(normalized_phrase)
        
        # Jeżeli field_id jest taki sam jak fraza (brak w słowniku), 
        # i nie jest na liście np. address_parts, omijamy żeby nie łapać śmieci
        # Ale dla MVP dopuszczamy wszystko z semantic_aliases i type hints
        known = False
        if field_id != normalized_phrase:
            known = True
            
        # Szukamy też w hintach
        field_type = get_field_type_hint(normalized_phrase)
        if field_type != "text" or normalized_phrase in POLISH_GOV_FORM_LABELS["field_type_hints"]["text"]:
            known = True
            
        if not known:
            continue

        px0, py0, px1, py1 = phrase["x0"], phrase["y0"], phrase["x1"], phrase["y1"]
        label_height = py1 - py0
        label_width = px1 - px0

        is_high_value = normalized_phrase in POLISH_GOV_FORM_LABELS["high_value_masked_fields"] or \
                        any(normalized_phrase in aliases for aliases in POLISH_GOV_FORM_LABELS["semantic_aliases"].values() if any(a in POLISH_GOV_FORM_LABELS["high_value_masked_fields"] for a in aliases))

        if field_type == "checkbox":
            nearest = find_nearest_rect(phrase, graphics)
            
            if nearest:
                candidate_x0 = nearest["x0"] - 1
                candidate_y0 = nearest["y0"] - 1
                candidate_x1 = nearest["x1"] + 1
                candidate_y1 = nearest["y1"] + 1
            else:
                # Default heuristic for yes/no checkboxes
                if normalized_phrase in ["tak", "nie"]:
                    box_size = max(14, label_height * 0.9)
                    candidate_x0 = px0 - box_size - 6
                    candidate_y0 = py0 + (label_height - box_size) / 2
                    candidate_x1 = candidate_x0 + box_size
                    candidate_y1 = candidate_y0 + box_size
                else:
                    box_size = max(14, label_height * 0.9)
                    if len(normalized_phrase) > 10:
                        candidate_x0 = px0 + (label_width - box_size) / 2
                        candidate_y0 = py1 + 4
                    else:
                        candidate_x0 = px1 + 8
                        candidate_y0 = py0 + (label_height - box_size) / 2
                    candidate_x1 = candidate_x0 + box_size
                    candidate_y1 = candidate_y0 + box_size
        else:
            left, top, right, bottom = find_cell_bounds_from_lines(phrase, h_lines, v_lines)
            
            if left != -1 and top != -1 and right != 10000 and bottom != 10000:
                candidate_x0 = max(px1 + 4, left + 2)
                candidate_y0 = top + 2
                candidate_x1 = right - 2
                candidate_y1 = bottom - 2
                
                if candidate_x0 >= candidate_x1:
                    candidate_x0 = left + 2
            else:
                candidate_x0 = px1 + max(6, label_height * 0.4)
                candidate_y0 = py0 - label_height * 0.1
                candidate_x1 = candidate_x0 + max(120, label_width * 2.2)
                candidate_y1 = py1 + label_height * 0.1

        new_candidate = {
            "x0": candidate_x0,
            "y0": candidate_y0,
            "x1": candidate_x1,
            "y1": candidate_y1,
            "label": field_id,
            "field_type": field_type,
            "is_high_value": is_high_value
        }
        
        # Unikamy duplikowania z AcroForm widgets:
        is_duplicate = False
        for c in candidates:
            # Check overlap logic
            if _rects_overlap(new_candidate, c):
                is_duplicate = True
                break
                
        if not is_duplicate:
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
