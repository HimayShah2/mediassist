# MediAssist Pro — Setup & Deployment Guide

This guide details how to configure MediAssist Pro for your clinic.

## 1. Initial Requirements
- **Hardware:** Windows 10/11, 8GB RAM minimum.
- **AI Access:** You need at least one API key from a supported provider:
  - **NVIDIA NIM** (Recommended for clinical reasoning)
  - **OpenAI** (GPT-4o)
  - **Anthropic** (Claude 3.5 Sonnet)
  - **Google Gemini**
  - **DeepSeek**

## 2. The Setup Wizard
When you launch the app for the first time:
1. Navigate to **Settings** (Requires Admin login).
2. **Key Selector:** Choose your provider and enter your API keys.
3. **Capacity:** Use the selector to define how many keys you are using (1 to 100).
4. **Rate Limiting:** The system automatically calculates a cooldown window: 
   `Wait Time = (60 / Keys) + 1 second` to prevent API blocks.

## 3. RAG Knowledge Base Setup
To give the AI medical knowledge:
1. Go to the **Document Library (RAG)** tab.
2. Upload your clinic's guidelines (PDF/DOCX).
3. Select the appropriate **Clinical Domain** for each document.
4. (Optional) Add **Trusted URLs** (e.g., `who.int`) in the settings for web search fallbacks.

## 4. Security & HIPAA
- **Database:** All patient data is stored in `mediassist.db` with AES-256 field-level encryption.
- **Backups:** Ensure you regularly copy the `mediassist.db` file to a secure, encrypted offline drive.
- **PII:** Never share your encryption keys; without them, the database cannot be read.
