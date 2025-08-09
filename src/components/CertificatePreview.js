import React, { useState } from 'react';

const CertificatePreview = ({ participantName = "[Participant's Name]" }) => {
  const [certificateType, setCertificateType] = useState('participation');

  const renderParticipationCertificate = () => (
    <div className="certificate-preview with-background">
      <div className="certificate-header">
        <div className="logo-placeholder">
          MDCAN<br/>LOGO
        </div>
        <div className="golden-seal-preview">
          <div className="seal-text-preview">
            MDCAN<br/>
            BDM<br/>
            2025
          </div>
        </div>
        <div className="logo-placeholder">
          COAL<br/>CITY<br/>LOGO
        </div>
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
          MDCAN BDM 14th – 2025
        </div>
        
        <div className="certificate-text">
          held in Enugu on 1st – 6th September, 2025
        </div>
      </div>
      
      <div className="signatures">
        <div className="signature">
          <div className="signature-line"></div>
          <div className="signature-name-preview">
            Prof. Aminu Mohammed
          </div>
          <div className="signature-title-preview">
            MDCAN President
          </div>
        </div>
        
        <div className="signature">
          <div className="signature-line"></div>
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
    <div className="certificate-preview with-background">
      <div className="certificate-header">
        <div className="logo-placeholder">
          MDCAN<br/>LOGO
        </div>
        <div className="golden-seal-preview">
          <div className="seal-text-preview">
            MDCAN<br/>
            BDM<br/>
            2025
          </div>
        </div>
        <div className="logo-placeholder">
          COAL<br/>CITY<br/>LOGO
        </div>
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
          MDCAN BDM 14th – 2025
        </div>
        
        <div className="certificate-text">
          on 1st – 6th September 2025
        </div>
      </div>
      
      <div className="signatures">
        <div className="signature">
          <div className="signature-line"></div>
          <div className="signature-name-preview">
            Prof. Aminu Mohammed
          </div>
          <div className="signature-title-preview">
            MDCAN President
          </div>
        </div>
        
        <div className="signature">
          <div className="signature-line"></div>
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
          The actual certificates will feature a premium modern design with:
        </p>
        <ul>
          <li><strong>Golden Border & Seal:</strong> Elegant gold gradient borders and a central golden seal</li>
          <li><strong>MDCAN Logo:</strong> Official MDCAN logo in the top-left corner</li>
          <li><strong>Coal City Logo:</strong> Coal City logo in the top-right corner</li>
          <li><strong>Professional Signatures:</strong> Digital signatures of Prof. Aminu Mohammed and Prof. Appolos Ndukuba</li>
          <li><strong>Classic Typography:</strong> Times New Roman with gradient text effects</li>
          <li><strong>Decorative Elements:</strong> Corner ornaments and subtle background patterns</li>
        </ul>
        <p>
          <strong>Required Files for Production:</strong>
        </p>
        <ul>
          <li><code>mdcan-logo.png</code> - MDCAN official logo</li>
          <li><code>coalcity-logo.png</code> - Coal City logo</li>
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
