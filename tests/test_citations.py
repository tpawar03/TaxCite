"""Citation and treatment extraction (tasks/todo.md C3), on text shaped like the real corpus.

Every case here is one C0 or C1 found in the 307 opinions or their appeals. CourtListener is
never called and no database is needed.
"""

from taxcite.ingest import citations as c


def test_line_break_inside_a_memo_cite_is_rejoined():
    # 23 of 2,456 memo cites in the corpus are split like this, and eyecite misses them unjoined
    text = "See Taras v. Commissioner, T.C. Memo. 1997-\n553, 74 T.C.M. (CCH) 1388."
    assert c.cites(text, "T.C. Memo. 2021-139") == {"T.C. Memo. 1997-553"}


def test_scanned_opinion_spacing_is_repaired():
    # ~200 cites in older scanned opinions have spaces before periods and commas; eyecite reads none of them
    text = "See Higbee v . Commissioner , 116 T .C . 438, 440 (2001) ; Chandler v . Commissioner , T .C . Memo 2010-92 ."
    assert c.cites(text, "T.C. Memo. 2010-198") == {"116 T.C. 438", "T.C. Memo. 2010-92"}


def test_ocr_digit_splits():
    # the opinion's own masthead, split: not a cite of T.C. Memo. 2010-1
    assert c.cites("T.C. Memo. 2010-1 7 UNITED STATES TAX COURT", "T.C. Memo. 2010-17") == set()
    # a page split before the year
    assert c.cites("Domulewicz v. Commissioner, 129 T.C. 1 1 (2007).", "T.C. Memo. 2010-177") == {"129 T.C. 11"}


def test_reported_tc_opinions_resolve_to_their_slip_number():
    text = "See Grey v. Commissioner, 119 T.C. 121, 126 (2002); Cohan v. Commissioner, 39 F.2d 540 (2d Cir. 1930)."
    assert c.cites(text, "T.C. Memo. 2013-85") == {"119 T.C. No. 5"}


def test_an_opinion_does_not_cite_itself():
    text = "Accord Rogerson v. Commissioner, T.C. Memo. 2022-49, at *16; Moss v. Commissioner, 135 T.C. 365 (2010)."
    assert c.cites(text, "T.C. Memo. 2022-49") == {"135 T.C. No. 18"}


def test_history_after_the_cite():
    text = "Menard, Inc. v. Commissioner, T.C. Memo. 2004-207, rev'd, 560 F.3d 620 (7th Cir. 2009)."
    assert c.history(text, "T.C. Memo. 2026-50") == {("T.C. Memo. 2004-207", "reversed", "560 F.3d 620 (ca7 2009)")}


def test_history_before_the_cite_split_decision():
    text = ("Chai v. Commissioner, 851 F.3d 190, 221 (2d Cir. 2017), aff'g in part, rev'g in part "
            "T.C. Memo. 2015-42, and Kroner v. Commissioner, 48 F.4th 1272 (11th Cir. 2022).")
    # a split decision reads as the more serious outcome; the label drops the case name and pin cite
    assert c.history(text, "T.C. Memo. 2024-1") == {("T.C. Memo. 2015-42", "reversed in part", "851 F.3d 190 (ca2 2017)")}


def test_only_an_appellate_court_can_affirm():
    # C1: a Board of Tax Appeals cite after "aff'd" was read as an appeal
    text = "Smith v. Commissioner, T.C. Memo. 1979-101, aff'd, Estate of Brawner v. Commissioner, 36 B.T.A. 884 (1937)."
    assert c.history(text, "T.C. Memo. 2013-1") == set()


def test_an_appeal_cannot_predate_the_opinion():
    # C1: a 2003 Supreme Court case "affirmed" a 2011 memo
    text = "Wells v. Commissioner, T.C. Memo. 2011-48, aff'd, Clackamas v. Wells, 538 U.S. 440 (2003)."
    assert c.history(text, "T.C. Memo. 2012-184") == set()


