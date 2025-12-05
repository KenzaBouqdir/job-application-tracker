#!/usr/bin/env python3
"""
Job Application Tracker - Gmail Analyzer with Visualizations
Tracks job applications from Gmail and generates insights with charts
Author: Kenza Bouqdir
"""

import os
import pickle
import base64
import re
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Set style for professional-looking charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class JobApplicationTracker:
    def __init__(self):
        self.service = None
        self.applications = []
        
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Successfully authenticated with Gmail\n")
    
    def search_emails(self, query, max_results=200):
        """Search Gmail for emails matching query"""
        try:
            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()
            return results.get('messages', [])
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def get_email_details(self, msg_id):
        """Get full email details"""
        try:
            return self.service.users().messages().get(
                userId='me', id=msg_id, format='full'
            ).execute()
        except:
            return None
    
    def is_job_alert(self, email_from, subject):
        """Filter out job alerts and newsletters"""
        spam_indicators = [
            'linkedin.com', 'indeed.com', 'glassdoor.com', 'monster.com',
            'jobrapido', 'jooble', 'jobtome', 'talent.com', 'simplyhired',
            'ziprecruiter', 'newsletter', 'job alert', 'new jobs',
            'recommended for you', 'jobs matching', 'daily digest'
        ]
        combined = (email_from + " " + subject).lower()
        return any(indicator in combined for indicator in spam_indicators)
    
    def extract_company(self, email_from, subject):
        """Extract company name from email"""
        # Try email domain
        match = re.search(r'@([\w-]+)\.(com|io|ai|co)', email_from.lower())
        if match:
            company = match.group(1)
            # Remove common recruiting platforms
            company = company.replace('greenhouse', '').replace('lever', '').replace('workday', '').replace('myworkday', '')
            if company and len(company) > 2:
                return company.title()
        
        # Try subject line
        match = re.search(r'at\s+([\w\s]+?)(?:\s*[-–|]|$)', subject)
        if match:
            return match.group(1).strip().title()
        
        return "Unknown"
    
    def categorize_status(self, subject, body):
        """Categorize email status"""
        s = subject.lower()
        b = (body[:500] if body else "").lower()
        combined = s + " " + b
        
        # Define keywords
        rejection_kw = ['not selected', 'unfortunately', 'other candidates', 
                       'position filled', 'not moving forward', 'pursue other',
                       'not be considered']
        assessment_kw = ['codesignal', 'hackerrank', 'coding challenge', 
                        'assessment', 'technical test']
        interview_kw = ['interview', 'schedule', 'meet with', 'phone screen',
                       'video call', 'would like to speak']
        applied_kw = ['application received', 'thank you for applying',
                     'confirm your application', 'submitted successfully']
        
        # Categorize
        if any(kw in combined for kw in rejection_kw):
            return 'Rejected'
        elif any(kw in combined for kw in assessment_kw):
            return 'Assessment'
        elif any(kw in combined for kw in interview_kw):
            return 'Interview'
        elif any(kw in combined for kw in applied_kw):
            return 'Applied'
        return 'Other'
    
    def extract_role(self, subject, body):
        """Extract job role from email"""
        patterns = [
            r'(?:for\s+|role:\s*|position:\s*)([\w\s]{5,40}?)(?:\s+at|\s*[-–|]|$)',
            r'(software engineer|data engineer|ml engineer|machine learning|data scientist|backend|frontend|full.stack)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()
            if body:
                match = re.search(pattern, body[:200], re.IGNORECASE)
                if match:
                    return match.group(1).strip().title()
        return "Unknown"
    
    def analyze_applications(self, months=6):
        """Analyze job applications from Gmail"""
        print(f"🔍 Searching for job applications (last {months} months)...\n")
        
        # Date filter
        cutoff_date = (datetime.now() - timedelta(days=30*months)).strftime('%Y/%m/%d')
        
        # Search queries
        queries = [
            f'after:{cutoff_date} ("application received" OR "thank you for applying")',
            f'after:{cutoff_date} ("not selected" OR "unfortunately" OR "other candidates")',
            f'after:{cutoff_date} (interview OR "schedule a call" OR assessment)',
            f'after:{cutoff_date} (codesignal OR hackerrank)',
        ]
        
        # Collect email IDs
        all_ids = set()
        for query in queries:
            msgs = self.search_emails(query)
            print(f"  Found {len(msgs)} emails")
            all_ids.update(msg['id'] for msg in msgs)
        
        print(f"\n📧 Total emails found: {len(all_ids)}")
        print("📥 Processing emails...\n")
        
        # Process each email
        for idx, msg_id in enumerate(all_ids, 1):
            if idx % 10 == 0:
                print(f"  Processed {idx}/{len(all_ids)}...")
            
            email = self.get_email_details(msg_id)
            if not email:
                continue
            
            # Extract headers
            headers = {h['name']: h['value'] for h in email['payload']['headers']}
            subject = headers.get('Subject', '')
            email_from = headers.get('From', '')
            
            # Skip job alerts
            if self.is_job_alert(email_from, subject):
                continue
            
            # Extract body
            body = ""
            try:
                if 'parts' in email['payload']:
                    for part in email['payload']['parts']:
                        if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                            break
                elif 'body' in email['payload'] and 'data' in email['payload']['body']:
                    body = base64.urlsafe_b64decode(email['payload']['body']['data']).decode('utf-8', errors='ignore')
            except:
                pass
            
            # Extract date
            date_ms = email['internalDate']
            date = datetime.fromtimestamp(int(date_ms)/1000)
            
            # Store application data
            self.applications.append({
                'Date': date,
                'Company': self.extract_company(email_from, subject),
                'Role': self.extract_role(subject, body),
                'Status': self.categorize_status(subject, body),
                'Subject': subject
            })
        
        print(f"\n✅ Found {len(self.applications)} actual applications\n")
    
    def generate_visualizations(self, df):
        """Generate charts and save as PNG files"""
        if df.empty:
            print("⚠️ No data to visualize")
            return
        
        print("📊 Generating visualizations...\n")
        
        # Create output directory
        os.makedirs('output', exist_ok=True)
        
        # 1. Status Distribution Pie Chart
        fig, ax = plt.subplots(figsize=(10, 8))
        status_counts = df['Status'].value_counts()
        colors = sns.color_palette('Set2', len(status_counts))
        
        wedges, texts, autotexts = ax.pie(
            status_counts.values,
            labels=status_counts.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_weight('bold')
        
        ax.set_title('Application Status Distribution', fontsize=16, weight='bold', pad=20)
        plt.tight_layout()
        plt.savefig('output/status_distribution.png', dpi=300, bbox_inches='tight')
        print("  ✓ Saved: status_distribution.png")
        plt.close()
        
        # 2. Applications Over Time
        fig, ax = plt.subplots(figsize=(14, 6))
        df_sorted = df.sort_values('Date')
        df_sorted['Week'] = df_sorted['Date'].dt.to_period('W')
        weekly_apps = df_sorted.groupby('Week').size()
        
        x = range(len(weekly_apps))
        ax.bar(x, weekly_apps.values, color='#3498db', alpha=0.7, edgecolor='black')
        ax.set_xlabel('Week', fontsize=12, weight='bold')
        ax.set_ylabel('Number of Applications', fontsize=12, weight='bold')
        ax.set_title('Application Activity Over Time', fontsize=16, weight='bold', pad=20)
        ax.set_xticks(x[::2])  # Show every other week
        ax.set_xticklabels([str(w) for w in weekly_apps.index[::2]], rotation=45)
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig('output/timeline.png', dpi=300, bbox_inches='tight')
        print("  ✓ Saved: timeline.png")
        plt.close()
        
        # 3. Top Companies Bar Chart
        fig, ax = plt.subplots(figsize=(12, 8))
        company_counts = df['Company'].value_counts().head(10)
        
        y_pos = range(len(company_counts))
        ax.barh(y_pos, company_counts.values, color='#2ecc71', edgecolor='black')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(company_counts.index)
        ax.set_xlabel('Number of Applications', fontsize=12, weight='bold')
        ax.set_title('Top 10 Companies Applied To', fontsize=16, weight='bold', pad=20)
        ax.invert_yaxis()
        
        # Add value labels
        for i, v in enumerate(company_counts.values):
            ax.text(v + 0.1, i, str(v), va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('output/top_companies.png', dpi=300, bbox_inches='tight')
        print("  ✓ Saved: top_companies.png")
        plt.close()
        
        # 4. Status by Month Heatmap
        fig, ax = plt.subplots(figsize=(14, 6))
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_status = pd.crosstab(df['Month'], df['Status'])
        
        sns.heatmap(monthly_status.T, annot=True, fmt='d', cmap='YlGnBu',
                   cbar_kws={'label': 'Count'}, ax=ax, linewidths=0.5)
        ax.set_title('Application Status by Month', fontsize=16, weight='bold', pad=20)
        ax.set_xlabel('Month', fontsize=12, weight='bold')
        ax.set_ylabel('Status', fontsize=12, weight='bold')
        plt.tight_layout()
        plt.savefig('output/monthly_heatmap.png', dpi=300, bbox_inches='tight')
        print("  ✓ Saved: monthly_heatmap.png")
        plt.close()
        
        print("\n✅ All visualizations saved to 'output/' directory\n")
    
    def generate_report(self):
        """Generate text report and CSV"""
        if not self.applications:
            print("❌ No applications found\n")
            return None
        
        df = pd.DataFrame(self.applications)
        df = df.sort_values('Date', ascending=False)
        
        # Save CSV
        filename = f'output/applications_{datetime.now().strftime("%Y%m%d")}.csv'
        df.to_csv(filename, index=False)
        
        # Print report
        print("=" * 70)
        print("📊 JOB APPLICATION ANALYSIS REPORT")
        print("=" * 70)
        
        print(f"\n📅 Date Range: {df['Date'].min().date()} to {df['Date'].max().date()}")
        print(f"📧 Total Applications: {len(df)}")
        
        print("\n🏢 STATUS BREAKDOWN:")
        for status, count in df['Status'].value_counts().items():
            pct = (count / len(df)) * 100
            print(f"   {status:15s}: {count:3d} ({pct:5.1f}%)")
        
        print("\n🏆 TOP COMPANIES:")
        for company, count in df['Company'].value_counts().head(10).items():
            print(f"   {company:30s}: {count:2d}")
        
        print("\n💼 TOP ROLES:")
        for role, count in df['Role'].value_counts().head(5).items():
            print(f"   {role:40s}: {count:2d}")
        
        # Conversion metrics
        applied = df[df['Status'] == 'Applied'].shape[0]
        rejected = df[df['Status'] == 'Rejected'].shape[0]
        interview = df[df['Status'].isin(['Interview', 'Assessment'])].shape[0]
        
        if applied > 0:
            print(f"\n📊 KEY METRICS:")
            print(f"   Applications Sent: {applied}")
            print(f"   Rejections: {rejected} ({(rejected/applied)*100:.1f}%)")
            print(f"   Interviews/Assessments: {interview} ({(interview/applied)*100:.1f}%)")
            
            if interview > 0:
                print(f"   Interview Rate: {(interview/len(df))*100:.1f}%")
        
        print(f"\n💾 Data saved to: {filename}")
        print("📊 Visualizations saved to: output/ directory")
        print("=" * 70 + "\n")
        
        return df

def main():
    """Main execution"""
    print("=" * 70)
    print("   📧 JOB APPLICATION TRACKER")
    print("   Gmail Analyzer with Visualizations")
    print("=" * 70 + "\n")
    
    tracker = JobApplicationTracker()
    
    try:
        # Authenticate and analyze
        tracker.authenticate()
        tracker.analyze_applications(months=6)
        
        # Generate report and visualizations
        df = tracker.generate_report()
        if df is not None and not df.empty:
            tracker.generate_visualizations(df)
            
            print("✅ Analysis complete!")
            print("\nFiles generated:")
            print("  📄 applications_YYYYMMDD.csv - Raw data")
            print("  📊 status_distribution.png - Status pie chart")
            print("  📈 timeline.png - Applications over time")
            print("  🏢 top_companies.png - Top companies bar chart")
            print("  🔥 monthly_heatmap.png - Status by month heatmap")
            print("\n💡 Tip: Include these visualizations in your job search tracker!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  1. credentials.json in current directory")
        print("  2. Required packages installed")

if __name__ == "__main__":
    main()