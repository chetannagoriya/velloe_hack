# ⏱️ Screen Time Tracker - Implementation Guide

## Overview
Complete screen time tracking system for CalmNest that monitors user activity and displays daily/weekly usage statistics.

---

## ✅ Features Implemented

### 1. **Automatic Time Tracking**
- Tracks active time when user is using the website
- Detects inactivity (30 seconds threshold)
- Pauses when tab is hidden or switched
- Resumes when user returns

### 2. **Smart Activity Detection**
- Mouse movements
- Keyboard input
- Scrolling
- Touch events
- Clicks

### 3. **Data Storage**
- **Client-side**: localStorage for instant access
- **Server-sid