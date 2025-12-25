import { db } from './lib/db';
import { stories, pages } from './lib/schema';

async function clearDatabase() {
  try {
    console.log('Clearing all pages...');
    await db.delete(pages);

    console.log('Clearing all stories...');
    await db.delete(stories);

    console.log('Database cleared successfully!');
  } catch (error) {
    console.error('Error clearing database:', error);
  } finally {
    process.exit(0);
  }
}

clearDatabase();