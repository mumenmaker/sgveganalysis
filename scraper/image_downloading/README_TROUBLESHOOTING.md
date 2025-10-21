# Troubleshooting Image Downloader

## Common Issues and Solutions

### 1. RLS Policy Errors

**Error:** `new row violates row-level security policy`

**Solution:** Run the SQL script to fix RLS policies:

1. Go to your Supabase dashboard
2. Navigate to SQL Editor
3. Copy and paste the contents of `fix_rls_policies.sql`
4. Run the script

### 2. Missing Database Column

**Error:** `Could not find the 'original_image_urls' column`

**Solution:** The script will automatically skip backup if the column doesn't exist. To add it:

```sql
ALTER TABLE restaurants ADD COLUMN original_image_urls TEXT[];
```

### 3. SVG/Placeholder Images

**Error:** `cannot identify image file`

**Solution:** The script now automatically skips SVG and placeholder images.

### 4. Storage Bucket Issues

**Error:** `Bucket creation failed`

**Solution:** 
1. Create the bucket manually in Supabase dashboard
2. Or run the SQL script to create it automatically

### 5. Authentication Issues

**Error:** `Unauthorized`

**Solution:** 
1. Check your Supabase URL and key in `.env` file
2. Ensure the key has the correct permissions
3. Run the RLS policy fix script

## Quick Fix Commands

### Reset Progress
```bash
python run_image_downloader.py
# Choose option 6: Reset progress tracking
```

### Test Setup
```bash
python test_setup.py
```

### Manual Storage Setup
1. Go to Supabase Dashboard → Storage
2. Create bucket named `restaurant-images`
3. Set as public
4. Set file size limit to 10MB
5. Allow MIME types: image/jpeg, image/png, image/webp

## Environment Variables

Make sure your `.env` file contains:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

## Database Schema

The script expects these columns in the `restaurants` table:

- `id` (primary key)
- `images_links` (TEXT[] - array of image URLs)
- `original_image_urls` (TEXT[] - optional backup column)

## Storage Structure

Images are stored as:
```
restaurant-images/
└── restaurants/
    ├── restaurant_1_0_abc123.jpg
    ├── restaurant_1_1_def456.jpg
    └── ...
```

## Performance Tips

1. **Start Small:** Process 10-20 restaurants first
2. **Monitor Progress:** Use the progress tracking features
3. **Resume Capability:** The script can resume interrupted processing
4. **Batch Processing:** Images are processed in configurable batches

## Debug Mode

Enable debug logging:

```bash
export DEBUG=1
python run_image_downloader.py
```

## Common Solutions

### If images fail to upload:
1. Check RLS policies
2. Verify bucket exists and is public
3. Check file size limits
4. Verify authentication

### If database updates fail:
1. Check column names
2. Verify table permissions
3. Check for data type mismatches

### If processing is slow:
1. Reduce batch size in config.py
2. Increase delays between requests
3. Check network connectivity