def test_overruled_with_an_appellate_cite_in_between():
    text = ("Wuebker v. Commissioner, 110 T.C. 431 (1998), rev'd, 205 F.3d 897 (6th Cir. 2000), is overruled. "
            "In so doing, we overrule our holding in Wuebker v. Commissioner, 110 T.C. 431.")
    found = c.history(text, "140 T.C. No. 16")
    assert ("110 T.C. 431", "overruled", "140 T.C. No. 16") in found
    assert ("110 T.C. 431", "reversed", "205 F.3d 897 (ca6 2000)") in found


def test_split_decisions_after_the_cite():
    # the whole phrase decides, not the first word; vacatur counts as more serious than affirmance
    text = "Greenspon v. Commissioner, 23 T.C. 138, 151 (1954), aff'd in part, rev'd in part, 229 F.2d 947 (8th Cir. 1956)."
    assert c.history(text, "T.C. Memo. 2020-1") == {("23 T.C. 138", "reversed in part", "229 F.2d 947 (ca8 1956)")}
    text = "Bank One Corp. v. Commissioner, 120 T.C. 174, 306 (2003), aff'd in part, vacated in part, 458 F.3d 564 (7th Cir. 2006)."
    assert {k for _, k, _ in c.history(text, "T.C. Memo. 2020-1")} == {"vacated in part"}


def test_history_across_parallel_cites_and_parentheticals():
    text = ("Smith v. Commissioner, T.C. Memo. 2007-368, 2007 WL 4410771, at *19, aff'd, 364 F. App'x 317 (9th Cir. 2009). "
            "Winn-Dixie Stores, Inc. v. Commissioner, 113 T.C. 254 (1999) (corporate-owned life insurance), aff'd per curiam, "
            "254 F.3d 1313 (11th Cir. 2001).")
    found = {(k, kind) for k, kind, _ in c.history(text, "T.C. Memo. 2023-133")}
    assert found == {("T.C. Memo. 2007-368", "affirmed"), ("113 T.C. 254", "affirmed")}


def test_history_that_belongs_to_another_case():
    # prose after a sentence break (#33)
    text = "Brannon's of Shawnee, Inc. v. Commissioner, 69 T.C. 999 (1978). We have also vacated a final decision. Michaels v. Commissioner, 144 F.3d 495 (7th Cir. 1998)."
    assert c.history(text, "T.C. Memo. 2011-1") == set()
    # the outer case was affirmed, not the one cited inside its parenthetical (#88)
    text = "Smith v. Commissioner, T.C. Memo. 2024-111, at *26 (citing Tokarski v. Commissioner, 87 T.C. 74, 77 (1986)), aff'd, 2026 WL 822261 (11th Cir. Mar. 25, 2026)."
    assert all(k != "87 T.C. 74" for k, _, _ in c.history(text, "T.C. Memo. 2026-1"))
    # a cite that isn't next to the history words isn't the appeal (#56)
    text = "Skidmore v. Swift & Co., 323 U.S. 134, 140 (1944))). 72, 73–74 (9th Cir. 1996), aff'g in part, rev'g in part T.C. Memo. 1993-558."
    assert c.history(text, "T.C. Memo. 2025-1") == set()
    # a blank appeal cite must not borrow a later, unrelated one (Cave)
    text = ("Donald G. Cave A Prof'l Law Corp. v. Commissioner, T.C. Memo. 2011-48, aff'd, 1. Degree of Control The degree "
            "of control is the most important consideration. See Clackamas Gastroenterology Assocs. v. Wells, 538 U.S. 440, 448.")
    assert c.history(text, "T.C. Memo. 2012-184") == set()
    text = "Sands v. Commissioner, T.C. Memo. 1997-146, aff'd sub nom. Murphy v. Commissioner, 164 F.3d 618 (2d Cir. 1998)."
    assert {k for k, _, _ in c.history(text, "T.C. Memo. 2026-51")} == {"T.C. Memo. 1997-146"}
    # "slip op. at 9" is not a sentence break, and a year comes from the cite's own parenthetical (Visin, Lavery)
    text = "Visin v. Commissioner, T.C. Memo. 2003-246, slip op. at 9, aff'd, 122 F. App'x 363 (9th Cir. 2005)."
    assert {k for k, _, _ in c.history(text, "T.C. Memo. 2023-87")} == {"T.C. Memo. 2003-246"}
    text = "Lavery v. Commissioner, 158 F.2d 859, 860 (7th Cir. 1946), affg. 5 T.C. 1283 (1945)), affd. 987 F.2d 770 (5th Cir. 1993)"
    assert ("5 T.C. 1283", "affirmed", "158 F.2d 859 (ca7 1946)") in c.history(text, "T.C. Memo. 2005-192")
    # a short form eyecite may misread as a full cite ("72 T.C. at 669") must not sit between a case and its appeal;
    # whether it does depends on the hash seed, so this is the test that keeps the load repeatable (Kahla)
    text = ("Kahla v. Commissioner, T.C. Memo. 2000-127 (citing Engdahl v. Commissioner, 72 T.C. at 669, and section "
            "1.183-2(b)(6), Income Tax Regs.), affd. without published opinion 273 F.3d 1096 (5th Cir. 2001).")
    assert {k for k, _, _ in c.history(text, "T.C. Memo. 2009-41")} == {"T.C. Memo. 2000-127"}
    assert all(not (x.groups.get("reporter") or "").endswith(" at") for x in c.full_cites(c.normalize(text)))
    # but two balanced parentheticals are fine
    text = "Humana Inc. v. Commissioner, 62 F.3d 835 (6th Cir. 1995) (captive insurance), rev'g and remanding T.C. Memo. 1993-585."
    assert {k for k, _, _ in c.history(text, "165 T.C. No. 10")} == {"T.C. Memo. 1993-585"}


