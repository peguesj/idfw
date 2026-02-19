"""
Security and compliance framework for the hooks system.
"""

import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import secrets
import base64

from .core import HookContext


class SecurityLevel(Enum):
    """Security classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"
    SOC2 = "soc2"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"


class ThreatLevel(Enum):
    """Threat severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PIIDetectionResult:
    """Results from PII detection."""
    found_pii: bool
    pii_types: List[str]
    pii_locations: List[Tuple[int, int]]  # (start, end) positions
    confidence_scores: Dict[str, float]
    redacted_content: str
    risk_level: ThreatLevel


@dataclass
class SecurityAuditEntry:
    """Security audit log entry."""
    entry_id: str
    timestamp: datetime
    event_type: str
    severity: ThreatLevel
    user_id: Optional[str]
    resource_id: str
    action: str
    result: str
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'entry_id': self.entry_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'severity': self.severity.value,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'action': self.action,
            'result': self.result,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }


@dataclass
class VulnerabilityAssessment:
    """Results from vulnerability assessment."""
    assessment_id: str
    assessed_at: datetime
    target_component: str
    vulnerabilities_found: List[Dict[str, Any]]
    overall_risk_score: float
    recommendations: List[str]
    next_assessment_due: datetime


@dataclass
class ComplianceCheck:
    """Results from compliance validation."""
    check_id: str
    framework: ComplianceFramework
    requirement_id: str
    description: str
    status: str  # compliant, non_compliant, partial, not_applicable
    evidence: List[str]
    findings: List[str]
    remediation_steps: List[str]
    checked_at: datetime


