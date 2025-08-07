"""
Fixed version of the get_statistics endpoint for MDCAN BDM 2025 Certificate Platform
"""

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get application statistics with robust error handling for missing fields"""
    try:
        # Basic stats that should work even with schema discrepancies
        stats = {
            'participants': {
                'total': 0,
                'participation_certificates': 0,
                'service_certificates': 0,
                'certificates_sent': 0,
                'certificates_pending': 0,
                'certificates_failed': 0
            },
            'recent_activity': {
                'registrations_today': 0,
                'certificates_sent_today': 0
            },
            'system': {
                'database_type': 'PostgreSQL',
                'total_logs': 0,
                'status': 'Connected'
            }
        }
        
        # Safely try to get counts with error handling for each query
        try:
            stats['participants']['total'] = Participant.query.count()
        except Exception as e:
            print(f"Error getting participant count: {e}")
        
        try:
            stats['participants']['participation_certificates'] = Participant.query.filter_by(certificate_type='participation').count()
        except Exception as e:
            print(f"Error getting participation certificate count: {e}")
        
        try:
            stats['participants']['service_certificates'] = Participant.query.filter_by(certificate_type='service').count()
        except Exception as e:
            print(f"Error getting service certificate count: {e}")
        
        try:
            stats['participants']['certificates_sent'] = Participant.query.filter_by(certificate_status='sent').count()
        except Exception as e:
            print(f"Error getting certificates sent count: {e}")
        
        try:
            stats['participants']['certificates_pending'] = Participant.query.filter_by(certificate_status='pending').count()
        except Exception as e:
            print(f"Error getting certificates pending count: {e}")
        
        try:
            stats['participants']['certificates_failed'] = Participant.query.filter_by(certificate_status='failed').count()
        except Exception as e:
            print(f"Error getting certificates failed count: {e}")
        
        try:
            stats['recent_activity']['registrations_today'] = Participant.query.filter(
                Participant.created_at >= datetime.utcnow().date()
            ).count()
        except Exception as e:
            print(f"Error getting registrations today count: {e}")
        
        try:
            stats['recent_activity']['certificates_sent_today'] = CertificateLog.query.filter(
                CertificateLog.timestamp >= datetime.utcnow().date(),
                CertificateLog.action == 'sent',
                CertificateLog.status == 'success'
            ).count()
        except Exception as e:
            print(f"Error getting certificates sent today count: {e}")
            
        try:
            stats['system']['total_logs'] = CertificateLog.query.count()
        except Exception as e:
            print(f"Error getting total logs count: {e}")
        
        # Add database schema version and connection info
        try:
            with db.engine.connect() as conn:
                result = conn.execute(sa.text("SELECT version();"))
                version = result.scalar()
                stats['system']['database_version'] = version
        except Exception as e:
            stats['system']['database_version'] = 'Unknown'
            print(f"Error getting database version: {e}")
        
        return jsonify(stats)
    except Exception as e:
        error_message = str(e)
        print(f"Error in get_statistics: {error_message}")
        return jsonify({
            'error': f'Failed to get statistics: {error_message}',
            'system': {
                'status': 'Error',
                'message': 'Database error encountered'
            }
        }), 500
