#!/usr/bin/env python3
"""Generate a hypothetical society: people with relationships, jobs, and a life-graph.

Emits into the output directory:
  - society.json     canonical graph (people + companies + all edges)
  - narrative.txt    flowing prose describing the society (paste into an LLM)
  - questions.txt    numbered question bank
  - answers.txt      ground-truth answers, same numbering
  - qa.json          structured Q&A for programmatic grading

Example:
  python generate_society.py --size 500 --seed 42 --out-dir society/
"""

import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path


REFERENCE_DATE = date(2026, 4, 24)
REFERENCE_YEAR = REFERENCE_DATE.year
ADULT_AGE = 22
MAX_MARRIAGE_AGE = 70
RETIREMENT_AGE = 66
MARRIAGE_AGE_GAP = 15
PARENT_AGE_MIN = 22
PARENT_AGE_MAX = 45
MAX_CHILDREN = 5
MARRIAGE_PROB = 0.85
FOUNDER_YEAR_WINDOW = (1935, 1975)
MAX_GENERATIONS = 8


COMPANY_TEMPLATES = [
    ("healthcare",
     ["{saint}'s Hospital", "{city} General Hospital", "{brand} Medical Center", "{city} Clinic"],
     ["nurse", "doctor", "surgeon", "paramedic", "radiologist", "dentist", "psychiatrist"]),
    ("landscape",
     ["Verdant Gardens", "{brand} Landscaping", "{city} Greenworks"],
     ["gardener", "florist", "landscaper", "arborist"]),
    ("automotive",
     ["{brand} Motors", "{city} Auto Repair", "Swift Mechanics"],
     ["mechanic", "auto technician", "tow truck driver", "car salesperson"]),
    ("legal",
     ["{brand} Law Firm", "{city} Legal Associates", "Chambers & {brand}"],
     ["lawyer", "paralegal", "legal secretary", "judge"]),
    ("construction",
     ["{brand} Construction", "{city} Builders", "Ironhammer Construction"],
     ["carpenter", "electrician", "plumber", "welder", "architect", "roofer"]),
    ("food",
     ["{brand} Bakery", "Fresh Rise Bakery", "{city} Bread Co", "The {city} Kitchen"],
     ["baker", "chef", "pastry chef", "barista", "waiter"]),
    ("education",
     ["{city} Elementary", "{brand} Academy", "Maple Ridge School", "{city} University"],
     ["teacher", "principal", "librarian", "professor", "school counselor"]),
    ("aviation",
     ["SkyBridge Aviation", "{city} Airlines", "{brand} Air"],
     ["pilot", "flight attendant", "air traffic controller"]),
    ("tech",
     ["{brand} Software", "Cortex Systems", "{city} Digital"],
     ["software engineer", "data analyst", "product manager", "UX designer"]),
    ("safety",
     ["{city} Police Department", "{brand} Security", "{city} Fire Station"],
     ["police officer", "firefighter", "security guard", "detective"]),
    ("retail",
     ["{brand} Market", "{city} Department Store"],
     ["shop clerk", "store manager", "cashier"]),
    ("finance",
     ["{brand} Bank", "{city} Financial"],
     ["accountant", "financial advisor", "bank teller", "auditor"]),
]

