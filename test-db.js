const { Pool } = require('pg');

const pool = new Pool({
  user: 'postgres',
  password: 'postgres',
  host: 'localhost',
  port: 5432,
  database: 'library_db'
});

async function testConnection() {
  let client;
  try {
    console.log('Attempting to connect...');
    client = await pool.connect();
    console.log('Connected successfully!');
    
    const result = await client.query('SELECT NOW()');
    console.log('Query result:', result.rows[0]);
  } catch (err) {
    console.error('Connection error:', err);
  } finally {
    if (client) {
      client.release();
      pool.end();
    }
  }
}

testConnection();