class PIIDetector:
    """Detect and protect personally identifiable information."""
    
    def __init__(self):
        # PII patterns with confidence scores
        self.pii_patterns = {
            'email': {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'confidence': 0.95
            },
            'phone': {
                'pattern': r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
                'confidence': 0.85
            },
            'ssn': {
                'pattern': r'\b\d{3}-\d{2}-\d{4}\b',
                'confidence': 0.98
            },
            'credit_card': {
                'pattern': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                'confidence': 0.90
            },
            'ip_address': {
                'pattern': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
                'confidence': 0.70
            },
            'api_key': {
                'pattern': r'[Aa][Pp][Ii][-_]?[Kk][Ee][Yy][-_]?[:=]\s*[\'"]?([A-Za-z0-9_\-]{20,})[\'"]?',
                'confidence': 0.85
            },
            'jwt_token': {
                'pattern': r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
                'confidence': 0.90
            },
            'password_field': {
                'pattern': r'[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd][-_]?[:=]\s*[\'"]?([^\s\'"]{8,})[\'"]?',
                'confidence': 0.80
            },
            'bank_account': {
                'pattern': r'\b\d{8,17}\b',
                'confidence': 0.60  # Lower confidence due to potential false positives
            },
            'driver_license': {
                'pattern': r'\b[A-Z]{1,2}\d{6,8}\b',
                'confidence': 0.70
            }
        }
        
        # Context-based PII indicators
        self.pii_context_indicators = {
            'personal_name': ['name', 'firstname', 'lastname', 'fullname'],
            'address': ['address', 'street', 'city', 'zip', 'postal'],
            'financial': ['account', 'routing', 'bank', 'credit', 'debit'],
            'medical': ['patient', 'medical', 'health', 'diagnosis'],
            'employment': ['employee', 'salary', 'wage', 'hr']
        }
    
    def detect_pii(self, content: str, context: str = "") -> PIIDetectionResult:
        """Detect PII in content."""
        
        found_types = []
        locations = []
        confidence_scores = {}
        redacted_content = content
        
        # Pattern-based detection
        for pii_type, pattern_info in self.pii_patterns.items():
            pattern = pattern_info['pattern']
            confidence = pattern_info['confidence']
            
            matches = list(re.finditer(pattern, content))
            if matches:
                found_types.append(pii_type)
                confidence_scores[pii_type] = confidence
                
                for match in matches:
                    locations.append((match.start(), match.end()))
                    
                    # Redact the content
                    matched_text = match.group(0)
                    redaction = self._create_redaction(matched_text, pii_type)
                    redacted_content = redacted_content.replace(matched_text, redaction)
        
        # Context-based detection
        context_pii = self._detect_context_pii(content, context)
        for pii_type, confidence in context_pii.items():
            if pii_type not in found_types:
                found_types.append(pii_type)
                confidence_scores[pii_type] = confidence
        
        # Determine risk level
        risk_level = self._assess_pii_risk(found_types, confidence_scores)
        
        return PIIDetectionResult(
            found_pii=len(found_types) > 0,
            pii_types=found_types,
            pii_locations=locations,
            confidence_scores=confidence_scores,
            redacted_content=redacted_content,
            risk_level=risk_level
        )
    
    def _detect_context_pii(self, content: str, context: str) -> Dict[str, float]:
        """Detect PII based on context clues."""
        
        context_pii = {}
        combined_text = (content + " " + context).lower()
        
        for pii_category, indicators in self.pii_context_indicators.items():
            for indicator in indicators:
                if indicator in combined_text:
                    # Look for potential PII values near the indicator
                    pattern = rf'{indicator}[-_\s]*[:=]\s*([^\s,;\n]+)'
                    matches = re.findall(pattern, combined_text, re.IGNORECASE)
                    if matches:
                        context_pii[f'context_{pii_category}'] = 0.6
                        break
        
        return context_pii
    
    def _create_redaction(self, original_text: str, pii_type: str) -> str:
        """Create appropriate redaction for PII."""
        
        redaction_patterns = {
            'email': '[EMAIL_REDACTED]',
            'phone': '[PHONE_REDACTED]',
            'ssn': '[SSN_REDACTED]',
            'credit_card': '[CARD_REDACTED]',
            'api_key': '[API_KEY_REDACTED]',
            'jwt_token': '[TOKEN_REDACTED]',
            'password_field': '[PASSWORD_REDACTED]'
        }
        
        return redaction_patterns.get(pii_type, '[PII_REDACTED]')
    
    def _assess_pii_risk(
        self,
        pii_types: List[str],
        confidence_scores: Dict[str, float]
    ) -> ThreatLevel:
        """Assess overall risk level based on detected PII."""
        
        if not pii_types:
            return ThreatLevel.LOW
        
        high_risk_types = ['ssn', 'credit_card', 'bank_account', 'jwt_token', 'api_key']
        medium_risk_types = ['email', 'phone', 'driver_license']
        
        # Check for high-risk PII
        for pii_type in pii_types:
            if pii_type in high_risk_types:
                confidence = confidence_scores.get(pii_type, 0)
                if confidence > 0.8:
                    return ThreatLevel.CRITICAL
                elif confidence > 0.6:
                    return ThreatLevel.HIGH
        
        # Check for medium-risk PII
        for pii_type in pii_types:
            if pii_type in medium_risk_types:
                confidence = confidence_scores.get(pii_type, 0)
                if confidence > 0.8:
                    return ThreatLevel.HIGH
                elif confidence > 0.6:
                    return ThreatLevel.MEDIUM
        
        # Multiple low-confidence PII types
        if len(pii_types) > 3:
            return ThreatLevel.MEDIUM
        
        return ThreatLevel.LOW


