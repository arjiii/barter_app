# Profile Update Fix

## Problem Found
The profile page is calling `authService.updateProfile()` with 4 parameters (name, location, latitude, longitude), but the method only accepts 2 parameters (name, location).

## Fix Required

### File: `Frontend/src/lib/services/authService.ts`

**Find this method (around line 232):**
```typescript
async updateProfile(name: string, location?: string): Promise<User | null> {
    try {
        const token = this.getToken();
        if (!token || this.isUuidToken(token)) return null; // UUID tokens are for offline mode only
        const res = await fetch(`${API_BASE_URL}/auth/profile`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
            body: JSON.stringify({ name, location: location || '' })
        });
        if (!res.ok) return null;
        const apiUser = await res.json();
        const user: User = {
            id: apiUser.id,
            email: apiUser.email,
            name: apiUser.name,
            isVerified: true,
            role: 'user',
            createdAt: new Date(),
            lastLoginAt: new Date(),
            location: apiUser.location || undefined,
        };
        return user;
    } catch (e) {
        console.error('Update profile error:', e);
        return null;
    }
}
```

**Replace it with:**
```typescript
async updateProfile(name: string, location?: string, latitude?: number, longitude?: number): Promise<User | null> {
    try {
        const token = this.getToken();
        if (!token || this.isUuidToken(token)) return null; // UUID tokens are for offline mode only
        
        const payload: any = { name, location: location || '' };
        if (latitude !== undefined) payload.latitude = latitude;
        if (longitude !== undefined) payload.longitude = longitude;
        
        const res = await fetch(`${API_BASE_URL}/auth/profile`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
            body: JSON.stringify(payload)
        });
        if (!res.ok) return null;
        const apiUser = await res.json();
        const user: User = {
            id: apiUser.id,
            email: apiUser.email,
            name: apiUser.name,
            isVerified: true,
            role: 'user',
            createdAt: new Date(),
            lastLoginAt: new Date(),
            location: apiUser.location || undefined,
            latitude: apiUser.latitude,
            longitude: apiUser.longitude
        };
        return user;
    } catch (e) {
        console.error('Update profile error:', e);
        return null;
    }
}
```

## What This Fixes
1. ✅ Accepts latitude and longitude parameters
2. ✅ Sends coordinates to the backend (which already supports them)
3. ✅ Returns the coordinates in the User object
4. ✅ Matches the profile page's call signature

## Backend Status
✅ The backend `/auth/profile` endpoint has already been updated to accept and return latitude/longitude coordinates.

## After Applying This Fix
The "Locate Me" button on the profile page will successfully save your location coordinates to the database.
