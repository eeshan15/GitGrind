import io
p = "tools/import_mineru_bank.py"
s = io.open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s
o = '            caption=" ".join(node.get("image_caption") or [])[:200],'
n = ('            # v2 captions are typed spans ({"type","content"}), not plain\r\n'
     '            # strings, so flatten either shape before joining.\r\n'
     '            caption=" ".join(\r\n'
     '                (c.get("content") or "") if isinstance(c, dict) else str(c)\r\n'
     '                for c in (node.get("image_caption") or [])\r\n'
     '            ).strip()[:200],') if crlf else (
     '            # v2 captions are typed spans ({"type","content"}), not plain\n'
     '            # strings, so flatten either shape before joining.\n'
     '            caption=" ".join(\n'
     '                (c.get("content") or "") if isinstance(c, dict) else str(c)\n'
     '                for c in (node.get("image_caption") or [])\n'
     '            ).strip()[:200],')
assert s.count(o) == 1, s.count(o)
io.open(p, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
print("patched")
