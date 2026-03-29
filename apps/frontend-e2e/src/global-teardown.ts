import { existsSync, readFileSync, rmSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

/** Clean up the temp database directory after all E2E tests. */
export default function globalTeardown() {
  const metaPath = join(tmpdir(), 'cue-e2e-meta.json');
  if (!existsSync(metaPath)) return;

  const { tempDir } = JSON.parse(readFileSync(metaPath, 'utf-8')) as {
    tempDir: string;
  };

  // Remove temp dir and all contents (db, shm, wal)
  if (existsSync(tempDir)) {
    rmSync(tempDir, { force: true, recursive: true });
  }

  rmSync(metaPath, { force: true });
}