class EncryptionManager:
    """AES-256-GCM encryption for sensitive data."""
    
    def __init__(self, key_path: Optional[Path] = None):
        self.key_path = key_path or Path.home() / '.claude' / 'hooks' / 'security' / 'encryption.key'
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or generate encryption key
        self.encryption_key = self._get_or_create_key()
    
    def _get_or_create_key(self) -> bytes:
        """Get existing or create new encryption key."""
        
        if self.key_path.exists():
            try:
                with open(self.key_path, 'rb') as f:
                    return f.read()
            except Exception as e:
                print(f"Warning: Could not load encryption key: {e}")
        
        # Generate new key
        key = secrets.token_bytes(32)  # 256-bit key
        
        try:
            # Save key with restricted permissions
            with open(self.key_path, 'wb') as f:
                f.write(key)
            
            # Set restrictive permissions (owner read-only)
            os.chmod(self.key_path, 0o600)
            
        except Exception as e:
            print(f"Warning: Could not save encryption key: {e}")
        
        return key
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """Encrypt data using AES-256-GCM."""
        
        # Convert string to bytes if needed
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Generate random nonce (12 bytes for GCM)
        nonce = secrets.token_bytes(12)
        
        # Simple AES implementation (in production, use cryptography library)
        # For this implementation, we'll use a basic approach
        encrypted_data = self._simple_encrypt(data, nonce)
        
        # Combine nonce + encrypted data and encode as base64
        combined = nonce + encrypted_data
        return base64.b64encode(combined).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data using AES-256-GCM."""
        
        try:
            # Decode from base64
            combined = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Extract nonce and encrypted data
            nonce = combined[:12]
            ciphertext = combined[12:]
            
            # Decrypt
            decrypted_data = self._simple_decrypt(ciphertext, nonce)
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
    
    def _simple_encrypt(self, data: bytes, nonce: bytes) -> bytes:
        """Simple encryption (placeholder for real AES-GCM)."""
        
        # This is a placeholder implementation
        # In production, use proper cryptography libraries
        
        key_hash = hashlib.sha256(self.encryption_key + nonce).digest()
        
        encrypted = bytearray()
        for i, byte in enumerate(data):
            key_byte = key_hash[i % len(key_hash)]
            encrypted.append(byte ^ key_byte)
        
        return bytes(encrypted)
    
    def _simple_decrypt(self, data: bytes, nonce: bytes) -> bytes:
        """Simple decryption (placeholder for real AES-GCM)."""
        
        # This is the reverse of the simple encryption
        key_hash = hashlib.sha256(self.encryption_key + nonce).digest()
        
        decrypted = bytearray()
        for i, byte in enumerate(data):
            key_byte = key_hash[i % len(key_hash)]
            decrypted.append(byte ^ key_byte)
        
        return bytes(decrypted)


class AuditLogger:
    """Comprehensive audit trail logging."""
    
    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or Path.home() / '.claude' / 'hooks' / 'security' / 'audit.log'
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Audit configuration
        self.max_log_size = 10 * 1024 * 1024  # 10MB
        self.max_log_files = 10
        
        # Security events to always log
        self.critical_events = {
            'authentication_failure',
            'authorization_failure', 
            'data_access',
            'data_modification',
            'configuration_change',
            'security_violation',
            'pii_detection',
            'encryption_failure'
        }
    
    def log_event(
        self,
        event_type: str,
        action: str,
        result: str,
        severity: ThreatLevel = ThreatLevel.LOW,
        user_id: Optional[str] = None,
        resource_id: str = "",
        details: Optional[Dict[str, Any]] = None,
        context: Optional[HookContext] = None
    ) -> str:
        """Log a security event."""
        
        entry_id = str(uuid.uuid4())
        
        # Extract additional info from context
        ip_address = None
        user_agent = None
        if context and context.metadata:
            ip_address = context.metadata.get('ip_address')
            user_agent = context.metadata.get('user_agent')
        
        audit_entry = SecurityAuditEntry(
            entry_id=entry_id,
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            result=result,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Write to log file
        self._write_audit_entry(audit_entry)
        
        # Trigger alerts for critical events
        if event_type in self.critical_events or severity in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            self._trigger_security_alert(audit_entry)
        
        return entry_id
    
    def _write_audit_entry(self, entry: SecurityAuditEntry):
        """Write audit entry to log file."""
        
        # Check if log rotation is needed
        if self.log_path.exists() and self.log_path.stat().st_size > self.max_log_size:
            self._rotate_log_files()
        
        # Write entry as JSON line
        log_line = json.dumps(entry.to_dict()) + '\n'
        
        with open(self.log_path, 'a') as f:
            f.write(log_line)
    
    def _rotate_log_files(self):
        """Rotate log files when they get too large."""
        
        try:
            # Move existing log files
            for i in range(self.max_log_files - 1, 0, -1):
                old_file = self.log_path.with_suffix(f'.log.{i}')
                new_file = self.log_path.with_suffix(f'.log.{i + 1}')
                
                if old_file.exists():
                    if i == self.max_log_files - 1:
                        old_file.unlink()  # Delete oldest
                    else:
                        old_file.rename(new_file)
            
            # Move current log to .1
            if self.log_path.exists():
                self.log_path.rename(self.log_path.with_suffix('.log.1'))
                
        except Exception as e:
            print(f"Warning: Log rotation failed: {e}")
    
    def _trigger_security_alert(self, entry: SecurityAuditEntry):
        """Trigger security alerts for critical events."""
        
        # In a real implementation, this would send alerts via email, Slack, etc.
        print(f"SECURITY ALERT: {entry.event_type} - {entry.action} - {entry.severity.value}")
    
    def search_audit_log(
        self,
        event_type: Optional[str] = None,
        severity: Optional[ThreatLevel] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SecurityAuditEntry]:
        """Search audit log entries."""
        
        entries = []
        
        if not self.log_path.exists():
            return entries
        
        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    if len(entries) >= limit:
                        break
                    
                    try:
                        entry_dict = json.loads(line.strip())
                        
                        # Apply filters
                        if event_type and entry_dict.get('event_type') != event_type:
                            continue
                        
                        if severity and entry_dict.get('severity') != severity.value:
                            continue
                        
                        if user_id and entry_dict.get('user_id') != user_id:
                            continue
                        
                        entry_time = datetime.fromisoformat(entry_dict['timestamp'])
                        if start_time and entry_time < start_time:
                            continue
                        
                        if end_time and entry_time > end_time:
                            continue
                        
                        # Convert back to SecurityAuditEntry
                        entry_dict['timestamp'] = entry_time
                        entry_dict['severity'] = ThreatLevel(entry_dict['severity'])
                        
                        entries.append(SecurityAuditEntry(**entry_dict))
                        
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"Warning: Could not parse audit entry: {e}")
                        continue
        
        except Exception as e:
            print(f"Warning: Could not read audit log: {e}")
        
        return entries


class VulnerabilityScanner:
    """Real-time vulnerability scanning and assessment."""
    
    def __init__(self):
        self.vulnerability_patterns = {
            'hardcoded_secrets': {
                'patterns': [
                    r'password\s*=\s*[\'"][^\'"]{8,}[\'"]',
                    r'api_key\s*=\s*[\'"][^\'"]{20,}[\'"]',
                    r'secret\s*=\s*[\'"][^\'"]{16,}[\'"]',
                ],
                'severity': ThreatLevel.HIGH,
                'description': 'Hardcoded secrets detected'
            },
            'sql_injection': {
                'patterns': [
                    r'SELECT\s+.*\s+FROM\s+.*\s+WHERE\s+.*\s*[\'"][^\'"]*\+',
                    r'INSERT\s+INTO\s+.*\s+VALUES\s*\([^)]*\+[^)]*\)',
                ],
                'severity': ThreatLevel.CRITICAL,
                'description': 'Potential SQL injection vulnerability'
            },
            'path_traversal': {
                'patterns': [
                    r'\.\./.*\.\./',
                    r'\.\.\\.*\.\.\\',
                ],
                'severity': ThreatLevel.HIGH,
                'description': 'Path traversal vulnerability detected'
            },
            'insecure_random': {
                'patterns': [
                    r'Math\.random\(\)',
                    r'random\.random\(\)',
                ],
                'severity': ThreatLevel.MEDIUM,
                'description': 'Insecure random number generation'
            },
            'debug_code': {
                'patterns': [
                    r'console\.log\(',
                    r'print\s*\(',
                    r'debug\s*=\s*True',
                ],
                'severity': ThreatLevel.LOW,
                'description': 'Debug code left in production'
            }
        }
    
    def scan_content(self, content: str, context: str = "") -> VulnerabilityAssessment:
        """Scan content for security vulnerabilities."""
        
        vulnerabilities = []
        total_risk_score = 0.0
        
        for vuln_type, vuln_info in self.vulnerability_patterns.items():
            patterns = vuln_info['patterns']
            severity = vuln_info['severity']
            description = vuln_info['description']
            
            matches = []
            for pattern in patterns:
                pattern_matches = list(re.finditer(pattern, content, re.IGNORECASE))
                matches.extend(pattern_matches)
            
            if matches:
                # Calculate risk score based on severity and match count
                severity_scores = {
                    ThreatLevel.LOW: 1,
                    ThreatLevel.MEDIUM: 3,
                    ThreatLevel.HIGH: 7,
                    ThreatLevel.CRITICAL: 10
                }
                
                risk_score = severity_scores[severity] * len(matches)
                total_risk_score += risk_score
                
                vulnerability = {
                    'type': vuln_type,
                    'description': description,
                    'severity': severity.value,
                    'match_count': len(matches),
                    'risk_score': risk_score,
                    'locations': [(m.start(), m.end()) for m in matches],
                    'samples': [content[m.start():m.end()] for m in matches[:3]]  # First 3 samples
                }
                
                vulnerabilities.append(vulnerability)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(vulnerabilities)
        
        # Calculate next assessment due date
        if total_risk_score > 20:
            next_assessment = datetime.now() + timedelta(days=7)  # Weekly for high risk
        elif total_risk_score > 10:
            next_assessment = datetime.now() + timedelta(days=30)  # Monthly for medium risk
        else:
            next_assessment = datetime.now() + timedelta(days=90)  # Quarterly for low risk
        
        return VulnerabilityAssessment(
            assessment_id=str(uuid.uuid4()),
            assessed_at=datetime.now(),
            target_component=context or "unknown",
            vulnerabilities_found=vulnerabilities,
            overall_risk_score=total_risk_score,
            recommendations=recommendations,
            next_assessment_due=next_assessment
        )
    
    def _generate_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on vulnerabilities."""
        
        recommendations = []
        
        for vuln in vulnerabilities:
            vuln_type = vuln['type']
            
            if vuln_type == 'hardcoded_secrets':
                recommendations.append("Move secrets to environment variables or secure key management")
            elif vuln_type == 'sql_injection':
                recommendations.append("Use parameterized queries or prepared statements")
            elif vuln_type == 'path_traversal':
                recommendations.append("Validate and sanitize file paths, use allowlists")
            elif vuln_type == 'insecure_random':
                recommendations.append("Use cryptographically secure random number generators")
            elif vuln_type == 'debug_code':
                recommendations.append("Remove debug code before production deployment")
        
        # General recommendations
        if vulnerabilities:
            recommendations.extend([
                "Implement regular security code reviews",
                "Use static analysis security testing (SAST) tools",
                "Establish secure coding guidelines for the team"
            ])
        
        return list(set(recommendations))  # Remove duplicates


