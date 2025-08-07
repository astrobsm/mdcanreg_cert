# Certificate Format Specifications

This document defines the format and content for the MDCAN BDM 14th - 2025 certificates.

## Certificate Types

### 1. Certificate of Participation
For conference attendees who participated in the event.

### 2. Acknowledgement of Service
For volunteers, organizers, and staff who contributed to the success of the conference.

## Certificate Layouts

### Certificate of Participation

#### Title
- **Text**: "CERTIFICATE OF PARTICIPATION"
- **Font**: Times New Roman, Bold
- **Size**: 36px
- **Color**: #2c3e50 (dark blue)
- **Alignment**: Center
- **Letter Spacing**: 3px

#### Content
- **Opening Text**: "This is to certify that"
- **Participant Name**: Dynamic field, bold, underlined, 32px, #e74c3c (red)
- **Middle Text**: "participated in the"
- **Event Name**: "MDCAN BDM 14th – 2025" (28px, bold, #2c3e50)
- **Closing Text**: "held in Enugu on 1st – 6th September, 2025"

### Acknowledgement of Service

#### Title
- **Text**: "ACKNOWLEDGEMENT OF SERVICE"
- **Font**: Times New Roman, Bold
- **Size**: 36px
- **Color**: #2c3e50 (dark blue)
- **Alignment**: Center
- **Letter Spacing**: 3px

#### Content
- **Opening Text**: "This is to acknowledge and appreciate"
- **Second Line**: "the exceptional service of"
- **Participant Name**: Dynamic field, bold, underlined, 32px, #e74c3c (red)
- **Middle Text**: "towards the successful hosting"
- **Continuation**: "of the"
- **Event Name**: "MDCAN BDM 14th – 2025" (28px, bold, #2c3e50)
- **Closing Text**: "on 1st – 6th September 2025"

## Common Styling

### Text Styling
- **Font**: Times New Roman
- **Body Text Size**: 20px
- **Line Height**: 1.6
- **Alignment**: Center

### Signatures Section
Two signature blocks arranged horizontally:

#### Left Signature
- **Image**: president-signature.png
- **Name**: Prof. Aminu Mohammed
- **Title**: MDCAN President

#### Right Signature
- **Image**: chairman-signature.png
- **Name**: Prof. Appolos Ndukuba
- **Title**: LOC Chairman

### Signature Styling
- **Name Font**: 16px, Bold
- **Title Font**: 14px, Regular
- **Signature Line**: 2px solid black, 200px width
- **Image Size**: Maximum 200x60px

### Page Layout
- **Orientation**: Landscape A4
- **Margins**: 0.5 inches all sides
- **Border**: 3px solid #2c3e50
- **Background**: White
- **Padding**: 60px top/bottom, 40px left/right

## File Requirements

### Signature Images
- **Format**: PNG (preferred) or JPG
- **Dimensions**: Approximately 200x60 pixels
- **Background**: Transparent (PNG) or white
- **Quality**: High resolution for print quality
- **Naming**: 
  - `president-signature.png`
  - `chairman-signature.png`

### Output Format
- **File Type**: PDF
- **Quality**: Print-ready (300 DPI equivalent)
- **Size**: A4 Landscape
- **Filename Format**: 
  - Participation: `MDCAN_BDM_2025_Certificate_[Participant_Name].pdf`
  - Service: `MDCAN_BDM_2025_Service_[Participant_Name].pdf`

## Template Variables

The certificate templates use these dynamic fields:
- `{{ participant_name }}`: Full name of the participant
- `{{ certificate_title }}`: "CERTIFICATE OF PARTICIPATION" or "ACKNOWLEDGEMENT OF SERVICE"
- `{{ certificate_content }}`: Type-specific content block
- `{{ president_signature }}`: Path to president's signature image
- `{{ chairman_signature }}`: Path to chairman's signature image

## Color Scheme
- **Primary Blue**: #2c3e50 (borders, titles)
- **Accent Red**: #e74c3c (participant name)
- **Text Black**: #000000 (body text, signatures)
- **Background**: #ffffff (white)

## Typography
- **Primary Font**: Times New Roman (serif)
- **Font Weights**: Regular (400), Bold (700)
- **Text Alignment**: Center for all elements

## Usage Guidelines

### Certificate of Participation
- Use for all conference attendees
- Recognizes participation in the event
- Standard format for participants

### Acknowledgement of Service
- Use for volunteers, organizers, and staff
- Recognizes contribution to event success
- Shows appreciation for service rendered
