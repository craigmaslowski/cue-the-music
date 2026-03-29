import { mkdtempSync, writeFileSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

/** Create a temp directory for the E2E test database and set env vars. */
export default function globalSetup() {
  const tempDir = mkdtempSync(join(tmpdir(), 'cue-e2e-'));
  const dbPath = join(tempDir, 'test.db');
  const dbUrl = `sqlite+aiosqlite:///${dbPath}`;

  // Set env vars for the backend webServer process
  process.env['DATABASE_URL'] = dbUrl;
  process.env['TEST_MODE'] = 'true';
  process.env['HOST_PIN'] = '1234';
  process.env['DISCOGS_TOKEN'] = 'e2e-test-token';
  process.env['DISCOGS_USERNAME'] = 'e2e-test-user';

  // Write temp dir path so teardown can clean up
  const metaPath = join(tmpdir(), 'cue-e2e-meta.json');
  writeFileSync(metaPath, JSON.stringify({ dbPath, tempDir }));
}
