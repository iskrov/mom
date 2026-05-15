"""Catalog import utilities for bulk (Option 1) workflows."""

import csv
import xml.etree.ElementTree as ET


def parse_catalog_file(filepath):
    """
    Parse CSV or XML catalog files into a normalized song list.

    Returns list of:
        {"artist": str|None, "title": str|None, "isrc": str|None}
    """
    if filepath.lower().endswith(".csv"):
        return _parse_csv(filepath)
    if filepath.lower().endswith(".xml"):
        return _parse_xml(filepath)
    raise ValueError("Unsupported catalog format. Use .csv or .xml")


def stream_catalog_records(filepath):
    """
    Lazy generator version of parse_catalog_file.

    Yields one normalized record at a time so callers can start processing
    without waiting for the full file to be read into memory.
    XML falls back to full parse (not easily streamed).
    """
    if filepath.lower().endswith(".csv"):
        with open(filepath, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                record = _norm_record(
                    artist=row.get("artist") or row.get("artist_name"),
                    title=row.get("title") or row.get("song") or row.get("song_title") or row.get("track_name"),
                    isrc=row.get("isrc"),
                )
                if record["artist"] or record["title"] or record["isrc"]:
                    yield record
    elif filepath.lower().endswith(".xml"):
        yield from parse_catalog_file(filepath)
    else:
        raise ValueError("Unsupported catalog format. Use .csv or .xml")


def count_csv_rows(filepath):
    """Fast approximate row count for a CSV (excludes header). Used to show progress before streaming."""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        return max(0, sum(1 for _ in f) - 1)


def _norm_record(artist=None, title=None, isrc=None):
    return {
        "artist": (artist or "").strip() or None,
        "title": (title or "").strip() or None,
        "isrc": (isrc or "").strip() or None,
    }


def _parse_csv(filepath):
    rows = []
    with open(filepath, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                _norm_record(
                    artist=row.get("artist") or row.get("artist_name"),
                    title=row.get("title") or row.get("song") or row.get("song_title") or row.get("track_name"),
                    isrc=row.get("isrc"),
                )
            )
    return [r for r in rows if r["artist"] or r["title"] or r["isrc"]]


def _parse_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    rows = []

    # Flexible parsing for basic XML shapes:
    # <catalog><track><artist>..</artist><title>..</title><isrc>..</isrc></track></catalog>
    # or similar tags.
    for track in root.findall(".//track"):
        artist = track.findtext("artist") or track.findtext("artist_name")
        title = track.findtext("title") or track.findtext("song") or track.findtext("song_title")
        isrc = track.findtext("isrc")
        rows.append(_norm_record(artist=artist, title=title, isrc=isrc))

    if rows:
        return [r for r in rows if r["artist"] or r["title"] or r["isrc"]]

    # fallback: parse all nodes named item/record/entry
    for node in root.findall(".//item") + root.findall(".//record") + root.findall(".//entry"):
        artist = node.findtext("artist") or node.findtext("artist_name")
        title = node.findtext("title") or node.findtext("song") or node.findtext("song_title")
        isrc = node.findtext("isrc")
        rows.append(_norm_record(artist=artist, title=title, isrc=isrc))
    return [r for r in rows if r["artist"] or r["title"] or r["isrc"]]
