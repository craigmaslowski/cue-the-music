import { defineConfig, devices } from '@playwright/test';
import { nxE2EPreset } from '@nx/playwright/preset';
import { workspaceRoot } from '@nx/devkit';
import { mkdtempSync, writeFileSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

// Create temp DB path for this test run — isolated from dev/production
const tempDir = mkdtempSync(join(tmpdir(), 'cue-e2e-'));
const dbPath = join(tempDir, 'test.db');
const dbUrl = `sqlite+aiosqlite:///${dbPath}`;

// Write meta for global-teardown to clean up
writeFileSync(
  join(tmpdir(), 'cue-e2e-meta.json'),
  JSON.stringify({ dbPath, tempDir }),
);

// Set env vars for backend webServer process
process.env['DATABASE_URL'] = dbUrl;
process.env['DISCOGS_TOKEN'] = 'e2e-test-token';
process.env['DISCOGS_USERNAME'] = 'e2e-test-user';
process.env['HOST_PIN'] = '1234';
process.env['TEST_MODE'] = 'true';

const baseURL = process.env['BASE_URL'] || 'http://localhost:4200';

export default defineConfig({
  ...nxE2EPreset(__filename, { testDir: './src' }),
  globalTeardown: './src/global-teardown.ts',
  use: {
    baseURL,
    trace: 'on-first-retry',
  },
  timeout: 30_000,
  webServer: [
    {
      command:
        'cd apps/backend && uv run alembic upgrade head && uv run uvicorn cue_the_music.main:app --port 8000',
      cwd: workspaceRoot,
      env: { ...process.env },
      reuseExistingServer: true,
      timeout: 30_000,
      url: 'http://localhost:8000/api/albums',
    },
    {
      command: 'npx nx run @cue-the-music/frontend:preview',
      cwd: workspaceRoot,
      reuseExistingServer: true,
      timeout: 60_000,
      url: 'http://localhost:4200',
    },
  ],
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 14'] },
    },
  ],
});
