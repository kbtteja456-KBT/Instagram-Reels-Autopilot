"""Script to inspect, report, and delete duplicate reels from MongoDB and local storage.
Generates a comprehensive report of Instagram Reels to delete manually or via Meta.
"""

import os
import sys
from pathlib import Path

# Ensure workspace root is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from collections import defaultdict
from pymongo import MongoClient

from backend.app.config import settings

def run_cleanup(dry_run: bool = False):
    print("=" * 60)
    print("AI INSTAGRAM REELS AUTOPILOT - DUPLICATE CLEANUP ENGINE")
    print(f"Mode: {'DRY RUN (Analysis Only)' if dry_run else 'ACTIVE CLEANUP'}")
    print("=" * 60)

    # 1. Connect to MongoDB
    client = MongoClient(settings.mongodb_uri)
    db = client[settings.mongodb_db_name]

    posted_docs = list(db.posted_quizzes.find())
    print(f"\n[MongoDB: posted_quizzes] Total records: {len(posted_docs)}")

    by_title = defaultdict(list)
    for doc in posted_docs:
        title = (doc.get("title") or "").strip().lower()
        by_title[title].append(doc)

    mongo_dups_to_delete = []
    instagram_dups = []
    unique_kept = []

    for title, group in by_title.items():
        # Sort by posted_at or date to keep the very first legitimate post
        def sort_key(x):
            val = x.get("posted_at") or x.get("created_at") or "9999"
            return str(val)

        group.sort(key=sort_key)
        kept = group[0]
        unique_kept.append(kept)

        if len(group) > 1:
            print(f"\n[Duplicate Cluster] \"{group[0].get('title')}\" - {len(group)} instances")
            print(f"  -> KEPT ORIGINAL: ID={kept.get('_id')} | MediaID={kept.get('media_id') or kept.get('instagram_media_id')} | URL={kept.get('instagram_url')}")
            for dup in group[1:]:
                mongo_dups_to_delete.append(dup)
                url = dup.get("instagram_url")
                media_id = dup.get("media_id") or dup.get("instagram_media_id")
                posted_at = dup.get("posted_at") or dup.get("created_at")
                quiz_id = dup.get("quiz_id")
                instagram_dups.append({
                    "title": dup.get("title"),
                    "quiz_id": quiz_id,
                    "media_id": media_id,
                    "url": url,
                    "posted_at": posted_at
                })
                print(f"  -> DUPLICATE TO PURGE: ID={dup.get('_id')} | MediaID={media_id} | URL={url}")

    print(f"\n[MongoDB Summary] Kept {len(unique_kept)} unique records, found {len(mongo_dups_to_delete)} duplicate records.")

    # 2. Cleanup MongoDB reels collection as well
    reels_docs = list(db.reels.find())
    print(f"\n[MongoDB: reels] Total records: {len(reels_docs)}")
    reels_by_title = defaultdict(list)
    for r in reels_docs:
        t = (r.get("title") or "").strip().lower()
        reels_by_title[t].append(r)

    reels_to_delete = []
    for t, rgroup in reels_by_title.items():
        if len(rgroup) > 1:
            rgroup.sort(key=lambda x: str(x.get("created_at") or x.get("instagram_published_at") or "9999"))
            for dup_r in rgroup[1:]:
                reels_to_delete.append(dup_r)

    print(f"[MongoDB reels Summary] Found {len(reels_to_delete)} duplicate records in db.reels.")

    if not dry_run:
        if mongo_dups_to_delete:
            delete_ids = [d["_id"] for d in mongo_dups_to_delete]
            res = db.posted_quizzes.delete_many({"_id": {"$in": delete_ids}})
            print(f"-> Deleted {res.deleted_count} duplicate documents from db.posted_quizzes.")

        if reels_to_delete:
            delete_rids = [d["_id"] for d in reels_to_delete]
            res_r = db.reels.delete_many({"_id": {"$in": delete_rids}})
            print(f"-> Deleted {res_r.deleted_count} duplicate documents from db.reels.")

    # 3. Cleanup local posted_quizzes.json
    posted_json_path = Path(settings.media_storage_dir) / "posted_quizzes.json"
    if posted_json_path.exists():
        with open(posted_json_path, "r", encoding="utf-8") as f:
            local_items = json.load(f)

        print(f"\n[Local JSON] Total items in {posted_json_path}: {len(local_items)}")
        local_by_title = defaultdict(list)
        for item in local_items:
            t = (item.get("title") or "").strip().lower()
            local_by_title[t].append(item)

        cleaned_local = []
        for t, lgroup in local_by_title.items():
            lgroup.sort(key=lambda x: str(x.get("posted_at") or "9999"))
            cleaned_local.append(lgroup[0])

        print(f"-> Deduplicated local JSON from {len(local_items)} to {len(cleaned_local)} items.")
        if not dry_run:
            with open(posted_json_path, "w", encoding="utf-8") as f:
                json.dump(cleaned_local, f, indent=2)
            print("-> Successfully updated local posted_quizzes.json.")

    # 4. Cleanup redundant local video files in media_storage/reels
    reels_dir = Path(settings.media_storage_dir) / "reels"
    if reels_dir.exists():
        video_files = list(reels_dir.glob("*.mp4"))
        print(f"\n[Local Video Files] Found {len(video_files)} mp4 files in {reels_dir}")

        # Group by quiz prefix, e.g. reel_set_comprehension_modulo...
        # Keep only the single most recent or oldest genuine file per quiz type
        files_by_quiz = defaultdict(list)
        for vf in video_files:
            # reel_set_comprehension_modulo_202609221257_20260922_182742.mp4
            name = vf.stem
            # extract key
            parts = name.split("_")
            if len(parts) >= 2:
                prefix = "_".join(parts[:3]) # e.g. reel_set_comprehension
            else:
                prefix = name
            files_by_quiz[prefix].append(vf)

        deleted_file_count = 0
        freed_bytes = 0
        for prefix, flist in files_by_quiz.items():
            if len(flist) > 1:
                # sort by mtime
                flist.sort(key=lambda f: f.stat().st_mtime)
                # keep the latest file, delete previous redundant renderings
                for redundant_file in flist[:-1]:
                    try:
                        sz = redundant_file.stat().st_size
                        if not dry_run:
                            redundant_file.unlink()
                        deleted_file_count += 1
                        freed_bytes += sz
                    except Exception as e:
                        print(f"Error removing {redundant_file}: {e}")

        mb_freed = freed_bytes / (1024 * 1024)
        print(f"-> {'[Dry Run] Would delete' if dry_run else 'Deleted'} {deleted_file_count} duplicate mp4 video files ({mb_freed:.2f} MB freed).")

    # 5. Output Instagram duplicates report
    print("\n" + "=" * 60)
    print("INSTAGRAM REELS DUPLICATE AUDIT REPORT")
    print("=" * 60)
    print(f"Found {len(instagram_dups)} duplicate posts that were uploaded to Instagram.\n")

    report_lines = []
    report_lines.append("# Instagram Duplicate Reels Deletion Report\n")
    report_lines.append(f"Generated at: {__import__('datetime').datetime.now().isoformat()}\n")
    report_lines.append(f"Total Duplicate Posts to Delete: **{len(instagram_dups)}**\n")
    report_lines.append("| # | Title | Date Posted | Instagram Media ID | Instagram URL |")
    report_lines.append("|---|---|---|---|---|")

    # Dedup by URL for the report
    seen_urls = set()
    counter = 1
    for item in instagram_dups:
        url = item.get("url")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        mid = item.get("media_id") or "N/A"
        title = item.get("title") or "Python Quiz"
        pat = item.get("posted_at") or "N/A"
        line = f"| {counter} | {title} | {pat} | `{mid}` | [{url}]({url}) |"
        report_lines.append(line)
        print(f"{counter}. {title}")
        print(f"   URL: {url} | ID: {mid} | Date: {pat}")
        counter += 1

    report_path = Path("DUPLICATE_REELS_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n-> Full report saved to: {report_path.resolve()}")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    dry = "--dry-run" in sys.argv
    run_cleanup(dry_run=dry)
