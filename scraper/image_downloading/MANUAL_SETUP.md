# Manual Setup Guide for Supabase Storage

Since you don't have owner permissions on the `storage.objects` table, you'll need to set up the storage bucket manually through the Supabase dashboard.

## Step 1: Create Storage Bucket

1. **Go to your Supabase Dashboard**
2. **Navigate to Storage** (in the left sidebar)
3. **Click "Create a new bucket"**
4. **Fill in the details:**
   - **Name:** `restaurant-images`
   - **Public:** ✅ **Yes** (check this box)
   - **File size limit:** `10 MB`
   - **Allowed MIME types:** `image/jpeg, image/png, image/webp`

5. **Click "Create bucket"**

## Step 2: Set Bucket Policies

1. **Go to Authentication → Policies** (in the left sidebar)
2. **Find the `storage.objects` table**
3. **Click "New Policy"**
4. **Create these policies:**

### Policy 1: Public Read Access
- **Policy name:** `Allow public read access to restaurant images`
- **Operation:** `SELECT`
- **Target roles:** `public`
- **Policy definition:**
```sql
bucket_id = 'restaurant-images'
```

### Policy 2: Authenticated Upload
- **Policy name:** `Allow authenticated users to upload restaurant images`
- **Operation:** `INSERT`
- **Target roles:** `authenticated`
- **Policy definition:**
```sql
bucket_id = 'restaurant-images' AND auth.role() = 'authenticated'
```

### Policy 3: Authenticated Update
- **Policy name:** `Allow authenticated users to update restaurant images`
- **Operation:** `UPDATE`
- **Target roles:** `authenticated`
- **Policy definition:**
```sql
bucket_id = 'restaurant-images' AND auth.role() = 'authenticated'
```

### Policy 4: Authenticated Delete
- **Policy name:** `Allow authenticated users to delete restaurant images`
- **Operation:** `DELETE`
- **Target roles:** `authenticated`
- **Policy definition:**
```sql
bucket_id = 'restaurant-images' AND auth.role() = 'authenticated'
```

## Step 3: Add Database Column (Optional)

Run this SQL in the SQL Editor:

```sql
ALTER TABLE restaurants ADD COLUMN original_image_urls TEXT[];
```

## Step 4: Test the Setup

After completing the manual setup, test the image downloader:

```bash
cd scraper/image_downloading
/Users/zeldon/anaconda3/envs/py3115/bin/python test_setup.py
```

## Alternative: Disable RLS Temporarily

If you have admin access, you can temporarily disable RLS:

1. **Go to SQL Editor**
2. **Run this command:**
```sql
ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;
```

3. **Run your image downloader**
4. **Re-enable RLS after completion:**
```sql
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;
```

## Troubleshooting

### If you still get permission errors:
1. **Check your Supabase project permissions**
2. **Ensure you're using the correct API key**
3. **Try using the service role key instead of the anon key**

### If bucket creation fails:
1. **Check if the bucket already exists**
2. **Try a different bucket name**
3. **Verify your project has storage enabled**

### If uploads still fail:
1. **Check the bucket is set to public**
2. **Verify the policies are correctly set**
3. **Test with a simple file upload first**
