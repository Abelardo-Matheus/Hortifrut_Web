// ==========================================
// Configuração do Supabase Client
// ==========================================

const SUPABASE_URL = 'https://bslfvnhtirrykxedgpkw.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJzbGZ2bmh0aXJyeWt4ZWRncGt3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ4MDU4MDksImV4cCI6MjEwMDM4MTgwOX0.LDt_M3ROkcY9RGN1QNo1XUTFOxjCvFpNwkA7RjdYTvA';

// Inicializa o cliente (requer que a biblioteca do Supabase seja carregada no HTML via CDN antes)
window.supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
