import React, { useState } from 'react';

const CertificatePreview = ({ participantName = "[Participant's Name]" }) => {
  const [certificateType, setCertificateType] = useState('participation');

  // Responsive styles
  const responsiveStyles = `
    .certificate-preview {
      max-width: 100%;
      margin: 0 auto;
      padding: 20px;
      box-sizing: border-box;
      min-height: 400px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .certificate-preview.with-background {
      background-size: cover !important;
      background-position: center !important;
      background-repeat: no-repeat !important;
      position: relative;
    }

    .certificate-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(255, 255, 255, 0.9);
      border-radius: 8px;
    }

    .certificate-title {
      font-size: clamp(1.5rem, 4vw, 2.5rem);
      font-weight: bold;
      text-align: center;
      margin: 20px 0;
      color: #2c3e50;
      text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
      position: relative;
      z-index: 1;
    }

    .certificate-text {
      font-size: clamp(0.9rem, 2.5vw, 1.2rem);
      text-align: center;
      margin: 10px 0;
      color: #34495e;
      position: relative;
      z-index: 1;
    }

    .participant-name {
      font-size: clamp(1.2rem, 3.5vw, 2rem);
      font-weight: bold;
      text-align: center;
      margin: 20px 0;
      color: #8b4513;
      text-decoration: underline;
      position: relative;
      z-index: 1;
    }

    .event-name-preview {
      font-size: clamp(0.8rem, 2vw, 1.1rem);
      font-weight: bold;
      text-align: center;
      margin: 15px 0;
      color: #2c3e50;
      line-height: 1.3;
      position: relative;
      z-index: 1;
      padding: 0 10px;
    }

    .signatures {
      display: flex;
      justify-content: space-around;
      align-items: flex-end;
      margin-top: 30px;
      flex-wrap: wrap;
      gap: 20px;
      position: relative;
      z-index: 1;
    }

    .signature {
      text-align: center;
      flex: 1;
      min-width: 150px;
      max-width: 200px;
    }

    .signature img {
      height: clamp(40px, 8vw, 60px);
      width: auto;
      margin-bottom: 5px;
      max-width: 100%;
      object-fit: contain;
    }

    .signature-name-preview {
      font-size: clamp(0.8rem, 2vw, 1rem);
      font-weight: bold;
      margin-bottom: 2px;
      color: #2c3e50;
    }

    .signature-title-preview {
      font-size: clamp(0.7rem, 1.8vw, 0.9rem);
      color: #7f8c8d;
      line-height: 1.2;
    }

    .conference-details-preview {
      margin: 20px 0;
      padding: 0 15px;
    }

    .certificate-header {
      text-align: center;
      margin-bottom: 20px;
      position: relative;
      z-index: 1;
    }

    /* Mobile specific styles */
    @media (max-width: 768px) {
      .certificate-preview {
        padding: 15px;
        margin: 10px;
        min-height: 350px;
      }

      .signatures {
        flex-direction: column;
        align-items: center;
        gap: 15px;
      }

      .signature {
        max-width: 180px;
        margin: 0 auto;
      }

      .event-name-preview {
        padding: 0 5px;
      }

      .certificate-title {
        margin: 15px 0;
      }

      .participant-name {
        margin: 15px 0;
      }
    }

    /* Tablet styles */
    @media (min-width: 769px) and (max-width: 1024px) {
      .certificate-preview {
        max-width: 90%;
        padding: 25px;
      }

      .signatures {
        justify-content: center;
        gap: 30px;
      }
    }

    /* Desktop styles */
    @media (min-width: 1025px) {
      .certificate-preview {
        max-width: 800px;
        padding: 40px;
      }
    }

    /* Print styles */
    @media print {
      .certificate-preview {
        max-width: 100%;
        box-shadow: none;
        border: 1px solid #ccc;
      }

      .certificate-overlay {
        background: rgba(255, 255, 255, 0.95);
      }
    }

    /* Form responsive styles */
    .form-group {
      margin-bottom: 20px;
      text-align: center;
    }

    .form-group label {
      font-size: clamp(0.9rem, 2vw, 1.1rem);
      font-weight: 500;
      color: #2c3e50;
    }

    .form-group select {
      margin-left: 10px;
      padding: 8px 12px;
      font-size: clamp(0.8rem, 2vw, 1rem);
      border: 2px solid #bdc3c7;
      border-radius: 4px;
      background-color: white;
      min-width: 200px;
    }

    @media (max-width: 480px) {
      .form-group {
        text-align: left;
      }

      .form-group label {
        display: block;
        margin-bottom: 8px;
      }

      .form-group select {
        margin-left: 0;
        width: 100%;
        max-width: 300px;
      }
    }

    .info-section {
      margin-top: 20px;
      padding: 15px;
      background-color: #f8f9fa;
      border-radius: 4px;
      font-size: clamp(0.8rem, 2vw, 1rem);
    }

    .info-section h4 {
      font-size: clamp(1rem, 2.5vw, 1.3rem);
      color: #2c3e50;
      margin-bottom: 10px;
    }

    .info-section ul {
      padding-left: 20px;
    }

    .info-section li {
      margin-bottom: 5px;
      line-height: 1.4;
    }

    @media (max-width: 768px) {
      .info-section {
        padding: 12px;
        margin: 15px 0;
      }

      .info-section ul {
        padding-left: 15px;
      }
    }
  `;

  const renderParticipationCertificate = () => (
    <div className="certificate-preview with-background" style={{ 
      backgroundImage: 'url("/certificate_background.png")'
    }}>
      <div className="certificate-overlay"></div>
      <div className="certificate-header">
        {/* Golden seal removed */}
      </div>
      
      <div className="certificate-title">
        CERTIFICATE OF PARTICIPATION
      </div>
      
      <div className="certificate-text">
        This is to certify that
      </div>
      
      <div className="participant-name">
        {participantName}
      </div>
      
      <div className="certificate-text">
        participated in the
      </div>
      
      <div className="conference-details-preview">
        <div className="event-name-preview">
          MEDICAL AND DENTAL CONSULTANTS’ ASSOCIATION OF NIGERIA 14th Biennial Delegates' Meeting and SCIENTIFIC Conference 
        </div>
        
        <div className="certificate-text">
          on 1st–6th September, 2025
        </div>
      </div>
      
      <div className="signatures">
        <div className="signature">
          <img 
            src="/president-signature.jpg" 
            alt="President Signature"
          />
          <div className="signature-name-preview">
            Prof. Aminu Mohammed
          </div>
          <div className="signature-title-preview">
            MDCAN President
          </div>
        </div>
        
        <div className="signature">
          <img 
            src="/chairman-signature.png" 
            alt="Chairman Signature"
          />
          <div className="signature-name-preview">
            Prof. Appolos Ndukuba
          </div>
          <div className="signature-title-preview">
            LOC Chairman
          </div>
        </div>
      </div>
    </div>
  );

  const renderServiceCertificate = () => (
    <div className="certificate-preview with-background" style={{ 
      backgroundImage: 'url("/certificate_background.png")'
    }}>
      <div className="certificate-overlay"></div>
      <div className="certificate-header">
        {/* Golden seal removed */}
      </div>
      
      <div className="certificate-title">
        ACKNOWLEDGEMENT OF SERVICE
      </div>
      
      <div className="certificate-text">
        This is to acknowledge and appreciate
      </div>
      
      <div className="certificate-text">
        the exceptional service of
      </div>
      
      <div className="participant-name">
        {participantName}
      </div>
      
      <div className="certificate-text">
        towards the successful hosting of the
      </div>
      
      <div className="conference-details-preview">
        <div className="event-name-preview">
          MEDICAL AND DENTAL CONSULTANTS' ASSOCIATION OF NIGERIA 14th Biennial Delegates' Meeting and SCIENTIFIC Conference
        </div>
        
        <div className="certificate-text">
          on 1st–6th September, 2025
        </div>
      </div>
      
      <div className="signatures">
        <div className="signature">
          <img 
            src="/chairman-signature.png" 
            alt="Chairman Signature"
          />
          <div className="signature-name-preview">
            Prof. Appolos Ndukuba
          </div>
          <div className="signature-title-preview">
            LOC Chairman
          </div>
        </div>
        
        <div className="signature">
          <img 
            src="/Dr_Augustine_Duru_signature.jpg" 
            alt="Secretary Signature"
          />
          <div className="signature-name-preview">
            Dr. Augustine Duru
          </div>
          <div className="signature-title-preview">
            LOC Secretary<br/>MDCAN Sec. Gen.
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div>
      <style>{responsiveStyles}</style>
      
      <h2 style={{ 
        textAlign: 'center', 
        fontSize: 'clamp(1.3rem, 3vw, 1.8rem)', 
        color: '#2c3e50',
        marginBottom: '20px'
      }}>
        Certificate Preview
      </h2>
      
      <div className="form-group">
        <label htmlFor="previewType">Preview Certificate Type:</label>
        <select
          id="previewType"
          value={certificateType}
          onChange={(e) => setCertificateType(e.target.value)}
        >
          <option value="participation">Certificate of Participation</option>
          <option value="service">Acknowledgement of Service</option>
        </select>
      </div>

      <p style={{ 
        textAlign: 'center', 
        fontSize: 'clamp(0.9rem, 2vw, 1.1rem)',
        color: '#34495e',
        margin: '20px 0',
        padding: '0 15px'
      }}>
        This is how the {certificateType === 'participation' ? 'Certificate of Participation' : 'Acknowledgement of Service'} will look when generated and sent to participants:
      </p>
      
      {certificateType === 'participation' ? renderParticipationCertificate() : renderServiceCertificate()}
      
      <div className="info-section">
        <h4>Modern Certificate Design Features:</h4>
        <p>
          The certificate uses the official background image with the following design elements:
        </p>
        <ul>
          <li><strong>Official Background:</strong> The certificate_background.png image serves as the backdrop</li>
          <li><strong>Clean Design:</strong> Minimalist layout with focus on certificate content</li>
          <li><strong>Enhanced Typography:</strong> Bold text with subtle shadows for readability</li>
          <li><strong>Professional Signatures:</strong> Digital signatures of Prof. Aminu Mohammed and Prof. Appolos Ndukuba</li>
          <li><strong>Responsive Design:</strong> Adapts to all screen sizes from mobile to desktop</li>
          <li><strong>Updated Text:</strong> Full event name held on 1st–6th September, 2025</li>
        </ul>
        <p>
          <strong>Required Files for Production:</strong>
        </p>
        <ul>
          <li><code>certificate_background.png</code> - Official certificate background</li>
          <li><code>president-signature.jpg</code> - Prof. Aminu Mohammed's signature</li>
          <li><code>chairman-signature.png</code> - Prof. Appolos Ndukuba's signature</li>
          <li><code>Dr_Augustine_Duru_signature.jpg</code> - Dr. Augustine Duru's signature</li>
        </ul>
        <p>
          All images should be high-resolution PNG/JPG files with transparent backgrounds for best results.
        </p>
      </div>
    </div>
  );
};

export default CertificatePreview;