def test_ruling_reads_the_last_disposition():
    assert c.ruling("…we reverse and remand to the Tax Court with instructions to enter judgment. 8 A footnote.") == "reversed"
    assert c.ruling("…the Tax Court committed clear error, and its decision is therefore R EVERSED. 3-10-09") == "reversed"
    assert c.ruling("For the foregoing reasons, the decision of the Tax Court is affirmed.") == "affirmed"


def test_ruling_edge_cases_from_c1():
    assert c.ruling("…gross income. AFFIRMED IN PART; REVERSED IN PART. 1 Oregon law requires…") == "reversed in part"
    # Visco: the Tax Court is the subject, so this is history, not the appellate ruling
    assert c.ruling("1. The Tax Court reversed the Commissioner's assessment of an addition to tax.") is None
    # Gregory: ends in a dissent with no disposition word
    assert c.ruling("Like the majority, I would deny the petition.") is None


def test_party_names_for_the_appellate_search():
    assert c.party("Donald B. & Arvilla Meinhardt, Petitioner") == '"Meinhardt"'
    assert c.party("Kenward F. Kolar, Jr., Petitioner") == '"Kolar"'
    assert c.party("Mission Organic Center, Inc., Petitioner") == '"Mission Organic"'
    assert c.party("Joseph M. Grey Public Accountant, P.C., Petitioner") == '"Grey" OR "Joseph M"'
    assert c.party("Willard Michael Christine & Patricia Ethel Borgia, Petitioners") == '"Borgia" OR "Christine"'
    # a part with one non-initial word is a first name: one family, not "Michael" (C1's three unrelated Michaels)
    assert c.party("C. Michael & Gwendolyn E. Willock, Petitioner") == '"Willock"'
    assert c.party("Michael P. Schwab & Kathryn J. Kleinman, Petitioners") == '"Kleinman" OR "Schwab"'


def test_a_same_name_case_is_not_an_appeal():
    op = {"caseCaption": "C. Michael & Gwendolyn E. Willock, Petitioner", "filingDate": "2010-04-12T00:00:00Z"}
    kelly = {"caseName": "Michael Kelly v. Cir", "dateFiled": "2025-06-05"}
    assert not c.is_appeal(op, kelly, "…petition for review of a decision of the Tax Court…")
    menard = {"caseName": "Menard, Inc. v. Commissioner", "dateFiled": "2009-03-10"}
    op = {"caseCaption": "Menard, Inc., Petitioner", "filingDate": "2004-09-14T00:00:00Z"}
    assert c.is_appeal(op, menard, "…the Tax Court committed clear error…")
    # the appeal carries the first spouse's name (C3: Schwab was missed when only Kleinman was checked)
    op = {"caseCaption": "Michael P. Schwab & Kathryn J. Kleinman, Petitioners", "filingDate": "2011-02-07T00:00:00Z"}
    assert c.is_appeal(op, {"caseName": "Schwab v. Commissioner", "dateFiled": "2013-04-24"}, "Michael Schwab… the Tax Court…")

