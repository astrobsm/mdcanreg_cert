# Bulk Upload and Certificate Background Features

## New Features Added

### 1. Certificate Background Image Support
- Certificates now support a background image for enhanced visual appeal
- Place your background image as `certificate_background.png` or `certificate_background.jpg` in the `public` directory
- The background will be automatically applied to both certificate types
- Background image should be A4 ratio (recommended: 2480x3508 pixels at 300 DPI)

### 2. Excel Bulk Upload System
- Upload multiple participants at once using Excel files (.xlsx or .xls)
- Automatically determines certificate type based on participant role
- Comprehensive error reporting and validation

### 3. Bulk Certificate Generation and Email Sending
- Send certificates to all participants with pending status in one click
- Background processing for large batches
- Detailed success/failure reporting

## Excel File Format

### Required Columns:
- `name`: Participant's full name
- `email`: Valid email address

### Optional Columns:
- `organization`: Company/institution name
- `position`: Job title or role
- `role`: Determines certificate type

### Certificate Type Assignment:
- **Service Certificate**: role contains "volunteer", "organizer", "staff", "committee"
- **Participation Certificate**: All other cases

## Email Configuration

The system is configured to send emails from `sylvia4douglas@gmail.com`. To set up email delivery:

1. Create a `.env` file in the `backend` directory
2. Add the following configuration:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=sylvia4douglas@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=MDCAN BDM 2025 <sylvia4douglas@gmail.com>
```

**Important**: Use an App Password, not your regular Gmail password for security.

## Usage Instructions

### Single Participant Upload:
1. Use the "Add Participant" tab for individual entries
2. Select certificate type manually
3. Send certificate immediately or later

### Bulk Upload Process:
1. Prepare Excel file with participant data
2. Navigate to "Bulk Upload" tab
3. Select and upload your Excel file
4. Review upload results and error reports
5. Use "Send All Certificates" to email all participants

### Certificate Management:
1. View all participants in "Participants List" tab
2. Send individual certificates as needed
3. Track certificate status (pending/sent)
4. Bulk send remaining certificates

## File Requirements

### Background Image:
- File: `public/certificate_background.png` (or .jpg)
- Resolution: 300 DPI minimum
- Size: A4 ratio (2480x3508 pixels recommended)
- Format: PNG (with transparency) or JPG

### Logo Files:
- MDCAN Logo: `public/mdcan-logo.png`
- Coal City Logo: `public/coalcity-logo.png`
- President Signature: `public/president-signature.png`
- Chairman Signature: `public/chairman-signature.png`

All images should be high resolution (300 DPI) for print quality.

## Error Handling

### Common Upload Errors:
- Missing required columns (name, email)
- Invalid email format
- Duplicate email addresses
- Empty rows or invalid data

### Solution:
- Check Excel file format against template
- Ensure all required fields are filled
- Remove duplicate entries
- Validate email addresses

## Technical Notes

### Backend Dependencies:
- pandas: Excel file processing
- openpyxl: Excel file reading
- Updated Flask routes for bulk operations

### Frontend Features:
- New BulkUpload component
- Enhanced UI with progress indicators
- Detailed error reporting
- File validation

### Performance:
- Efficient batch processing
- Background email sending
- Memory-optimized Excel reading
- Proper error recovery

## Security Considerations

1. File upload validation (only Excel files accepted)
2. Secure filename handling
3. Temporary file cleanup
4. Email authentication with App Passwords
5. Input sanitization for all data fields

## Troubleshooting

### Upload Issues:
- Ensure file is .xlsx or .xls format
- Check file permissions
- Verify column names match requirements

### Email Delivery:
- Configure App Password in Gmail
- Check SMTP settings
- Verify email addresses are valid
- Monitor email quota limits

### Certificate Generation:
- Ensure background image is properly sized
- Check logo file paths
- Verify PDF generation dependencies

For technical support, check the application logs and ensure all dependencies are properly installed.
