import { ApifyClient } from 'apify-client';
import xlsx from 'xlsx';
import fs from 'fs';

const HASHTAGS = ['contohtag1', 'contohtag2'];
const MAX_POSTS_PER_HASHTAG = 200;
const MIN_FOLLOWERS = 100;
const MIN_DATE = new Date('2020-01-01T00:00:00Z');
const OUTPUT_XLSX = 'data/instagram_indonesia_all.xlsx';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

async function main() {
  console.log('='.repeat(60));
  console.log('APIFY INSTAGRAM CRAWLER (Node.js)');
  console.log('='.repeat(60));

  if (!process.env.APIFY_TOKEN) {
    throw new Error('APIFY_TOKEN belum di-set. Jalankan: export APIFY_TOKEN=...');
  }

  const allRows = [];

  for (const hashtag of HASHTAGS) {
    console.log(`\n[HASHTAG] #${hashtag} — menjalankan actor...`);

    const input = {
      hashtags: [hashtag],
      maxPostsPerHashtag: MAX_POSTS_PER_HASHTAG,
      includeReels: true,
      includeDetails: true,
      proxyConfiguration: { useApifyProxy: true },
    };

    const run = await client.actor('automation-lab/instagram-hashtag-posts-scraper').call(input);

    console.log(`  RUN_ID: ${run.id}  STATUS: ${run.status}`);

    const { items } = await client.dataset(run.defaultDatasetId).listItems();
    console.log(`  ITEMS_FETCHED: ${items.length}`);

    for (const item of items) {
      const postDate = item.timestamp ? new Date(item.timestamp) : null;
      if (postDate && postDate < MIN_DATE) continue;

      const followers = item.ownerFollowersCount ?? item.followersCount ?? null;
      if (followers !== null && followers < MIN_FOLLOWERS) continue;

      allRows.push({
        hashtag,
        username: item.ownerUsername ?? item.username ?? '',
        followers: followers ?? '',
        postUrl: item.postUrl ?? '',
        caption: item.caption ?? '',
        likesCount: item.likesCount ?? '',
        commentsCount: item.commentsCount ?? '',
        timestamp: item.timestamp ?? '',
        mediaType: item.mediaType ?? '',
      });
    }
  }

  console.log(`\nTOTAL_ROWS_AFTER_FILTER: ${allRows.length}`);

  if (allRows.length === 0) {
    console.log('Tidak ada data yang lolos filter. Cek HASHTAGS / MIN_FOLLOWERS / MIN_DATE.');
    return;
  }

  const worksheet = xlsx.utils.json_to_sheet(allRows);
  const workbook = xlsx.utils.book_new();
  xlsx.utils.book_append_sheet(workbook, worksheet, 'instagram_data');

  fs.mkdirSync('data', { recursive: true });
  xlsx.writeFile(workbook, OUTPUT_XLSX);

  console.log(`\nEXCEL_SAVED: ${OUTPUT_XLSX}`);
  console.log('='.repeat(60));
}

main().catch((err) => {
  console.error('ERROR:', err.message);
  process.exit(1);
});
