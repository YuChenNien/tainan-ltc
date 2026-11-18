import { defineConfig } from 'astro/config';
import icon from 'astro-icon';

// 部署到 GitHub Pages 時，網址是 https://<帳號>.github.io/<儲存庫名稱>/
// 這兩個值由部署設定（.github/workflows/deploy.yml）自動帶入；本機預覽時用預設值。
const site = process.env.SITE_URL || 'http://localhost:4321';
const base = process.env.BASE_PATH || '/';

export default defineConfig({
  site,
  base,
  integrations: [icon()],
  trailingSlash: 'always',
});