CITIES = [
    "Ashford", "Brookhaven", "Celestia", "Dunmore", "Elmshire", "Falworth",
    "Greystone", "Havenwood", "Ironhold", "Jasperdale", "Kenmare", "Lorien",
    "Maplewood", "Northridge", "Oakvale", "Pinehurst", "Quinton", "Ravenscroft",
    "Silvermoor", "Thornbury", "Valemont", "Whitehaven",
]
BRANDS = [
    "Vanguard", "Meridian", "Sterling", "Pinnacle", "Summit", "Horizon", "Apex",
    "Cascade", "Beacon", "Catalyst", "Phoenix", "Atlas", "Orion", "Zenith",
    "Sovereign", "Titan",
]
SAINTS = [
    "Mark", "Luke", "John", "Peter", "Paul", "Mary", "Agnes", "Clare", "Joseph",
    "Anne", "Thomas", "Francis",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_names(path: Path) -> list:
    names = [n.strip() for n in path.read_text(encoding="utf-8").splitlines() if n.strip()]
    return names


def random_birthday(rng: random.Random, year: int) -> date:
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    return start + timedelta(days=rng.randint(0, (end - start).days))


def age_of(birthday: date, ref: date = REFERENCE_DATE) -> int:
    years = ref.year - birthday.year
    if (ref.month, ref.day) < (birthday.month, birthday.day):
        years -= 1
    return years


def age_at_birth(parent_bday: date, child_bday: date) -> int:
    years = child_bday.year - parent_bday.year
    if (child_bday.month, child_bday.day) < (parent_bday.month, parent_bday.day):
        years -= 1
    return years


def pick_name(rng: random.Random, names: list, used: set) -> str | None:
    for _ in range(200):
        n = rng.choice(names)
        if n not in used:
            used.add(n)
            return n
    for n in names:
        if n not in used:
            used.add(n)
            return n
    return None


def make_person(name: str, gender: str, birthday: date, pid: str) -> dict:
    return {
        "id": pid,
        "name": name,
        "gender": gender,
        "birthday": birthday.isoformat(),
        "job": None,
        "employer_id": None,
        "spouse_id": None,
        "parent_ids": [],
        "child_ids": [],
    }


# ---------------------------------------------------------------------------
# Population builder (generational)
# ---------------------------------------------------------------------------

def is_blood_related(a: dict, b: dict, people_by_id: dict) -> bool:
    """True if a and b share blood (siblings, parent/child, uncle/aunt, first cousins)."""
    if a["id"] == b["id"]:
        return True
    if a["id"] in b["parent_ids"] or b["id"] in a["parent_ids"]:
        return True
    if set(a["parent_ids"]) & set(b["parent_ids"]):
        return True
    def grandparents(p: dict) -> set:
        gps = set()
        for pid in p["parent_ids"]:
            par = people_by_id.get(pid)
            if par:
                gps.update(par["parent_ids"])
        return gps
    ga = grandparents(a)
    gb = grandparents(b)
    if ga & gb:
        return True
    if a["id"] in gb or b["id"] in ga:
        return True
    return False


def pair_up_couples(rng: random.Random, pool: list, people_by_id: dict,
                     same_sex_rate: float) -> list:
    candidates = [p for p in pool if p["spouse_id"] is None]
    rng.shuffle(candidates)
    couples = []
    used = set()
    for a in candidates:
        if a["id"] in used:
            continue
        if rng.random() > MARRIAGE_PROB:
            continue
        want_same_sex = rng.random() < same_sex_rate
        a_bday = date.fromisoformat(a["birthday"])
        partner = None
        for b in candidates:
            if b["id"] == a["id"] or b["id"] in used:
                continue
            if b["spouse_id"] is not None:
                continue
            if want_same_sex and a["gender"] != b["gender"]:
                continue
            if not want_same_sex and a["gender"] == b["gender"]:
                continue
            b_bday = date.fromisoformat(b["birthday"])
            if abs((a_bday - b_bday).days) > MARRIAGE_AGE_GAP * 365:
                continue
            if is_blood_related(a, b, people_by_id):
                continue
            partner = b
            break
        if partner is None:
            continue
        a["spouse_id"] = partner["id"]
        partner["spouse_id"] = a["id"]
        used.add(a["id"])
        used.add(partner["id"])
        couples.append((a, partner))
    return couples


def spawn_children(rng: random.Random, couple: tuple, people_by_id: dict,
                    names: list, names_used: set, next_id, childless_rate: float,
                    size_limit: int, all_people: list) -> list:
    a, b = couple
    if rng.random() < childless_rate:
        return []
    mother = a if a["gender"] == "f" else (b if b["gender"] == "f" else a)
    father = b if mother is a else a
    a_bday = date.fromisoformat(a["birthday"])
    b_bday = date.fromisoformat(b["birthday"])
    a_year, b_year = a_bday.year, b_bday.year
    min_year = max(a_year, b_year) + PARENT_AGE_MIN
    max_year = min(min(a_year, b_year) + PARENT_AGE_MAX, REFERENCE_YEAR - 1)
    if min_year > max_year:
        return []
    n_kids = rng.randint(1, MAX_CHILDREN)
    children = []
    for _ in range(n_kids):
        if len(all_people) >= size_limit:
            break
        child_year = rng.randint(min_year, max_year)
        child_bday = random_birthday(rng, child_year)
        name = pick_name(rng, names, names_used)
        if name is None:
            break
        gender = rng.choice(["m", "f"])
        pid = next_id()
        child = make_person(name, gender, child_bday, pid)
        child["parent_ids"] = [mother["id"], father["id"]]
        mother["child_ids"].append(pid)
        father["child_ids"].append(pid)
        people_by_id[pid] = child
        all_people.append(child)
        children.append(child)
    return children


def build_population(rng: random.Random, size: int, names: list,
                      same_sex_rate: float, childless_rate: float) -> tuple:
    people: list = []
    people_by_id: dict = {}
    names_used: set = set()
    counter = [0]
    def next_id():
        counter[0] += 1
        return f"p{counter[0]:06d}"

    n_founders = max(4, size // 4)
    if n_founders % 2 != 0:
        n_founders += 1
    for _ in range(n_founders):
        if len(people) >= size:
            break
        name = pick_name(rng, names, names_used)
        gender = rng.choice(["m", "f"])
        by = rng.randint(*FOUNDER_YEAR_WINDOW)
        p = make_person(name, gender, random_birthday(rng, by), next_id())
        people.append(p)
        people_by_id[p["id"]] = p

    current_gen = list(people)
    for gen_idx in range(MAX_GENERATIONS):
        if len(people) >= size:
            break
        eligible = []
        for p in current_gen:
            bday = date.fromisoformat(p["birthday"])
            age = age_of(bday)
            if p["spouse_id"] is None and ADULT_AGE <= age <= MAX_MARRIAGE_AGE:
                eligible.append(p)
        couples = pair_up_couples(rng, eligible, people_by_id, same_sex_rate)
        if not couples:
            n_new = max(4, (size - len(people)) // 3)
            if n_new % 2 != 0:
                n_new += 1
            fresh = []
            for _ in range(n_new):
                if len(people) >= size:
                    break
                name = pick_name(rng, names, names_used)
                if name is None:
                    break
                gender = rng.choice(["m", "f"])
                lo = FOUNDER_YEAR_WINDOW[0] + gen_idx * 20
                hi = min(FOUNDER_YEAR_WINDOW[1] + gen_idx * 20, REFERENCE_YEAR - ADULT_AGE - 1)
                if lo > hi:
                    lo = hi - 10
                by = rng.randint(lo, hi)
                p = make_person(name, gender, random_birthday(rng, by), next_id())
                people.append(p)
                people_by_id[p["id"]] = p
                fresh.append(p)
            current_gen = fresh
            continue

        next_gen = []
        for couple in couples:
            if len(people) >= size:
                break
            kids = spawn_children(rng, couple, people_by_id, names, names_used,
                                   next_id, childless_rate, size, people)
            next_gen.extend(kids)
        current_gen = next_gen if next_gen else list(people_by_id.values())

    while len(people) < size:
        name = pick_name(rng, names, names_used)
        if name is None:
            break
        gender = rng.choice(["m", "f"])
        by = rng.randint(FOUNDER_YEAR_WINDOW[0], REFERENCE_YEAR - ADULT_AGE - 1)
        p = make_person(name, gender, random_birthday(rng, by), next_id())
        people.append(p)
        people_by_id[p["id"]] = p

    return people, people_by_id


# ---------------------------------------------------------------------------
# Companies and jobs
# ---------------------------------------------------------------------------

def build_companies(rng: random.Random, size: int) -> list:
    n_companies = max(3, size // 10)
    companies: list = []
    used_names: set = set()
    attempts = 0
    while len(companies) < n_companies and attempts < n_companies * 50:
        attempts += 1
        industry, templates, jobs = rng.choice(COMPANY_TEMPLATES)
        tpl = rng.choice(templates)
        name = tpl.format(
            city=rng.choice(CITIES),
            brand=rng.choice(BRANDS),
            saint=rng.choice(SAINTS),
        )
        if name in used_names:
            continue
        used_names.add(name)
        companies.append({
            "id": f"c{len(companies) + 1:04d}",
            "name": name,
            "industry": industry,
            "jobs": list(jobs),
        })
    return companies


def assign_jobs_and_employers(rng: random.Random, people: list, companies: list) -> None:
    for p in people:
        age = age_of(date.fromisoformat(p["birthday"]))
        if age < ADULT_AGE:
            continue
        if age >= RETIREMENT_AGE and rng.random() < 0.7:
            continue
        if rng.random() < 0.05:
            continue
        company = rng.choice(companies)
        p["employer_id"] = company["id"]
        p["job"] = rng.choice(company["jobs"])


# ---------------------------------------------------------------------------
# Narrative rendering
# ---------------------------------------------------------------------------

def _article(word: str) -> str:
    return "an" if word and word[0].lower() in "aeiou" else "a"


def _attach_attrs(rng: random.Random, person: dict, companies_by_id: dict,
                   mentioned_birthday: set, mentioned_job: set,
                   birthday_prob: float, job_prob: float) -> str:
    bits = []
    if person["id"] not in mentioned_birthday and rng.random() < birthday_prob:
        bits.append(f"born on {person['birthday']}")
        mentioned_birthday.add(person["id"])
    if (person["id"] not in mentioned_job
            and person["job"]
            and rng.random() < job_prob):
        comp = companies_by_id[person["employer_id"]]
        bits.append(f"{_article(person['job'])} {person['job']} at {comp['name']}")
        mentioned_job.add(person["id"])
    return ", ".join(bits)


def _pick_outgoing_edge(rng: random.Random, person: dict, people_by_id: dict,
                         mentioned_marriage: set, mentioned_parentage: set) -> tuple | None:
    candidates = []
    if person["spouse_id"]:
        key = frozenset({person["id"], person["spouse_id"]})
        if key not in mentioned_marriage:
            candidates.append(("married", people_by_id[person["spouse_id"]],
                                ("marriage", key)))
    for cid in person["child_ids"]:
        pkey = (person["id"], cid)
        if pkey not in mentioned_parentage:
            verb = "fathered" if person["gender"] == "m" else "gave birth to"
            candidates.append((verb, people_by_id[cid], ("parentage", pkey)))
    if not candidates:
        return None
    return rng.choice(candidates)


def _walk_chain(rng: random.Random, start: dict, people_by_id: dict,
                 companies_by_id: dict, mentioned_marriage: set,
                 mentioned_parentage: set, mentioned_job: set,
                 mentioned_birthday: set) -> str | None:
    depth = rng.randint(2, 5)
    opener_attrs = _attach_attrs(rng, start, companies_by_id, mentioned_birthday,
                                   mentioned_job, birthday_prob=0.45, job_prob=0.55)
    subject = f"{start['name']}, {opener_attrs}" if opener_attrs else start["name"]
    hops: list = []
    current = start
    for _ in range(depth):
        edge = _pick_outgoing_edge(rng, current, people_by_id,
                                     mentioned_marriage, mentioned_parentage)
        if edge is None:
            break
        verb, nxt, fact = edge
        if fact[0] == "marriage":
            mentioned_marriage.add(fact[1])
        else:
            mentioned_parentage.add(fact[1])
        extras = _attach_attrs(rng, nxt, companies_by_id, mentioned_birthday,
                                 mentioned_job, birthday_prob=0.30, job_prob=0.55)
        obj_phrase = f"{nxt['name']}, {extras}" if extras else nxt["name"]
        hops.append((verb, obj_phrase))
        current = nxt
    if not hops:
        return None

    if opener_attrs:
        clauses = [subject] + [f"who {v} {o}" for v, o in hops]
        return ", ".join(clauses) + "."
    head = f"{subject} {hops[0][0]} {hops[0][1]}"
    tail = [f"who {v} {o}" for v, o in hops[1:]]
    if tail:
        return head + ", " + ", ".join(tail) + "."
    return head + "."


def render_narrative(rng: random.Random, people: list, companies: list) -> str:
    companies_by_id = {c["id"]: c for c in companies}
    people_by_id = {p["id"]: p for p in people}
    mentioned_marriage: set = set()
    mentioned_parentage: set = set()
    mentioned_job: set = set()
    mentioned_birthday: set = set()

    sentences: list = []

    # Pass A: chained walks, one rooted at each person
    roots = list(people)
    rng.shuffle(roots)
    for root in roots:
        s = _walk_chain(rng, root, people_by_id, companies_by_id,
                         mentioned_marriage, mentioned_parentage,
                         mentioned_job, mentioned_birthday)
        if s:
            sentences.append(s)

    # Pass B: flat-fact fallback for any uncovered data
    for p in people:
        if p["id"] not in mentioned_birthday:
            sentences.append(f"{p['name']} was born on {p['birthday']}.")
            mentioned_birthday.add(p["id"])
    for p in people:
        if p["id"] not in mentioned_job and p["job"]:
            comp = companies_by_id[p["employer_id"]]
            sentences.append(
                f"{p['name']} works as {_article(p['job'])} {p['job']} at {comp['name']}."
            )
            mentioned_job.add(p["id"])
    for p in people:
        if p["spouse_id"]:
            key = frozenset({p["id"], p["spouse_id"]})
            if key not in mentioned_marriage:
                sp = people_by_id[p["spouse_id"]]
                sentences.append(f"{p['name']} is married to {sp['name']}.")
                mentioned_marriage.add(key)
        for cid in p["child_ids"]:
            k = (p["id"], cid)
            if k not in mentioned_parentage:
                ch = people_by_id[cid]
                verb = "fathered" if p["gender"] == "m" else "gave birth to"
                sentences.append(f"{p['name']} {verb} {ch['name']}.")
                mentioned_parentage.add(k)

    rng.shuffle(sentences)
    return "\n".join(sentences)


# ---------------------------------------------------------------------------
# Q&A generation
# ---------------------------------------------------------------------------

def _relation_resolvers(people: list, people_by_id: dict) -> list:
    employer_index: dict = {}
    for p in people:
        if p["employer_id"]:
            employer_index.setdefault(p["employer_id"], []).append(p)

    def spouse(p):
        return people_by_id[p["spouse_id"]] if p["spouse_id"] else None

    def mother(p):
        for pid in p["parent_ids"]:
            par = people_by_id[pid]
            if par["gender"] == "f":
                return par
        return None

    def father(p):
        for pid in p["parent_ids"]:
            par = people_by_id[pid]
            if par["gender"] == "m":
                return par
        return None

    def eldest_child(p):
        if not p["child_ids"]:
            return None
        kids = sorted((people_by_id[c] for c in p["child_ids"]),
                       key=lambda x: x["birthday"])
        return kids[0]

    def eldest_sibling(p):
        sibs: set = set()
        for pid in p["parent_ids"]:
            par = people_by_id[pid]
            for cid in par["child_ids"]:
                if cid != p["id"]:
                    sibs.add(cid)
        if not sibs:
            return None
        ordered = sorted((people_by_id[s] for s in sibs),
                          key=lambda x: x["birthday"])
        return ordered[0]

    def oldest_colleague(p):
        if not p["employer_id"]:
            return None
        coworkers = [c for c in employer_index.get(p["employer_id"], []) if c["id"] != p["id"]]
        if not coworkers:
            return None
        coworkers.sort(key=lambda x: x["birthday"])
        return coworkers[0]

    return [
        ("spouse", spouse),
        ("mother", mother),
        ("father", father),
        ("eldest child", eldest_child),
        ("eldest sibling", eldest_sibling),
        ("oldest colleague", oldest_colleague),
    ]


def build_qa(rng: random.Random, people: list, companies: list,
              max_hops: int, per_hop: int) -> list:
    people_by_id = {p["id"]: p for p in people}
    companies_by_id = {c["id"]: c for c in companies}
    relations = _relation_resolvers(people, people_by_id)

    attribute_choices = [
        ("job", lambda p: p["job"]),
        ("birthday", lambda p: p["birthday"]),
        ("employer", lambda p: companies_by_id[p["employer_id"]]["name"] if p["employer_id"] else None),
        ("name", lambda p: p["name"]),
    ]

    def phrase_question(target_name: str, chain: list, attr: str) -> str:
        if chain:
            possessive = f"{target_name}'s " + "'s ".join(chain)
        else:
            possessive = target_name
        if attr == "job":
            return f"What is the job of {possessive}?"
        if attr == "birthday":
            return f"What is the birthday of {possessive}?"
        if attr == "employer":
            return f"Where does {possessive} work?"
        if attr == "name":
            return f"What is the full name of {possessive}?"
        raise ValueError(attr)

    qa: list = []
    qid = 1
    for hop in range(1, max_hops + 1):
        made = 0
        attempts = 0
        seen_keys: set = set()
        while made < per_hop and attempts < per_hop * 200:
            attempts += 1
            target = rng.choice(people)
            chain_names: list = []
            current = target
            failed = False
            for _ in range(hop - 1):
                rname, rfn = rng.choice(relations)
                nxt = rfn(current)
                if nxt is None:
                    failed = True
                    break
                chain_names.append(rname)
                current = nxt
            if failed:
                continue
            aname, afn = rng.choice(attribute_choices)
            if hop == 1 and aname == "name":
                continue
            answer = afn(current)
            if answer is None:
                continue
            key = (target["id"], tuple(chain_names), aname)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            q = phrase_question(target["name"], chain_names, aname)
            qa.append({
                "id": qid,
                "hop_count": hop,
                "question": q,
                "answer": answer,
                "target": target["name"],
                "relation_chain": chain_names,
                "attribute": aname,
            })
            qid += 1
            made += 1
    return qa


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_outputs(out_dir: Path, people: list, companies: list,
                   narrative: str, qa: list) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    graph = {
        "reference_date": REFERENCE_DATE.isoformat(),
        "people": people,
        "companies": companies,
    }
    (out_dir / "society.json").write_text(
        json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out_dir / "narrative.txt").write_text(narrative + "\n", encoding="utf-8")

    q_lines = [f"Q{i['id']} [hops={i['hop_count']}]: {i['question']}" for i in qa]
    a_lines = [f"A{i['id']}: {i['answer']}" for i in qa]
    (out_dir / "questions.txt").write_text("\n".join(q_lines) + "\n", encoding="utf-8")
    (out_dir / "answers.txt").write_text("\n".join(a_lines) + "\n", encoding="utf-8")
    (out_dir / "qa.json").write_text(
        json.dumps(qa, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(people: list, people_by_id: dict, companies: list) -> None:
    company_ids = {c["id"] for c in companies}
    for p in people:
        assert len(p["parent_ids"]) in (0, 2), \
            f"{p['id']} has {len(p['parent_ids'])} parents"
        if p["spouse_id"]:
            sp = people_by_id[p["spouse_id"]]
            assert sp["spouse_id"] == p["id"], \
                f"asymmetric marriage {p['id']} <-> {sp['id']}"
            assert sp["id"] not in p["parent_ids"], "married to parent"
            assert sp["id"] not in p["child_ids"], "married to child"
            assert not (set(p["parent_ids"]) & set(sp["parent_ids"])), \
                f"sibling marriage: {p['id']} <-> {sp['id']}"
        for pid in p["parent_ids"]:
            parent = people_by_id[pid]
            assert p["id"] in parent["child_ids"], \
                f"parent {pid} missing child {p['id']}"
            gap = age_at_birth(date.fromisoformat(parent["birthday"]),
                                 date.fromisoformat(p["birthday"]))
            assert PARENT_AGE_MIN - 1 <= gap <= PARENT_AGE_MAX + 1, \
                f"bad parent age gap {pid}->{p['id']}: {gap}"
        for cid in p["child_ids"]:
            child = people_by_id[cid]
            assert p["id"] in child["parent_ids"], \
                f"child {cid} missing parent {p['id']}"
        if p["employer_id"]:
            assert p["employer_id"] in company_ids, \
                f"unknown employer {p['employer_id']}"
            assert p["job"], f"{p['id']} has employer but no job"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--size", type=int, default=500, help="target person count")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--names-file", type=Path,
                     default=Path(__file__).parent / "names.txt")
    ap.add_argument("--out-dir", type=Path,
                     default=Path(__file__).parent / "society")
    ap.add_argument("--max-hops", type=int, default=5)
    ap.add_argument("--questions-per-hop", type=int, default=10)
    ap.add_argument("--same-sex-rate", type=float, default=0.05)
    ap.add_argument("--childless-rate", type=float, default=0.20)
    args = ap.parse_args()

    assert args.size >= 10, "size must be >= 10"
    assert 1 <= args.max_hops <= 10, "max-hops in [1, 10]"
    assert args.questions_per_hop >= 1

    rng = random.Random(args.seed)
    names = load_names(args.names_file)
    assert len(names) >= args.size, \
        f"names file has {len(names)} names, need at least {args.size}"

    people, people_by_id = build_population(
        rng, args.size, names, args.same_sex_rate, args.childless_rate
    )
    companies = build_companies(rng, args.size)
    assign_jobs_and_employers(rng, people, companies)

    validate(people, people_by_id, companies)

    narrative = render_narrative(rng, people, companies)
    qa = build_qa(rng, people, companies, args.max_hops, args.questions_per_hop)

    write_outputs(args.out_dir, people, companies, narrative, qa)

    n_married = sum(1 for p in people if p["spouse_id"]) // 2
    n_parent_edges = sum(len(p["child_ids"]) for p in people)
    n_sentences = narrative.count("\n") + 1
    print(f"Wrote {len(people)} people, {len(companies)} companies, "
          f"{n_married} marriages, {n_parent_edges} parent-child edges.")
    print(f"Narrative: {len(narrative):,} chars / {n_sentences} sentences.")
    print(f"Questions: {len(qa)} "
          f"({args.questions_per_hop} per hop, hops 1-{args.max_hops}).")
    print(f"Output: {args.out_dir}")


if __name__ == "__main__":
    main()