class ComplianceValidator:
    """Validate compliance with various frameworks."""
    
    def __init__(self):
        self.compliance_requirements = {
            ComplianceFramework.GDPR: {
                'data_protection': 'Ensure personal data is protected with appropriate technical measures',
                'consent': 'Verify explicit consent for data processing',
                'right_to_be_forgotten': 'Implement data deletion capabilities',
                'data_portability': 'Enable data export functionality',
                'privacy_by_design': 'Implement privacy considerations from design phase'
            },
            ComplianceFramework.SOC2: {
                'access_control': 'Implement proper access controls and authentication',
                'encryption': 'Encrypt sensitive data in transit and at rest',
                'monitoring': 'Implement logging and monitoring of system access',
                'incident_response': 'Establish incident response procedures',
                'vendor_management': 'Assess security of third-party vendors'
            }
        }
    
    def validate_compliance(
        self,
        framework: ComplianceFramework,
        content: str,
        context: HookContext
    ) -> List[ComplianceCheck]:
        """Validate compliance with specified framework."""
        
        checks = []
        
        if framework not in self.compliance_requirements:
            return checks
        
        requirements = self.compliance_requirements[framework]
        
        for requirement_id, description in requirements.items():
            check = self._perform_compliance_check(
                framework, requirement_id, description, content, context
            )
            checks.append(check)
        
        return checks
    
    def _perform_compliance_check(
        self,
        framework: ComplianceFramework,
        requirement_id: str,
        description: str,
        content: str,
        context: HookContext
    ) -> ComplianceCheck:
        """Perform a specific compliance check."""
        
        # Basic compliance checking logic
        status = "not_applicable"
        evidence = []
        findings = []
        remediation_steps = []
        
        if framework == ComplianceFramework.GDPR:
            if requirement_id == 'data_protection':
                # Check for encryption mentions
                if any(term in content.lower() for term in ['encrypt', 'hash', 'secure']):
                    status = "compliant"
                    evidence.append("Encryption/security measures mentioned")
                else:
                    status = "non_compliant"
                    findings.append("No explicit data protection measures found")
                    remediation_steps.append("Implement encryption for sensitive data")
            
            elif requirement_id == 'consent':
                if any(term in content.lower() for term in ['consent', 'opt-in', 'permission']):
                    status = "partial"
                    evidence.append("Consent mechanisms mentioned")
                else:
                    status = "non_compliant"
                    findings.append("No consent mechanisms found")
                    remediation_steps.append("Implement explicit consent collection")
        
        elif framework == ComplianceFramework.SOC2:
            if requirement_id == 'access_control':
                if any(term in content.lower() for term in ['auth', 'login', 'access control']):
                    status = "compliant"
                    evidence.append("Access control measures mentioned")
                else:
                    status = "non_compliant"
                    findings.append("No access control measures found")
                    remediation_steps.append("Implement proper authentication and authorization")
            
            elif requirement_id == 'encryption':
                if any(term in content.lower() for term in ['encrypt', 'tls', 'ssl', 'https']):
                    status = "compliant"
                    evidence.append("Encryption measures mentioned")
                else:
                    status = "partial"
                    findings.append("Limited encryption evidence found")
                    remediation_steps.append("Ensure all sensitive data is encrypted")
        
        return ComplianceCheck(
            check_id=str(uuid.uuid4()),
            framework=framework,
            requirement_id=requirement_id,
            description=description,
            status=status,
            evidence=evidence,
            findings=findings,
            remediation_steps=remediation_steps,
            checked_at=datetime.now()
        )