# --- C4: treatment flags ---------------------------------------------------------------------------

from datetime import datetime, timedelta, timezone  # noqa: E402

NOW = datetime(2026, 9, 27, tzinfo=timezone.utc)
DAY = timedelta(days=1)


def test_a_reversal_is_flagged_with_its_source_and_date():
    f = c.flag([("courtlistener", "reversed", "769 F.3d 616 (ca8 2014)", NOW - DAY)], NOW)
    assert (f["status"], f["by"], f["sources"], f["checked_at"], f["stale"]) == (
        "reversed", "769 F.3d 616 (ca8 2014)", ["CourtListener"], "2026-09-26", False)


def test_sources_that_disagree_give_unknown():
    rows = [("courtlistener", "affirmed", "1 F.3d 1 (ca9 2000)", NOW), ("corpus", "reversed", "1 F.3d 1 (ca9 2000)", NOW)]
    assert c.flag(rows, NOW)["status"] == "unknown"


def test_the_most_serious_outcome_and_an_overruling_win():
    rows = [("corpus", "reversed", "205 F.3d 897 (ca6 2000)", NOW), ("corpus", "overruled", "140 T.C. No. 16", NOW)]
    assert (c.flag(rows, NOW)["status"], c.flag(rows, NOW)["by"]) == ("overruled", "140 T.C. No. 16")
    rows = [("corpus", "reversed in part", "a", NOW), ("corpus", "vacated", "b", NOW)]
    assert c.flag(rows, NOW)["status"] == "vacated"


def test_nothing_found_is_never_good_law():
    f = c.flag([("courtlistener", "none", "", NOW - DAY)], NOW)
    assert f["status"] == "none" and "No negative treatment found in CourtListener as of 2026-09-26" in f["note"]
    assert "good law" not in f["note"].lower()
    assert c.flag([], NOW)["status"] == "unknown"  # never checked is not the same as clean


def test_an_old_check_is_stale():
    assert c.flag([("courtlistener", "none", "", NOW - 8 * DAY)], NOW)["stale"]


def test_a_failed_lookup_fails_open_and_rolls_back():
    class Broken:
        rolled_back = False
        def execute(self, *a):
            raise RuntimeError("relation \"treatments\" does not exist")
        def rollback(self):
            self.rolled_back = True
    conn = Broken()
    out = c.flags(conn, ["140 T.C. No. 16", "T.C. Memo. 2004-207"], NOW)
    assert {f["status"] for f in out.values()} == {"unknown"} and set(out) == {"140 T.C. No. 16", "T.C. Memo. 2004-207"}
    assert conn.rolled_back  # the job publishes the answer on this connection next


def test_a_decided_appeal_whose_ruling_did_not_parse_is_not_pending():
    """E3 (Gregory): CourtListener found the Eleventh Circuit's opinion but its ruling didn't parse."""
    for kind in ("decided", "appealed"):  # "appealed": rows recorded before E3
        f = c.flag([("courtlistener", kind, "69 F.4th 762 (ca11 2023)", NOW)], NOW)
        assert f["status"] == "decided" and f["by"] == "69 F.4th 762 (ca11 2023)" and "could not be read" in f["note"]


def test_a_hand_checked_record_overrides_a_one_level_reading():
    """E3 (Banaitis): reversed in part by the Ninth Circuit, which the Supreme Court reversed in Banks."""
    [(cite, kind, by, _)] = c.MANUAL
    rows = [("courtlistener", "reversed in part", "340 F.3d 1074 (ca9 2003)", NOW - DAY), ("manual", kind, by, NOW)]
    f = c.flag(rows, NOW)
    assert (f["status"], f["by"], f["sources"]) == ("upheld", by, ["a hand-checked record"])
    assert "Banks" in f["note"] and cite == "T.C. Memo. 2002-5"
