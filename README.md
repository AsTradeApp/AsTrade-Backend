Here’s the translated and adapted version of your backend tutorial section in English:

---

# AsTrade Backend

## 📚 **Documentation**

* [📡 **Endpoints**](docs/ENDPOINTS.md) – All API endpoints
* [🏗️ **Structure**](docs/BACKEND_STRUCTURE_ANALYSIS.md) – Backend architecture analysis

---

## 🚀 **Tutorial: Running the Backend (Developer Guide)**

### **Step 1: Set Up Supabase**

1. **Create a Supabase project**
2. **Run the full SQL setup script:**

   * Open the SQL Editor in Supabase
   * Copy and paste the contents of [`setup_database.sql`](setup_database.sql)
   * Execute the full script

**📁 Full SQL file:** [`setup_database.sql`](setup_database.sql)

> **Note:** The SQL script includes:
>
> * User tables (wallets, credentials, profiles)
> * Reward system and NFTs
> * Planets and quizzes
> * User progress tracking
> * RLS enabled with security policies
> * Automatic `updated_at` triggers
> * Indexes for performance

---

### **Step 2: Configure Environment Variables**

```bash
# Copy the example file
cp extended.env.example .env

# Edit with your Supabase credentials
nano .env
```

**Required variables in `.env`:**

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SECRET_KEY=your-secret-key
```

---

### **Step 3: Start the Backend**

```bash
# Start using Docker
docker-compose up -d

# View logs
docker-compose logs -f api

# Check that it’s working
curl http://localhost:8000/health

# Integration status
curl http://localhost:8000/api/v1/users/integration/status
```

---

### **Useful Commands**

```bash
# Stop the backend
docker-compose down

# Rebuild the image
docker-compose build --no-cache

# Tail logs
docker-compose logs -f

# Run tests
./test_docker.sh
```

---

**✅ Your backend is now running at `http://localhost:8000`**

Let me know if you want this added to the documentation file or linked from the README!
