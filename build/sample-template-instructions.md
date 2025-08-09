# Sample Participants Excel Template

This directory contains sample Excel templates for bulk uploading participants.

## Template Format

The Excel file should contain the following columns:

### Required Columns:
- **name**: Full name of the participant
- **email**: Email address of the participant

### Optional Columns:
- **organization**: Organization/Institution name
- **position**: Job title or position
- **role**: Participant role (affects certificate type)

### Role Values for Certificate Types:
- **For Participation Certificate**: Leave role empty or use "participant", "attendee"
- **For Service Certificate**: Use "volunteer", "organizer", "staff", "committee", "organizing committee"

## Sample Data Format:

| name | email | organization | position | role |
|------|-------|--------------|----------|------|
| John Doe | john.doe@example.com | ABC Company | Manager | participant |
| Jane Smith | jane.smith@example.com | XYZ Organization | Coordinator | volunteer |
| Dr. Robert Johnson | robert.j@university.edu | State University | Professor | committee |

## Instructions:
1. Create an Excel file (.xlsx or .xls) with the columns above
2. Fill in the participant data
3. Upload using the "Bulk Upload" tab in the application
4. Review the upload results and send certificates
