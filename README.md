# Autonomous Instagram Physics Reel Pipeline

An end-to-end, zero-cost automated content engine that procedurally generates 2D physics maze simulations, synthesizes context-aware captions via the Google GenAI SDK, stages media to cloud storage, and publishes directly to Instagram Reels on a daily schedule.

---

## Key Features

* **Procedural Physics Engine:** Headless 2D dynamic simulations built using `pymunk` and rendered frame-by-frame with `pygame`.
* **Algorithmic Validation:** Simulates trials headlessly in memory to guarantee each procedural seed produces a solvable, engaging maze path before rendering.
* **AI Caption Generation:** Leverages Google's `gemini-3.6-flash` via the `google-genai` SDK to dynamically create engaging hooks and contextual hashtags.
* **Automated Cloud Staging:** Direct-to-cloud MP4 staging using Cloudinary's media API.
* **Meta Graph API Publishing:** Two-step media containerization and automated status polling (`IN_PROGRESS` $\rightarrow$ `FINISHED`) to reliably publish to Instagram Reels without manual intervention.
* **Zero-Touch Automation:** Scheduled via Windows Task Scheduler to run autonomously at 5:55 PM daily.

---

## 🛠️ Architecture & Tech Stack

[ Pygame / Pymunk Simulation ] ──> [ MoviePy Rendering (MP4) ]
│
┌──────────────────────────────────────┴──────────────────────────────────────┐
▼                                                                             ▼
[ Cloudinary API ] (Staging)                                           [ Google GenAI SDK ] (Captions)
│                                                                             │
└──────────────────────────────────────┬──────────────────────────────────────┘
▼
[ Instagram Graph API ]
(Media Container -> Publish Reel)

* **Language:** Python 3
* **Physics & Graphics:** `pymunk`, `pygame`, `numpy`
* **Video Compilation:** `moviepy`
* **Cloud & APIs:** `google-genai`, `cloudinary`, `requests` (Meta Graph API v19.0+)
* **Environment Security:** `python-dotenv`

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone [https://github.com/ttahvvs/autonomous-physics-reels.git](https://github.com/ttahvvs/autonomous-physics-reels.git)
cd autonomous-physics-reels

### 2. Install Dependencies

pip install pygame pymunk moviepy numpy google-genai cloudinary python-dotenv requests

GEMINI_API_KEY=your_gemini_api_key
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
META_IG_USER_ID=your_instagram_user_id
META_ACCESS_TOKEN=your_meta_long_lived_token

python generate_reel.py

---

### Step 3: Publish to GitHub via VS Code

1. Click on the **Source Control** tab on the left sidebar of VS Code (or press `Ctrl + Shift + G`).
2. Verify that **`.env`** and **`final_reel_silent.mp4`** are **NOT** listed in the changes list (this confirms `.gitignore` is working).
3. If you haven't initialized the repository yet, click **Initialize Repository**.
4. In the "Message" input field, type:
   ```text
   feat: autonomous physics simulation and instagram reels publishing pipeline