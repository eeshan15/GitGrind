#!/usr/bin/env python3
"""Reconnect imported history to the current question bank, automatically.

A question_id is a content value, not a database key. When a bank is replaced the
ids change, so a backup taken on an older bank imports with every row intact and
then reads as empty on every per-topic view - the data is disconnected, not lost,
and from the outside those look identical.

This makes /api/import repair the references itself and report what it did.

CRLF-safe and idempotent. Run from the repo root:  python patch_import_repair.py
"""
import io, os, sys

EDITS = [
    ('core/content.py',
     'import re\n',
     'import re\nimport sqlite3\n'),
    ('core/content.py',
     'def paper_summary(conn):',
     '# Bank prefixes an id may have gained. The mineru extraction replaced an earlier\n# one that used bare filter1-* ids, keeping the same suffix, so history recorded\n# under the old scheme is recoverable by prefixing.\nID_PREFIXES = ("mineru-",)\n\n\ndef remap_orphaned_question_ids(conn, prefixes=ID_PREFIXES):\n    """Re-point activity rows at ids that still exist in the bank.\n\n    A question_id is a content value, not a database key. Replacing a bank\n    changes the ids, and every attempt referencing the old scheme becomes an\n    orphan: the row survives, but nothing resolves it, so it stops counting\n    towards a topic and disappears from the heatmap. The data is not lost, it is\n    disconnected - and the person cannot tell the difference from the outside.\n\n    A row is only rewritten when the candidate id actually exists in the bank. An\n    orphan with no candidate is left alone and counted, because a wrong remap\n    would credit a result to a question that was never answered.\n    """\n    bank = question_bank()\n    tables = []\n    for row in conn.execute(\n        "SELECT name FROM sqlite_master WHERE type=\'table\' AND name NOT LIKE \'sqlite_%\'"\n    ):\n        cols = {r[1] for r in conn.execute(\'PRAGMA table_info("%s")\' % row[0])}\n        if "question_id" in cols:\n            tables.append(row[0])\n\n    remapped, rows_touched = 0, 0\n    stuck = set()\n    with conn:\n        for table in sorted(tables):\n            ids = [\n                r[0]\n                for r in conn.execute(\n                    \'SELECT DISTINCT question_id FROM "%s"\'\n                    " WHERE question_id IS NOT NULL" % table\n                )\n            ]\n            for old in ids:\n                if not old or old in bank:\n                    continue\n                new = next((p + old for p in prefixes if p + old in bank), None)\n                if not new:\n                    stuck.add(old)\n                    continue\n                try:\n                    cur = conn.execute(\n                        \'UPDATE "%s" SET question_id = ? WHERE question_id = ?\' % table,\n                        (new, old),\n                    )\n                    rows_touched += cur.rowcount\n                    remapped += 1\n                except sqlite3.IntegrityError:\n                    # A row already exists under the new id: keep it, drop the stale one.\n                    conn.execute(\n                        \'DELETE FROM "%s" WHERE question_id = ?\' % table, (old,)\n                    )\n    return dict(\n        remapped=remapped, rows=rows_touched, unresolved=sorted(stuck)\n    )\n\n\ndef paper_summary(conn):'),
    ('core/api.py',
     '        content.seed(conn)\n        return build_state(conn)',
     '        content.seed(conn)\n        # A backup taken on an older bank references ids that no longer exist, so\n        # the history would import intact and then read as empty on every\n        # per-topic view. Reconnect it here rather than leaving the person to\n        # conclude the import lost their data.\n        repair = content.remap_orphaned_question_ids(conn)\n        state = build_state(conn)\n        state["import_repair"] = repair\n        return state'),
    ('static/js/app.js',
     "        apply(await GG.api('/import', { body: payload }));\n        GG.toast('Backup restored');",
     "        const state = await GG.api('/import', { body: payload });\n        apply(state);\n        /* A backup from an older bank carries question ids that have since been\n           replaced. Say what was reconnected and what was not, because silence\n           here reads as data loss. */\n        const r = state.import_repair || {};\n        const stuck = (r.unresolved || []).length;\n        if (r.rows) {\n          GG.toast('Backup restored',\n            r.rows + ' history row(s) reconnected to the current question bank' +\n            (stuck ? ', ' + stuck + ' question(s) no longer in the bank' : ''));\n        } else if (stuck) {\n          GG.toast('Backup restored',\n            stuck + ' question(s) in your history are no longer in the bank. ' +\n            'Those attempts are kept but will not show under a topic.');\n        } else {\n          GG.toast('Backup restored');\n        }"),
]


def main():
    changed = skipped = 0
    for path, old, new in EDITS:
        if not os.path.isfile(path):
            sys.exit("missing %s - run this from the repo root" % path)
        s = io.open(path, encoding="utf-8", newline="").read()
        crlf = "\r\n" in s
        o = old.replace("\n", "\r\n") if crlf else old
        n = new.replace("\n", "\r\n") if crlf else new
        if n in s:
            print("  skip    %-22s already applied" % path)
            skipped += 1
            continue
        if s.count(o) != 1:
            sys.exit("  ERROR   %s: anchor found %d times, expected 1" % (path, s.count(o)))
        io.open(path, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched %-22s ok" % path)
        changed += 1
    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())