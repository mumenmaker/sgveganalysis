# Coordinate-Based Unique Constraint

## Why Use Latitude/Longitude Instead of Name?

### Problems with Name-Based Constraints:
- ❌ **Similar names**: "McDonald's" vs "McDonald's Restaurant"
- ❌ **Different languages**: "Restaurant ABC" vs "ABC 餐厅"
- ❌ **Typos and variations**: "Starbucks Coffee" vs "Starbucks"
- ❌ **Franchise locations**: Multiple "McDonald's" at different locations

### Benefits of Coordinate-Based Constraints:
- ✅ **Unique physical locations**: Each lat/lng pair represents one specific location
- ✅ **Language independent**: Coordinates work regardless of language
- ✅ **Precise location matching**: Even if names differ, same coordinates = same place
- ✅ **Handles franchises**: Different McDonald's locations have different coordinates

## Database Schema Changes

### Updated SQL Constraint:
```sql
-- OLD: Name-based constraint (problematic)
ALTER TABLE restaurants ADD CONSTRAINT unique_restaurant_name UNIQUE (name);

-- NEW: Location-based constraint (better)
ALTER TABLE restaurants ADD CONSTRAINT unique_restaurant_location UNIQUE (latitude, longitude);
```

### Benefits:
1. **Prevents duplicate locations** even with different names
2. **Allows same restaurant name** at different locations (franchises)
3. **More reliable duplicate detection** based on physical location
4. **Handles coordinate extraction** - if coordinates are missing, fallback to name check

## Code Changes

### Enhanced Duplicate Detection:
```python
def check_restaurant_exists(self, name: str, address: str = None, latitude: float = None, longitude: float = None) -> bool:
    # First try to check by coordinates (most reliable)
    if latitude is not None and longitude is not None:
        query = self.supabase.table('restaurants').select('id').eq('latitude', latitude).eq('longitude', longitude)
        result = query.limit(1).execute()
        if len(result.data) > 0:
            return True
    
    # Fallback to name and address check
    # ... rest of the logic
```

### Improved Logging:
```python
self.logger.info(f"Skipping duplicate: {restaurant.name} at ({restaurant.latitude}, {restaurant.longitude})")
```

## Usage Instructions

### 1. Update Database Schema
Run this SQL in your Supabase SQL Editor:
```sql
-- Remove old constraint if it exists
ALTER TABLE restaurants DROP CONSTRAINT IF EXISTS unique_restaurant_name;

-- Add new coordinate-based constraint
ALTER TABLE restaurants ADD CONSTRAINT unique_restaurant_location UNIQUE (latitude, longitude);
```

### 2. Clean Up Existing Duplicates (Optional)
```sql
-- Remove duplicate locations, keeping only the first occurrence
DELETE FROM restaurants 
WHERE id NOT IN (
    SELECT MIN(id) 
    FROM restaurants 
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    GROUP BY latitude, longitude
);
```

### 3. Test the New Constraint
```bash
python test_coordinates_and_duplicates.py
```

## Expected Behavior

### ✅ **Will Allow:**
- Same restaurant name at different locations (franchises)
- Different names at the same location (if coordinates are missing)

### ❌ **Will Prevent:**
- Same coordinates being inserted twice
- Duplicate physical locations

### 🔄 **Fallback Logic:**
1. **Primary**: Check by coordinates (latitude, longitude)
2. **Fallback**: Check by name and address (if coordinates missing)
3. **Error Handling**: Graceful handling of constraint violations

## Monitoring

The enhanced logging will show:
- Coordinate-based duplicate detection
- Fallback to name-based detection when coordinates are missing
- Clear indication of why duplicates were skipped

## Benefits Summary

1. **More Accurate**: Physical location is more reliable than name matching
2. **Handles Franchises**: Multiple locations of same restaurant chain
3. **Language Independent**: Works with any language restaurant names
4. **Precise Matching**: Exact coordinate matching prevents false positives
5. **Robust Fallback**: Still works when coordinates are missing
