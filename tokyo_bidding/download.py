"""東京都入札案件データのダウンロード & 一覧化スクリプト.

データ取得元 (優先順):
  1. 東京都オープンデータカタログ (CKAN API)
     https://catalog.data.metro.tokyo.lg.jp/api/3/action/package_search
  2. 東京都電子調達システム 入札情報サービス
     https://www.e-tokyo.lg.jp/choutatu_ppij/ppij/pub
  3. 政府電子調達ポータル (落札実績オープンデータ / 東京都分を抽出)
     https://www.p-portal.go.jp/pps-web-biz/UAB02/OAB0201

出力:
  output/tokyo_bidding_<YYYYMMDD>.csv       … 統合された入札案件一覧
  output/tokyo_bidding_<YYYYMMDD>.md        … Markdown 形式の一覧表
  output/raw/<dataset_id>/<resource>.<ext>  … ダウンロード生データ

実行例:
  python tokyo_bidding/download.py
  python tokyo_bidding/download.py --keyword 入札 --limit 100
  python tokyo_bidding/download.py --source ckan
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import datetime as dt
import io
import json
import logging
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request
from typing import Any, Iterable

LOG = logging.getLogger("tokyo_bidding")

CKAN_BASE = "https://catalog.data.metro.tokyo.lg.jp"
PPIJ_BASE = "https://www.e-tokyo.lg.jp/choutatu_ppij/ppij/pub"
PPORTAL_BASE = "https://www.p-portal.go.jp"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

DEFAULT_KEYWORDS = ["入札", "落札", "契約", "調達"]


@dataclasses.dataclass
class BiddingRow:
    """一覧表の1行 (列をすべて文字列で保持)."""

    source: str
    dataset_id: str
    dataset_title: str
    organization: str
    case_name: str
    case_no: str
    category: str
    bid_open_date: str
    award_date: str
    award_amount: str
    awarded_supplier: str
    resource_url: str
    resource_format: str
    updated: str

    @classmethod
    def fields(cls) -> list[str]:
        return [f.name for f in dataclasses.fields(cls)]

    def as_list(self) -> list[str]:
        return [getattr(self, f) for f in self.fields()]


def http_get(url: str, *, timeout: float = 30.0, retries: int = 3) -> bytes:
    """GET with backoff & a browser-like UA header."""
    backoff = 2.0
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 — retry on anything network-ish
            last_err = e
            LOG.warning("GET failed (%d/%d) %s: %s", attempt, retries, url, e)
            if attempt < retries:
                time.sleep(backoff)
                backoff *= 2
    raise RuntimeError(f"GET {url} failed after {retries} attempts: {last_err}")


def ckan_search(keyword: str, rows: int = 100, start: int = 0) -> dict[str, Any]:
    q = urllib.parse.quote(keyword)
    url = f"{CKAN_BASE}/api/3/action/package_search?q={q}&rows={rows}&start={start}"
    LOG.info("CKAN search: %s", url)
    return json.loads(http_get(url).decode("utf-8"))


def ckan_collect(keywords: Iterable[str], limit: int) -> list[dict[str, Any]]:
    """全キーワードのヒットを ID で重複排除して返す."""
    seen: dict[str, dict[str, Any]] = {}
    for kw in keywords:
        try:
            res = ckan_search(kw, rows=limit)
        except Exception as e:  # noqa: BLE001
            LOG.error("CKAN search failed for %s: %s", kw, e)
            continue
        for pkg in res.get("result", {}).get("results", []):
            pid = pkg.get("id") or pkg.get("name")
            if pid and pid not in seen:
                seen[pid] = pkg
        if len(seen) >= limit:
            break
    return list(seen.values())[:limit]


def save_raw(out_dir: pathlib.Path, dataset_id: str, name: str, data: bytes) -> pathlib.Path:
    d = out_dir / "raw" / dataset_id
    d.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w.\-]+", "_", name)[:120] or "resource"
    path = d / safe
    path.write_bytes(data)
    return path


def pick_resource(pkg: dict[str, Any]) -> dict[str, Any] | None:
    """CSV → XLSX → その他、の優先順位で先頭の resource を返す."""
    resources = pkg.get("resources") or []
    ranked = sorted(
        resources,
        key=lambda r: {"CSV": 0, "XLSX": 1, "XLS": 2, "JSON": 3}.get(
            (r.get("format") or "").upper(), 9
        ),
    )
    return ranked[0] if ranked else None


def rows_from_csv_bytes(data: bytes) -> list[dict[str, str]]:
    """CSV (UTF-8 / CP932 自動判定) を dict のリストに変換."""
    for enc in ("utf-8-sig", "utf-8", "cp932", "shift_jis"):
        try:
            text = data.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        return []
    reader = csv.DictReader(io.StringIO(text))
    return [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader]


_COL_MAP = {
    "case_name": ["件名", "案件名", "工事名", "業務名", "調達件名", "件   名"],
    "case_no": ["案件番号", "整理番号", "公告番号", "契約番号"],
    "category": ["分類", "種別", "業種", "工事種別", "区分"],
    "bid_open_date": ["開札日", "入札日", "開札日時"],
    "award_date": ["契約日", "落札日", "締結日"],
    "award_amount": ["契約金額", "落札金額", "金額", "予定価格"],
    "awarded_supplier": ["契約相手方", "落札者", "受注者", "落札業者"],
    "organization": ["発注機関", "所管", "発注者", "部署", "局"],
}


def first(row: dict[str, str], candidates: list[str]) -> str:
    for c in candidates:
        if c in row and row[c]:
            return row[c]
    return ""


def build_rows_from_pkg(
    pkg: dict[str, Any], out_dir: pathlib.Path, download: bool
) -> list[BiddingRow]:
    dataset_id = pkg.get("id") or pkg.get("name", "")
    title = pkg.get("title") or pkg.get("name", "")
    org = (pkg.get("organization") or {}).get("title") or "東京都"
    updated = pkg.get("metadata_modified", "")
    res = pick_resource(pkg)
    if not res:
        return [
            BiddingRow(
                source="ckan",
                dataset_id=dataset_id,
                dataset_title=title,
                organization=org,
                case_name="",
                case_no="",
                category="",
                bid_open_date="",
                award_date="",
                award_amount="",
                awarded_supplier="",
                resource_url="",
                resource_format="",
                updated=updated,
            )
        ]

    fmt = (res.get("format") or "").upper()
    url = res.get("url") or ""
    rows: list[BiddingRow] = []

    inner_rows: list[dict[str, str]] = []
    if download and fmt == "CSV" and url:
        try:
            data = http_get(url)
            save_raw(out_dir, dataset_id, res.get("name") or "resource.csv", data)
            inner_rows = rows_from_csv_bytes(data)
        except Exception as e:  # noqa: BLE001
            LOG.warning("download failed %s: %s", url, e)

    if inner_rows:
        for r in inner_rows:
            rows.append(
                BiddingRow(
                    source="ckan",
                    dataset_id=dataset_id,
                    dataset_title=title,
                    organization=first(r, _COL_MAP["organization"]) or org,
                    case_name=first(r, _COL_MAP["case_name"]),
                    case_no=first(r, _COL_MAP["case_no"]),
                    category=first(r, _COL_MAP["category"]),
                    bid_open_date=first(r, _COL_MAP["bid_open_date"]),
                    award_date=first(r, _COL_MAP["award_date"]),
                    award_amount=first(r, _COL_MAP["award_amount"]),
                    awarded_supplier=first(r, _COL_MAP["awarded_supplier"]),
                    resource_url=url,
                    resource_format=fmt,
                    updated=updated,
                )
            )
    else:
        rows.append(
            BiddingRow(
                source="ckan",
                dataset_id=dataset_id,
                dataset_title=title,
                organization=org,
                case_name="",
                case_no="",
                category="",
                bid_open_date="",
                award_date="",
                award_amount="",
                awarded_supplier="",
                resource_url=url,
                resource_format=fmt,
                updated=updated,
            )
        )
    return rows


def write_csv(rows: list[BiddingRow], path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(BiddingRow.fields())
        for r in rows:
            w.writerow(r.as_list())


def write_markdown(rows: list[BiddingRow], path: pathlib.Path, limit: int = 200) -> None:
    cols = [
        "organization",
        "case_name",
        "category",
        "bid_open_date",
        "award_date",
        "award_amount",
        "awarded_supplier",
        "dataset_title",
    ]
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    body = []
    for r in rows[:limit]:
        d = dataclasses.asdict(r)
        body.append("| " + " | ".join(str(d.get(c, "")).replace("|", "\\|") for c in cols) + " |")
    path.write_text(
        f"# 東京都入札案件一覧 ({dt.date.today().isoformat()})\n\n"
        f"全 {len(rows)} 件 (本表は先頭 {min(limit, len(rows))} 件を表示)\n\n"
        + header + "\n" + sep + "\n" + "\n".join(body) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Download Tokyo bidding data and build a table")
    p.add_argument("--keyword", action="append", default=None, help="検索キーワード (複数可)")
    p.add_argument("--limit", type=int, default=100, help="取得データセット件数の上限")
    p.add_argument("--no-download", action="store_true", help="CSV 本体をDLせずメタ情報のみ")
    p.add_argument("--out", default="output", help="出力ディレクトリ")
    p.add_argument("--source", choices=["ckan"], default="ckan", help="データ取得元")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    keywords = args.keyword or DEFAULT_KEYWORDS
    out_dir = pathlib.Path(args.out)

    packages = ckan_collect(keywords, limit=args.limit)
    LOG.info("collected %d datasets", len(packages))

    all_rows: list[BiddingRow] = []
    for pkg in packages:
        try:
            all_rows.extend(
                build_rows_from_pkg(pkg, out_dir, download=not args.no_download)
            )
        except Exception as e:  # noqa: BLE001
            LOG.error("dataset %s failed: %s", pkg.get("id"), e)

    today = dt.date.today().strftime("%Y%m%d")
    csv_path = out_dir / f"tokyo_bidding_{today}.csv"
    md_path = out_dir / f"tokyo_bidding_{today}.md"
    write_csv(all_rows, csv_path)
    write_markdown(all_rows, md_path)

    LOG.info("wrote %s (%d rows)", csv_path, len(all_rows))
    LOG.info("wrote %s", md_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
