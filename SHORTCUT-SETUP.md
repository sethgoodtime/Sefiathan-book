# iPhone Shortcut Setup

Two shortcuts make the loop work. Shortcut #1 screenshots Co-Star and uploads it. Shortcut #2 fires when the entry is ready and sends it as an iMessage.

---

## Prerequisites

- Install the **ntfy** app from the App Store
- Open ntfy → Subscribe → Topic: `sefiathan-book`
- Have your GitHub personal access token ready (the fine-grained one for Sefiathan-book)

---

## Shortcut #1: "Sefiathan Capture"

This runs daily on a schedule. It opens Co-Star, takes a screenshot, and uploads it to GitHub.

### Build the Shortcut

Open the **Shortcuts** app → tap **+** → name it **Sefiathan Capture**.

Add these actions in order:

1. **Open App**
   - App: Co-Star

2. **Wait**
   - Duration: 4 seconds

3. **Take Screenshot**

4. **Get Current Date**
   - Format: Custom → `yyyy-MM-dd`
   - Save to variable: `today`

5. **Base64 Encode**
   - Input: Screenshot (from step 3)

6. **Get Contents of URL**
   - URL: `https://api.github.com/repos/sethgoodtime/Sefiathan-book/contents/screenshots/[today].png`
     - (Use the `today` variable in the URL — tap and insert the variable between `screenshots/` and `.png`)
   - Method: **PUT**
   - Headers:
     - `Authorization`: `Bearer YOUR_GITHUB_TOKEN`
     - `Accept`: `application/vnd.github.v3+json`
   - Request Body: **JSON**
     - `message`: `Add Co-Star screenshot for [today]`
     - `content`: (the Base64 Encode result from step 5)

### Automate It

1. Go to the **Automation** tab in Shortcuts
2. Tap **+** → **Time of Day**
3. Pick your daily time (e.g., 8:00 AM — make sure Co-Star has had time to update)
4. Action: **Run Shortcut** → select **Sefiathan Capture**
5. Turn OFF "Ask Before Running"

---

## Shortcut #2: "Sefiathan Send"

This fires when ntfy delivers the "entry ready" notification, pulls the entry from GitHub, and sends it as an iMessage.

### Build the Shortcut

Open the **Shortcuts** app → tap **+** → name it **Sefiathan Send**.

Add these actions in order:

1. **Get Current Date**
   - Format: Custom → `yyyy-MM-dd`
   - Save to variable: `today`

2. **Get Contents of URL**
   - URL: `https://api.github.com/repos/sethgoodtime/Sefiathan-book/contents/chapters/[today].md`
     - (Insert the `today` variable)
   - Method: **GET**
   - Headers:
     - `Authorization`: `Bearer YOUR_GITHUB_TOKEN`
     - `Accept`: `application/vnd.github.v3+json`

3. **Get Dictionary Value**
   - Key: `content`
   - (This returns the file content as base64)

4. **Base64 Decode**
   - Input: result from step 3

5. **Send Message**
   - Message: (the decoded text from step 4)
   - To: the recipient's contact
   - (During testing, add yourself and the other tester)

### Automate It

1. Go to the **Automation** tab in Shortcuts
2. Tap **+** → **App** → select **ntfy**
3. Trigger: **Notification** — when ntfy sends any notification
4. Action: **Run Shortcut** → select **Sefiathan Send**
5. Turn OFF "Ask Before Running"

**Alternative automation trigger**: If the ntfy notification trigger is unreliable, you can instead set this as a **Time of Day** automation — schedule it ~15 minutes after Shortcut #1. The GitHub Action typically completes in 1-3 minutes, so 15 minutes gives plenty of buffer.

---

## Testing

### Test Shortcut #1 manually:
1. Run **Sefiathan Capture** by tapping it
2. Check GitHub: go to `sethgoodtime/Sefiathan-book` → `screenshots/` folder
3. You should see today's screenshot

### Test the full loop:
1. The screenshot upload triggers the GitHub Action automatically
2. Go to `sethgoodtime/Sefiathan-book` → Actions tab → watch "Process Daily Sefiathan" run
3. Once it completes, check `chapters/` for today's entry
4. You should get an ntfy notification
5. Shortcut #2 should fire and send the iMessage

### If something breaks:
- **Screenshot didn't upload**: Check your GitHub token is correct and has Contents write permission
- **Action didn't trigger**: Check the Actions tab for errors — most likely the ANTHROPIC_API_KEY secret
- **No ntfy notification**: Make sure you're subscribed to the `sefiathan-book` topic in the ntfy app
- **iMessage didn't send**: Run Shortcut #2 manually to test it in isolation

---

## Testing vs Production

**Testing (2 recipients):**
- In Shortcut #2, set the "Send Message" to both yourself and the other tester

**Production (1 recipient):**
- Change "Send Message" to just the final recipient
