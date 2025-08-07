<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# MDCAN BDM 2025 Certificate Generation Platform

This is a full-stack certificate generation platform for the MDCAN BDM 14th - 2025 conference.

## Project Structure
- Frontend: React.js application for participant management and certificate preview
- Backend: Python Flask API for certificate generation and email delivery
- Database: PostgreSQL for storing participant information
- Deployment: Configured for Vercel

## Key Components
- Certificate generation using HTML-to-PDF conversion
- Email integration for automatic certificate delivery  
- Participant management system
- Digital signature integration

## Development Guidelines
- Use JavaScript (not TypeScript) for React components
- Follow React functional component patterns with hooks
- Use Flask best practices for API development
- Ensure proper error handling for email and PDF generation
- Maintain responsive design for the frontend
- Include proper validation for form inputs

## Certificate Format
The platform supports two types of certificates:

### Certificate of Participation
- Title: "CERTIFICATE OF PARTICIPATION"
- For conference attendees
- Text: "This is to certify that [Name] participated in the MDCAN BDM 14th – 2025 held in Enugu on 1st – 6th September, 2025"

### Acknowledgement of Service
- Title: "ACKNOWLEDGEMENT OF SERVICE"  
- For volunteers, organizers, and staff
- Text: "This is to acknowledge and appreciate the exceptional service of [Name] towards the successful hosting of the MDCAN BDM 14th – 2025 on 1st – 6th September 2025"

Both certificates include signatures of Prof. Aminu Mohammed (MDCAN President) and Prof. Appolos Ndukuba (LOC Chairman)
