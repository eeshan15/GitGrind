Your database lives here as gitgrind.db once you start the app.

This is the only file that holds your work: sessions, topic progress, quiz
attempts, daily questions, stickers and readiness history. Everything else in
the project can be regenerated from the source.

Back it up. Copying gitgrind.db somewhere safe is enough, or use
Activity -> Export backup for a portable JSON file (which also strips your API
key, so it is safe to move around).

SQLite runs in WAL mode, so you may also see gitgrind.db-wal and
gitgrind.db-shm alongside it. Copy all three, or stop the app first so they
fold back into the main file.
