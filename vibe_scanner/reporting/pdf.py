from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, Preformatted
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

class PDFReportGenerator:
    def __init__(self, scan_data: dict, findings: list):
        self.scan_data = scan_data
        self.findings = findings
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#8b5cf6'),
            spaceAfter=30,
            alignment=TA_CENTER,
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1976d2'),
            spaceAfter=12,
            spaceBefore=20,
        ))
        
        self.styles.add(ParagraphStyle(
            name='FindingTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#ffffff'),
            spaceAfter=6,
            spaceBefore=12,
            backColor=colors.HexColor('#1e1e2e'),
            leftIndent=6,
            rightIndent=6,
        ))
        
        self.styles.add(ParagraphStyle(
            name='CodeStyle',
            parent=self.styles['Code'],
            fontSize=8,
            textColor=colors.HexColor('#22c55e'),
            backColor=colors.HexColor('#1a1a2e'),
            leftIndent=10,
            rightIndent=10,
            spaceBefore=6,
            spaceAfter=6,
        ))
        
        self.styles.add(ParagraphStyle(
            name='CVEStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#f97316'),
            spaceBefore=4,
        ))

    def generate(self, output_path: str):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.6*inch,
            leftMargin=0.6*inch,
            topMargin=0.6*inch,
            bottomMargin=0.6*inch,
        )
        
        story = []
        
        # Title Page
        story.append(Spacer(1, 1.5*inch))
        story.append(Paragraph("ONYX Security Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Vulnerability Assessment Report", self.styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        
        meta_info = [
            f"<b>Target:</b> {self.scan_data.get('target_url')}",
            f"<b>Scan ID:</b> {self.scan_data.get('id')}",
            f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"<b>Total Findings:</b> {len(self.findings)}",
        ]
        
        for info in meta_info:
            story.append(Paragraph(info, self.styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
            
        story.append(PageBreak())
        
        # Executive Summary with severity counts
        story.append(Paragraph("Executive Summary", self.styles['SectionHeading']))
        
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        for f in self.findings:
            if f.severity in severity_counts:
                severity_counts[f.severity] += 1
        
        summary_data = [
            ['Severity', 'Count', 'Risk Level'],
            ['CRITICAL', str(severity_counts['CRITICAL']), 'Immediate Action Required'],
            ['HIGH', str(severity_counts['HIGH']), 'Address Within 24 Hours'],
            ['MEDIUM', str(severity_counts['MEDIUM']), 'Address Within 7 Days'],
            ['LOW', str(severity_counts['LOW']), 'Address Within 30 Days'],
            ['INFO', str(severity_counts['INFO']), 'Informational Only'],
        ]
        
        summary_table = Table(summary_data, colWidths=[1.5*inch, 1*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e1e2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fecaca')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#fed7aa')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#fef08a')),
            ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#bfdbfe')),
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#e5e7eb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#374151')),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Risk assessment
        total_risk = severity_counts['CRITICAL'] * 10 + severity_counts['HIGH'] * 5 + severity_counts['MEDIUM'] * 2 + severity_counts['LOW']
        if total_risk > 30:
            risk_level = "CRITICAL - Immediate remediation required"
            risk_color = "red"
        elif total_risk > 15:
            risk_level = "HIGH - Significant security issues detected"
            risk_color = "orange"
        elif total_risk > 5:
            risk_level = "MEDIUM - Moderate security concerns"
            risk_color = "blue"
        else:
            risk_level = "LOW - Minor issues or good security posture"
            risk_color = "green"
        
        story.append(Paragraph(f"<b>Overall Risk Assessment:</b> <font color='{risk_color}'>{risk_level}</font>", self.styles['Normal']))
        story.append(PageBreak())
        
        # Detailed Findings
        story.append(Paragraph("Detailed Findings", self.styles['SectionHeading']))
        
        if not self.findings:
            story.append(Paragraph("✓ No vulnerabilities detected. The target appears to have good security practices in place.", self.styles['Normal']))
        else:
            for i, finding in enumerate(self.findings, 1):
                sev_colors = {
                    "CRITICAL": "#ef4444",
                    "HIGH": "#f97316", 
                    "MEDIUM": "#eab308",
                    "LOW": "#3b82f6",
                    "INFO": "#6b7280"
                }
                sev_color = sev_colors.get(finding.severity, "#6b7280")
                
                # Finding header
                story.append(Paragraph(
                    f"<font color='{sev_color}'>[{finding.severity}]</font> {i}. {finding.name}",
                    self.styles['Heading3']
                ))
                
                # CVE/CWE reference
                if finding.evidence and 'cve_cwe' in finding.evidence:
                    story.append(Paragraph(
                        f"<b>Reference:</b> {finding.evidence['cve_cwe']}",
                        self.styles['CVEStyle']
                    ))
                
                if finding.evidence and 'owasp' in finding.evidence:
                    story.append(Paragraph(
                        f"<b>OWASP:</b> {finding.evidence['owasp']}",
                        self.styles['CVEStyle']
                    ))
                
                # Category and location
                story.append(Paragraph(f"<b>Category:</b> {finding.category}", self.styles['Normal']))
                if finding.location:
                    story.append(Paragraph(f"<b>Location:</b> {finding.location}", self.styles['Normal']))
                
                # Description
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(f"<b>Description:</b>", self.styles['Normal']))
                story.append(Paragraph(finding.description, self.styles['BodyText']))
                
                # Recommendation
                if finding.recommendation:
                    story.append(Spacer(1, 0.1*inch))
                    story.append(Paragraph(f"<b>Remediation Steps:</b>", self.styles['Normal']))
                    # Split recommendation into lines and format
                    rec_lines = finding.recommendation.split('\n')
                    for line in rec_lines:
                        if line.strip().startswith('```'):
                            continue
                        if line.strip():
                            story.append(Paragraph(line, self.styles['BodyText']))
                
                # Evidence
                if finding.evidence:
                    story.append(Spacer(1, 0.1*inch))
                    evidence_str = str({k: v for k, v in finding.evidence.items() if k not in ['cve_cwe', 'owasp', 'owasp_llm', 'references']})
                    if len(evidence_str) > 10:
                        story.append(Paragraph(f"<b>Evidence:</b> <i>{evidence_str[:300]}</i>", self.styles['Normal']))
                
                # References
                if finding.evidence and 'references' in finding.evidence:
                    story.append(Paragraph("<b>References:</b>", self.styles['Normal']))
                    for ref in finding.evidence['references'][:3]:
                        story.append(Paragraph(f"• {ref}", self.styles['Normal']))
                
                story.append(Spacer(1, 0.2*inch))
                story.append(Paragraph("─" * 80, self.styles['Normal']))

        doc.build(story)
        return output_path
