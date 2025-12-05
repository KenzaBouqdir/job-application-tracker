# 📧 Job Application Tracker

> A Python tool that analyzes your Gmail to track job applications, rejections, and interviews with beautiful visualizations

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 🎯 Overview

Job hunting is hard enough without losing track of where you've applied. This tool automatically scans your Gmail, extracts job application emails, and generates insightful visualizations to help you optimize your job search strategy.

**Built with:** Python, Gmail API, Pandas, Matplotlib, Seaborn

## ✨ Features

- 📊 **Automatic email analysis** - Scans Gmail for job applications, rejections, and interview invitations
- 🎨 **Beautiful visualizations** - Generates 4 professional charts to visualize your job search
- 📈 **Timeline tracking** - See your application activity over time
- 🏢 **Company insights** - Identify which companies you've applied to most
- 📉 **Conversion metrics** - Calculate response rates and interview conversion
- 🚫 **Smart filtering** - Automatically excludes job alerts and newsletters (LinkedIn, Indeed, etc.)
- 💾 **Data export** - Saves results to CSV for further analysis

## 📊 Sample Visualizations

The tool generates four key visualizations:

1. **Status Distribution** - Pie chart showing Applied/Rejected/Interview/Assessment breakdown
2. **Timeline** - Bar chart of application activity week-by-week
3. **Top Companies** - Horizontal bar chart of companies you've applied to most
4. **Monthly Heatmap** - Heatmap showing status distribution by month

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Gmail account
- Google Cloud Console account (free)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/job-application-tracker.git
   cd job-application-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas matplotlib seaborn
   ```

3. **Set up Gmail API**

   a. Go to [Google Cloud Console](https://console.cloud.google.com/)
   
   b. Create a new project
   
   c. Enable Gmail API:
      - Navigate to "APIs & Services" > "Library"
      - Search for "Gmail API"
      - Click "Enable"
   
   d. Create OAuth credentials:
      - Go to "APIs & Services" > "Credentials"
      - Click "Create Credentials" > "OAuth client ID"
      - Configure consent screen (External, add your email as test user)
      - Choose "Desktop app" as application type
      - Download the JSON file
      - Rename it to `credentials.json` and place in project directory

### Usage

```bash
python job_tracker_visual.py
```

On first run:
- A browser window will open for Gmail authentication
- Grant the necessary permissions
- The tool will create a `token.pickle` file for future runs

## 📁 Output Files

The tool creates an `output/` directory containing:

- `applications_YYYYMMDD.csv` - Complete data export
- `status_distribution.png` - Status pie chart
- `timeline.png` - Application timeline
- `top_companies.png` - Top companies bar chart
- `monthly_heatmap.png` - Monthly status heatmap

## 🔧 Configuration

You can modify the analysis timeframe by changing the `months` parameter in `job_tracker_visual.py`:

```python
tracker.analyze_applications(months=6)  # Change to 3, 12, etc.
```

## 📊 Understanding Your Results

### Status Categories

- **Applied** - Application confirmation received
- **Rejected** - Explicit rejection email
- **Interview** - Interview invitation or scheduling
- **Assessment** - Coding challenge or technical assessment
- **Other** - Unclear or promotional emails

### Key Metrics

- **Response Rate** - (Rejections + Interviews) / Total Applications
- **Interview Rate** - Interviews / Total Applications
- **Rejection Rate** - Rejections / Total Applications

### Red Flags to Watch For

🚩 **Response rate < 10%** - Your CV might not be passing ATS filters
🚩 **0% interview rate with 20+ applications** - Qualification mismatch or targeting wrong roles
🚩 **High "Other" category** - Email categorization might need tuning

## 🛠️ Technical Details

### How It Works

1. **Authentication** - Uses OAuth 2.0 to securely access your Gmail (read-only)
2. **Email Search** - Queries Gmail for job-related keywords in the last 6 months
3. **Smart Filtering** - Removes job alerts from LinkedIn, Indeed, Glassdoor, etc.
4. **Data Extraction** - Parses company names, roles, and status from email content
5. **Categorization** - Uses keyword matching to classify email status
6. **Visualization** - Generates professional charts with Matplotlib and Seaborn

### Privacy & Security

- ✅ **Read-only access** - Can't send, delete, or modify emails
- ✅ **Local processing** - All data stays on your machine
- ✅ **OAuth 2.0** - Industry-standard secure authentication
- ✅ **No data collection** - Tool doesn't send data anywhere

## 🤝 Contributing

Contributions are welcome! Here are some ideas:

- Add support for other email providers (Outlook, Yahoo)
- Improve company name extraction
- Add sentiment analysis for rejection emails
- Create a web dashboard interface
- Add email templates for follow-ups

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Kenza Bouqdir**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

## 🙏 Acknowledgments

- Google Gmail API documentation
- Python data visualization community
- Everyone struggling with job hunting (you're not alone!)

## 📈 Roadmap

- [ ] Web dashboard with Flask
- [ ] Email follow-up reminders
- [ ] Integration with job boards
- [ ] Mobile app version
- [ ] Machine learning for status prediction

## ⭐ Star This Repo!

If this tool helped you track your job applications, please consider giving it a star! It helps others discover the project.

---

**Built with ❤️ by a fellow job seeker**

*Remember: Job hunting is a numbers game. Track your progress, stay consistent, and you will succeed!*