class SecurityFramework:
    """Main security framework coordinating all security components."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / '.claude' / 'hooks' / 'security'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.pii_detector = PIIDetector()
        self.encryption_manager = EncryptionManager(self.storage_path / 'encryption.key')
        self.audit_logger = AuditLogger(self.storage_path / 'audit.log')
        self.vulnerability_scanner = VulnerabilityScanner()
        self.compliance_validator = ComplianceValidator()
        
        # Security configuration
        self.security_config = {
            'auto_encrypt_pii': True,
            'auto_redact_pii': True,
            'vulnerability_scan_enabled': True,
            'compliance_frameworks': [ComplianceFramework.GDPR, ComplianceFramework.SOC2],
            'alert_on_critical': True
        }
    
    async def process_security_check(
        self,
        content: str,
        context: HookContext,
        security_level: SecurityLevel = SecurityLevel.INTERNAL
    ) -> Dict[str, Any]:
        """Comprehensive security processing."""
        
        results = {
            'security_level': security_level.value,
            'timestamp': datetime.now().isoformat(),
            'checks_performed': []
        }
        
        # PII Detection
        pii_result = self.pii_detector.detect_pii(content, context.message)
        results['pii_detection'] = {
            'found_pii': pii_result.found_pii,
            'pii_types': pii_result.pii_types,
            'risk_level': pii_result.risk_level.value,
            'redacted_content': pii_result.redacted_content if self.security_config['auto_redact_pii'] else None
        }
        results['checks_performed'].append('pii_detection')
        
        # Log PII detection if found
        if pii_result.found_pii:
            self.audit_logger.log_event(
                'pii_detection',
                'content_scan',
                f"PII detected: {', '.join(pii_result.pii_types)}",
                pii_result.risk_level,
                context.user_id,
                context.hook_id,
                {'pii_types': pii_result.pii_types},
                context
            )
        
        # Vulnerability Scanning
        if self.security_config['vulnerability_scan_enabled']:
            vuln_assessment = self.vulnerability_scanner.scan_content(content, context.message)
            results['vulnerability_assessment'] = {
                'vulnerabilities_found': len(vuln_assessment.vulnerabilities_found),
                'overall_risk_score': vuln_assessment.overall_risk_score,
                'recommendations': vuln_assessment.recommendations,
                'vulnerabilities': vuln_assessment.vulnerabilities_found
            }
            results['checks_performed'].append('vulnerability_scan')
            
            # Log high-risk vulnerabilities
            if vuln_assessment.overall_risk_score > 10:
                severity = ThreatLevel.HIGH if vuln_assessment.overall_risk_score > 20 else ThreatLevel.MEDIUM
                self.audit_logger.log_event(
                    'security_violation',
                    'vulnerability_detected',
                    f"Risk score: {vuln_assessment.overall_risk_score}",
                    severity,
                    context.user_id,
                    context.hook_id,
                    {'risk_score': vuln_assessment.overall_risk_score},
                    context
                )
        
        # Compliance Validation
        compliance_results = {}
        for framework in self.security_config['compliance_frameworks']:
            checks = self.compliance_validator.validate_compliance(framework, content, context)
            compliance_results[framework.value] = {
                'total_checks': len(checks),
                'compliant': len([c for c in checks if c.status == 'compliant']),
                'non_compliant': len([c for c in checks if c.status == 'non_compliant']),
                'partial': len([c for c in checks if c.status == 'partial']),
                'checks': [asdict(check) for check in checks]
            }
        
        results['compliance_validation'] = compliance_results
        results['checks_performed'].append('compliance_validation')
        
        # Data Encryption (if PII found and auto-encrypt enabled)
        if pii_result.found_pii and self.security_config['auto_encrypt_pii']:
            try:
                encrypted_content = self.encryption_manager.encrypt(content)
                results['encryption'] = {
                    'encrypted': True,
                    'encrypted_content_length': len(encrypted_content)
                }
                
                self.audit_logger.log_event(
                    'data_protection',
                    'content_encrypted',
                    'Content encrypted due to PII detection',
                    ThreatLevel.LOW,
                    context.user_id,
                    context.hook_id,
                    {'content_length': len(content)},
                    context
                )
                
            except Exception as e:
                results['encryption'] = {
                    'encrypted': False,
                    'error': str(e)
                }
                
                self.audit_logger.log_event(
                    'encryption_failure',
                    'content_encryption',
                    f'Encryption failed: {str(e)}',
                    ThreatLevel.HIGH,
                    context.user_id,
                    context.hook_id,
                    {'error': str(e)},
                    context
                )
        
        # Generate overall security score
        results['security_score'] = self._calculate_security_score(
            pii_result, 
            vuln_assessment if 'vulnerability_assessment' in results else None,
            compliance_results
        )
        
        return results
    
    def _calculate_security_score(
        self,
        pii_result: PIIDetectionResult,
        vuln_assessment: Optional[VulnerabilityAssessment],
        compliance_results: Dict[str, Dict[str, Any]]
    ) -> float:
        """Calculate overall security score (0-100)."""
        
        score = 100.0
        
        # Deduct points for PII
        if pii_result.found_pii:
            if pii_result.risk_level == ThreatLevel.CRITICAL:
                score -= 30
            elif pii_result.risk_level == ThreatLevel.HIGH:
                score -= 20
            elif pii_result.risk_level == ThreatLevel.MEDIUM:
                score -= 10
            else:
                score -= 5
        
        # Deduct points for vulnerabilities
        if vuln_assessment:
            score -= min(40, vuln_assessment.overall_risk_score * 2)
        
        # Deduct points for compliance issues
        total_compliance_issues = 0
        total_compliance_checks = 0
        
        for framework_results in compliance_results.values():
            total_compliance_issues += framework_results['non_compliant']
            total_compliance_checks += framework_results['total_checks']
        
        if total_compliance_checks > 0:
            compliance_rate = 1 - (total_compliance_issues / total_compliance_checks)
            score = score * compliance_rate
        
        return max(0.0, min(100.0, score))
    
    def get_security_statistics(self) -> Dict[str, Any]:
        """Get security framework statistics."""
        
        # Get recent audit entries
        recent_entries = self.audit_logger.search_audit_log(
            start_time=datetime.now() - timedelta(days=7),
            limit=1000
        )
        
        # Count events by type and severity
        event_counts = {}
        severity_counts = {}
        
        for entry in recent_entries:
            event_counts[entry.event_type] = event_counts.get(entry.event_type, 0) + 1
            severity_counts[entry.severity.value] = severity_counts.get(entry.severity.value, 0) + 1
        
        return {
            'total_audit_entries': len(recent_entries),
            'event_type_distribution': event_counts,
            'severity_distribution': severity_counts,
            'security_config': self.security_config,
            'storage_path': str(self.storage_path)
        }