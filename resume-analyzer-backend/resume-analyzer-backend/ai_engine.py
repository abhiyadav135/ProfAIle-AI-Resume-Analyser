# ai_engine.py
import re
import spacy
from pyresparser import ResumeParser
from docx import Document
import PyPDF2
import language_tool_python
from sklearn.feature_extraction.text import TfidfVectorizer
import textstat
import nltk
nltk.download('stopwords')
class ResumeAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.grammar_tool = language_tool_python.LanguageTool('en-US')
        with open('action_verbs.txt') as f:
            self.action_verbs = set(line.strip().lower() for line in f)

    def extract_text(self, file_path):
        """Handle PDF/DOCX file parsing with error checking"""
        try:
            if file_path.endswith('.pdf'):
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    return ''.join([page.extract_text() for page in reader.pages if page.extract_text()])
            elif file_path.endswith('.docx'):
                doc = Document(file_path)
                return '\n'.join([para.text for para in doc.paragraphs])
            else:
                raise ValueError("Unsupported file format")
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return ""

    def analyze_resume(self, file_path, job_description=""):
        """Main analysis workflow"""
        text = self.extract_text(file_path)
        if not text:
            return {"error": "Failed to extract text from resume"}
        
        try:
            resume_data = ResumeParser(file_path).get_extracted_data()
        except Exception as e:
            resume_data = {}
            print(f"Error parsing resume: {str(e)}")

        analysis = {
            'missing_sections': self._check_missing_sections(text),
            'format_issues': self._check_format_issues(text),
            'keyword_analysis': self._analyze_keywords(text, job_description),
            'achievement_analysis': self._analyze_achievements(text),
            'grammar_issues': self._check_grammar(text),
            'ats_compatibility': self._check_ats_issues(resume_data),
            'readability': self._assess_readability(text)
        }
        
        return self._generate_report(analysis)

    def _check_missing_sections(self, resume_text):
        """Check for standard sections based on presence of common headers"""
        section_headers = {
            'skills': ['skills', 'technical skills', 'core competencies'],
            'experience': ['experience', 'work experience', 'professional experience', 'employment history'],
            'education': ['education', 'academic background', 'qualifications']
        }

        missing_sections = []
        text_lower = resume_text.lower()

        for section, variants in section_headers.items():
            if not any(header in text_lower for header in variants):
                missing_sections.append(section)

        return missing_sections

    def _check_format_issues(self, text):
        """Detect formatting inconsistencies"""
        issues = []
        # Check for multiple font sizes (simple heuristic)
        font_sizes = re.findall(r'font-size:\d+pt', text)
        if len(set(font_sizes)) > 3:
            issues.append("Too many font size variations")
            
        # Check for proper section headers
        if not re.search(r'\b(Experience|Work History)\b', text, re.I):
            issues.append("Missing clear 'Experience' section header")
            
        return issues

    def _analyze_keywords(self, resume_text, job_description):
        """Compare resume against job description"""
        analysis = {}
        if job_description:
            tfidf = TfidfVectorizer(stop_words='english')
            matrix = tfidf.fit_transform([resume_text, job_description])
            jd_keywords = set(tfidf.get_feature_names_out()[matrix[1].indices])
            resume_keywords = set(tfidf.get_feature_names_out()[matrix[0].indices])
            analysis['missing'] = list(jd_keywords - resume_keywords)[:10]
            analysis['matching'] = list(jd_keywords & resume_keywords)[:10]
        return analysis

    def _analyze_achievements(self, text):
        """Find and evaluate quantifiable achievements"""
        achievements = []
        metric_patterns = [
            r'\$?\d+(?:,\d+)*(?:\.\d+)?\%?',  # Currency/percentages
            r'\d+\+? (?:years?|months?)',     # Time experience
            r'(?:increased|reduced|improved) by \d+%',
        ]

        for line in text.split('\n'):
            line = line.strip()
            if any(re.search(pattern, line, re.I) for pattern in metric_patterns):
                achievements.append({
                    'text': line,
                    'has_metric': True,
                    'verbs': [verb for verb in self.action_verbs if verb in line.lower()]
                })
            elif any(verb in line.lower() for verb in self.action_verbs):
                achievements.append({
                    'text': line,
                    'has_metric': False,
                    'verbs': [verb for verb in self.action_verbs if verb in line.lower()]
                })
                
        return achievements

    def _check_grammar(self, text):
        """Grammar and style checking"""
        matches = self.grammar_tool.check(text)
        return [{
            'message': match.message,
            'suggestion': match.replacements[0] if match.replacements else None,
            'offset': match.offset,
            'length': match.errorLength
        } for match in matches[:20]]  # Limit to top 20 errors

    def _check_ats_issues(self, resume_data):
        """Check ATS compatibility"""
        issues = []
        if resume_data.get('total_experience', 0) < 1:
            issues.append("Experience duration not clear")
        if len(resume_data.get('skills', [])) < 5:
            issues.append("Less than 5 skills listed")
        if 'summary' not in resume_data.get('section_names', []):
            issues.append("Missing professional summary")
        return issues

    def _assess_readability(self, text):
        """Evaluate text structure quality"""
        doc = self.nlp(text)
        long_sentences = [sent.text for sent in doc.sents if len(sent) > 40]
        passive_voice = len(re.findall(r'\b(was|were|been|is|are|am)\b [a-z]+ed\b', text))
        
        return {
            'avg_sentence_length': sum(len(sent) for sent in doc.sents)/len(list(doc.sents)),
            'long_sentences': long_sentences[:5],
            'passive_voice_count': passive_voice,
            'readability_score': textstat.flesch_reading_ease(text)
        }

    def _generate_report(self, analysis):
        """Generate actionable suggestions and summary from analysis"""
        suggestions = []

        # Section completeness
        for section in analysis['missing_sections']:
            suggestions.append(f"Add '{section.capitalize()}' section")

        # Keyword optimization
        if analysis['keyword_analysis'].get('missing'):
            suggestions.append(
                f"Add missing keywords: {', '.join(analysis['keyword_analysis']['missing'][:5])}"
            )

        # Achievement improvements
        for achievement in analysis['achievement_analysis']:
            if not achievement['has_metric']:
                suggestion = f"Add metrics to: '{achievement['text']}'. Example: 'Increased X by Y% using Z'"
                suggestions.append(suggestion)

        # Grammar fixes
        if analysis['grammar_issues']:
            suggestions.append(
                f"Fix {len(analysis['grammar_issues'])} grammar issues. Example: '{analysis['grammar_issues'][0]['message']}'"
            )

        # ATS improvements
        if analysis['ats_compatibility']:
            suggestions.extend(
                [f"ATS Issue: {issue}" for issue in analysis['ats_compatibility']]
            )

        # Readability
        if analysis['readability']['passive_voice_count'] > 3:
            suggestions.append(
                f"Reduce passive voice ({analysis['readability']['passive_voice_count']} instances found)"
            )

        # Summary
        total_achievements = len(analysis['achievement_analysis'])
        with_metrics = sum(1 for a in analysis['achievement_analysis'] if a['has_metric'])
        without_metrics = total_achievements - with_metrics

        summary = {
            'grammar_issues': len(analysis['grammar_issues']),
            'missing_keywords': len(analysis['keyword_analysis'].get('missing', [])),
            'ats_issues': len(analysis['ats_compatibility']),
            'long_sentences': len(analysis['readability']['long_sentences']),
            'achievement_count': total_achievements,
            'achievements_with_metrics': with_metrics,
            'achievements_without_metrics': without_metrics
        }

        return {
            **analysis,
            'summary': summary,
            'suggestions': suggestions
        }