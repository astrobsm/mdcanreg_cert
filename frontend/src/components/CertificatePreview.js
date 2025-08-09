import React, { useState } from 'react';

const CertificatePreview = ({ participantName = "[Participant's Name]" }) => {
  const [certificateType, setCertificateType] = useState('participation');

  const renderParticipationCertificate = () => (
    <div className="certificate-preview with-background" style={{ 
      backgroundImage: 'url("/certificate_background.png")',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
      position: 'relative'
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
          HELD IN ENUGU on 1st–6th September, 2025
        </div>
      </div>
      
      <div className="signatures">
        <div className="signature">
          <img 
            src="/president-signature.jpg" 
            alt="President Signature" 
            style={{ height: '60px', marginBottom: '5px' }}
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
            style={{ height: '60px', marginBottom: '5px' }}
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
      backgroundImage: 'url("/certificate_background.png")',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
      position: 'relative'
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
          MDCAN BDM 042-2025
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
            style={{ height: '60px', marginBottom: '5px' }}
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
            style={{ height: '60px', marginBottom: '5px' }}
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
      <h2>Certificate Preview</h2>
      
      <div className="form-group" style={{ marginBottom: '20px' }}>
        <label htmlFor="previewType">Preview Certificate Type:</label>
        <select
          id="previewType"
          value={certificateType}
          onChange={(e) => setCertificateType(e.target.value)}
          style={{ marginLeft: '10px', padding: '5px' }}
        >
          <option value="participation">Certificate of Participation</option>
          <option value="service">Acknowledgement of Service</option>
        </select>
      </div>

      <p>This is how the {certificateType === 'participation' ? 'Certificate of Participation' : 'Acknowledgement of Service'} will look when generated and sent to participants:</p>
      
      {certificateType === 'participation' ? renderParticipationCertificate() : renderServiceCertificate()}
      
      <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
        <h4>Modern Certificate Design Features:</h4>
        <p>
          The certificate uses the official background image with the following design elements:
        </p>
        <ul>
          <li><strong>Official Background:</strong> The certificate_background.png image serves as the backdrop</li>
          <li><strong>Clean Design:</strong> Minimalist layout with focus on certificate content</li>
          <li><strong>Enhanced Typography:</strong> Bold text with subtle shadows for readability</li>
          <li><strong>Professional Signatures:</strong> Digital signatures of Prof. Aminu Mohammed and Prof. Appolos Ndukuba</li>
          <li><strong>Updated Text:</strong> MDCAN BDM 042-2025 held on 1st–6th September, 2025</li>
        </ul>
        <p>
          <strong>Required Files for Production:</strong>
        </p>
        <ul>
          <li><code>certificate_background.png</code> - Official certificate background</li>
          <li><code>president-signature.png</code> - Prof. Aminu Mohammed's signature</li>
          <li><code>chairman-signature.png</code> - Prof. Appolos Ndukuba's signature</li>
        </ul>
        <p>
          All images should be high-resolution PNG files with transparent backgrounds for best results.
        </p>
      </div>
    </div>
  );
};

export default CertificatePreview;
