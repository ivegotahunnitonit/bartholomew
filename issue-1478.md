## Update: Auto token refresh & persistence (2026-07-17)

Added automatic token renewal when expired/invalid, and persistence to  files.

### What was broken
When a Hermes profile started after being idle (e.g. MacBook off overnight), the stored session token was already expired. The plugin would:
1. Call  which calls 
2. Get back an expired/invalid token from the API
3. Back off for 60 seconds (_ACTIVATION_RETRY_COOLDOWN)
4. Block ALL subsequent API calls until the cooldown expired — effectively freezing the profile

### What was fixed in  (_MemantoClient class)

#### 1. New methods for token persistence
-  — set profile path for token persistence
-  — save session_token to 
-  — load existing token (future use)

#### 2.  updated
- After successful , saves the new token to 
- On  or , retries activation (auto-refresh)
- No more 60-second freeze after expiration

#### 3.  method added
- Tries to activate agent again on token expiration
- Persists the new token to file
- Only runs once per cooldown period

#### 4.  updated
- Passes  to client via 
- So token persistence works automatically

### Result
- Tokens are now saved to  after every successful activation
- Auto-refresh on expiration — no more profile freeze
- Works correctly after MacBook sleeps, cron refresh, etc.
- Token is persisted across sessions

### Files changed
- 
  - Added , , , 
  - Updated  with auto-refresh on expired/invalid tokens
  - Updated  to pass profile dir to client

### Testing
- Verified on profiles: main, server-admin, llm, caraudio, delegate, wrighter, anna-corestone
- All 7 profiles activate correctly after Macbook restart
- Cron job refreshes tokens correctly (script already updated to save tokens)
