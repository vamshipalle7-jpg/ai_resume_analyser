import re
import math
from typing import Dict, Any, List, Set, Tuple
from collections import Counter
from app.models.schemas import (
    ScoreBreakdown, MissingSkill, ExperienceAnalysis,
    EducationAnalysis, KeywordItem, KeywordAnalysis
)

# Standard Stopwords to ignore in keyword analysis
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
    "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", 
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him", 
    "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me", 
    "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", "only", 
    "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", 
    "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", 
    "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", 
    "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", 
    "why", "with", "would", "you", "your", "yours", "yourself", "yourselves", "will", "can", "must",
    "years", "experience", "work", "job", "candidate", "role", "team", "looking", "company", "ability",
    "skills", "working", "strong", "preferred", "required", "responsibilities", "qualifications", "plus"
}

# High-impact strong action verbs
STRONG_ACTION_VERBS = {
    "architected", "spearheaded", "engineered", "orchestrated", "optimized", "streamlined",
    "pioneered", "implemented", "overhauled", "accelerated", "designed", "developed",
    "executed", "automated", "mentored", "transformed", "championed", "negotiated",
    "generated", "surpassed", "expanded", "maximized", "reduced", "delivered", "deployed",
    "formulated", "established", "led", "founded", "revamped", "scaled", "boosted"
}

WEAK_PASSIVE_VERBS = {
    "assisted", "helped", "worked", "participated", "involved", "responsible", "handled",
    "supported", "contributed", "attempted", "tried", "did", "tasked"
}

# Comprehensive Skill Taxonomy
SKILLS_TAXONOMY: Dict[str, Dict[str, Any]] = {
    # Programming Languages
    "python": {"name": "Python", "category": "Programming Languages", "synonyms": ["py", "python3"]},
    "javascript": {"name": "JavaScript", "category": "Programming Languages", "synonyms": ["js", "es6", "ecmascript"]},
    "typescript": {"name": "TypeScript", "category": "Programming Languages", "synonyms": ["ts"]},
    "java": {"name": "Java", "category": "Programming Languages", "synonyms": ["j2ee", "core java"]},
    "c++": {"name": "C++", "category": "Programming Languages", "synonyms": ["cpp"]},
    "c#": {"name": "C#", "category": "Programming Languages", "synonyms": ["csharp", ".net c#"]},
    "golang": {"name": "Go", "category": "Programming Languages", "synonyms": ["go", "golang"]},
    "rust": {"name": "Rust", "category": "Programming Languages", "synonyms": []},
    "ruby": {"name": "Ruby", "category": "Programming Languages", "synonyms": []},
    "php": {"name": "PHP", "category": "Programming Languages", "synonyms": []},
    "sql": {"name": "SQL", "category": "Programming Languages", "synonyms": ["t-sql", "pl/sql"]},
    "bash": {"name": "Bash / Shell", "category": "Programming Languages", "synonyms": ["shell script", "zsh", "powershell"]},
    "html": {"name": "HTML5", "category": "Programming Languages", "synonyms": ["html", "html5"]},
    "css": {"name": "CSS3", "category": "Programming Languages", "synonyms": ["css", "css3", "sass", "scss"]},
    "swift": {"name": "Swift", "category": "Programming Languages", "synonyms": ["ios swift"]},
    "kotlin": {"name": "Kotlin", "category": "Programming Languages", "synonyms": ["android kotlin"]},

    # Backend Frameworks & Systems
    "fastapi": {"name": "FastAPI", "category": "Backend Frameworks", "synonyms": []},
    "django": {"name": "Django", "category": "Backend Frameworks", "synonyms": ["django rest framework", "drf"]},
    "flask": {"name": "Flask", "category": "Backend Frameworks", "synonyms": []},
    "nodejs": {"name": "Node.js", "category": "Backend Frameworks", "synonyms": ["node", "node.js"]},
    "express": {"name": "Express.js", "category": "Backend Frameworks", "synonyms": ["express", "expressjs"]},
    "nestjs": {"name": "NestJS", "category": "Backend Frameworks", "synonyms": ["nest.js"]},
    "spring boot": {"name": "Spring Boot", "category": "Backend Frameworks", "synonyms": ["spring", "spring-boot"]},
    "rest api": {"name": "RESTful APIs", "category": "Backend Frameworks", "synonyms": ["rest", "rest api", "restful api", "restful"]},
    "graphql": {"name": "GraphQL", "category": "Backend Frameworks", "synonyms": []},
    "grpc": {"name": "gRPC", "category": "Backend Frameworks", "synonyms": ["protocol buffers", "protobuf"]},
    "microservices": {"name": "Microservices", "category": "Architecture", "synonyms": ["microservice architecture"]},
    "celery": {"name": "Celery", "category": "Backend Frameworks", "synonyms": ["task queue", "rabbitmq worker"]},

    # Frontend Frameworks & Libraries
    "react": {"name": "React.js", "category": "Frontend Frameworks", "synonyms": ["react", "reactjs", "react.js"]},
    "nextjs": {"name": "Next.js", "category": "Frontend Frameworks", "synonyms": ["next", "next.js"]},
    "vue": {"name": "Vue.js", "category": "Frontend Frameworks", "synonyms": ["vue", "vuejs", "vue.js"]},
    "angular": {"name": "Angular", "category": "Frontend Frameworks", "synonyms": ["angularjs", "angular 2+"]},
    "tailwind": {"name": "Tailwind CSS", "category": "Frontend Frameworks", "synonyms": ["tailwindcss"]},
    "redux": {"name": "Redux", "category": "Frontend Frameworks", "synonyms": ["redux toolkit", "rtk"]},

    # Databases & Caching
    "postgresql": {"name": "PostgreSQL", "category": "Databases & Storage", "synonyms": ["postgres", "pgsql"]},
    "mysql": {"name": "MySQL", "category": "Databases & Storage", "synonyms": []},
    "mongodb": {"name": "MongoDB", "category": "Databases & Storage", "synonyms": ["mongo", "nosql"]},
    "redis": {"name": "Redis", "category": "Databases & Storage", "synonyms": ["redis cache"]},
    "supabase": {"name": "Supabase", "category": "Databases & Storage", "synonyms": []},
    "firebase": {"name": "Firebase", "category": "Databases & Storage", "synonyms": ["firestore"]},
    "elasticsearch": {"name": "Elasticsearch", "category": "Databases & Storage", "synonyms": ["elastic search", "elk"]},
    "snowflake": {"name": "Snowflake", "category": "Databases & Storage", "synonyms": []},

    # Cloud & DevOps
    "docker": {"name": "Docker", "category": "Cloud & DevOps", "synonyms": ["containerization", "containers"]},
    "kubernetes": {"name": "Kubernetes", "category": "Cloud & DevOps", "synonyms": ["k8s"]},
    "aws": {"name": "Amazon Web Services (AWS)", "category": "Cloud & DevOps", "synonyms": ["amazon web services", "ec2", "s3", "lambda", "ecs"]},
    "azure": {"name": "Microsoft Azure", "category": "Cloud & DevOps", "synonyms": ["azure cloud"]},
    "gcp": {"name": "Google Cloud Platform (GCP)", "category": "Cloud & DevOps", "synonyms": ["google cloud", "gcp"]},
    "ci/cd": {"name": "CI/CD", "category": "Cloud & DevOps", "synonyms": ["continuous integration", "continuous deployment", "github actions", "gitlab ci", "jenkins"]},
    "terraform": {"name": "Terraform", "category": "Cloud & DevOps", "synonyms": ["iac", "infrastructure as code"]},
    "linux": {"name": "Linux", "category": "Cloud & DevOps", "synonyms": ["ubuntu", "debian", "centos", "redhat"]},
    "git": {"name": "Git / GitHub", "category": "Cloud & DevOps", "synonyms": ["version control", "github", "gitlab"]},

    # AI, Machine Learning & Data
    "machine learning": {"name": "Machine Learning", "category": "AI & Data Science", "synonyms": ["ml", "supervised learning"]},
    "deep learning": {"name": "Deep Learning", "category": "AI & Data Science", "synonyms": ["neural networks", "dl"]},
    "pytorch": {"name": "PyTorch", "category": "AI & Data Science", "synonyms": []},
    "tensorflow": {"name": "TensorFlow", "category": "AI & Data Science", "synonyms": ["keras"]},
    "pandas": {"name": "Pandas / NumPy", "category": "AI & Data Science", "synonyms": ["pandas", "numpy", "data analysis"]},
    "scikit-learn": {"name": "Scikit-Learn", "category": "AI & Data Science", "synonyms": ["sklearn"]},
    "llm": {"name": "Large Language Models (LLMs)", "category": "AI & Data Science", "synonyms": ["generative ai", "llms", "gpt", "rag", "langchain", "prompt engineering"]},
    "nlp": {"name": "Natural Language Processing (NLP)", "category": "AI & Data Science", "synonyms": ["nlp", "text mining"]},

    # Testing & Best Practices
    "unit testing": {"name": "Unit Testing & QA", "category": "Testing & Quality", "synonyms": ["pytest", "jest", "tdd", "test driven development", "integration testing"]},
    "agile": {"name": "Agile / Scrum", "category": "Process & Methodologies", "synonyms": ["scrum", "kanban", "sprints"]},
    "system design": {"name": "System Design", "category": "Architecture", "synonyms": ["distributed systems", "high availability", "scalability"]},

    # Soft Skills
    "leadership": {"name": "Leadership & Mentoring", "category": "Leadership & Soft Skills", "synonyms": ["team lead", "mentorship", "mentoring"]},
    "communication": {"name": "Communication & Collaboration", "category": "Leadership & Soft Skills", "synonyms": ["cross-functional", "stakeholder management", "presentation"]}
}


class ATSEngine:
    """
    Production-grade ATS scoring and analysis engine.
    """

    @classmethod
    def analyze(
        cls,
        resume_text: str,
        job_description: str,
        job_title: str = "",
        sections: Dict[str, str] = None
    ) -> Dict[str, Any]:
        sections = sections or {}
        
        # 1. Skills Matching & Missing Skills
        matched_skills, missing_skills, bonus_skills = cls._match_skills(resume_text, job_description)
        skills_score = cls._calculate_skills_score(matched_skills, missing_skills)

        # 2. Experience & Impact Analysis
        experience_analysis = cls._analyze_experience(resume_text, job_description, sections.get("experience", ""))
        experience_score = cls._calculate_experience_score(experience_analysis)

        # 3. Keyword Relevance & Density
        keyword_analysis = cls._analyze_keywords(resume_text, job_description)
        keyword_score = keyword_analysis.density_score

        # 4. Education & Certifications
        education_analysis = cls._analyze_education(resume_text, job_description, sections.get("education", ""))
        education_score = 90 if education_analysis.degree_matched else (75 if education_analysis.highest_degree else 60)
        if education_analysis.certifications_found:
            education_score = min(100, education_score + 10)

        # 5. Formatting & Section Structure
        formatting_score = cls._analyze_formatting(resume_text, sections)

        # Overall ATS Score (Weighted Composite)
        # 35% Skills, 25% Experience, 20% Keywords, 10% Education, 10% Formatting
        composite_score = (
            (skills_score * 0.35) +
            (experience_score * 0.25) +
            (keyword_score * 0.20) +
            (education_score * 0.10) +
            (formatting_score * 0.10)
        )
        ats_score = int(round(composite_score))
        ats_score = max(10, min(100, ats_score))

        match_level = "Exceptional" if ats_score >= 85 else ("Strong" if ats_score >= 70 else ("Moderate" if ats_score >= 50 else "Needs Improvement"))

        score_breakdown = ScoreBreakdown(
            skills=int(skills_score),
            experience=int(experience_score),
            keywords=int(keyword_score),
            education=int(education_score),
            formatting=int(formatting_score)
        )

        return {
            "ats_score": ats_score,
            "match_level": match_level,
            "score_breakdown": score_breakdown,
            "matched_skills": [s["name"] for s in matched_skills],
            "missing_skills": missing_skills,
            "bonus_skills": [s["name"] for s in bonus_skills],
            "experience_analysis": experience_analysis,
            "education_analysis": education_analysis,
            "keyword_analysis": keyword_analysis
        }

    @classmethod
    def _match_skills(cls, resume_text: str, jd_text: str) -> Tuple[List[Dict[str, Any]], List[MissingSkill], List[Dict[str, Any]]]:
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()

        jd_required_skills = []
        resume_present_skills = []

        for skill_key, info in SKILLS_TAXONOMY.items():
            name = info["name"]
            synonyms = [skill_key] + info["synonyms"]
            
            # Check presence in JD
            in_jd = any(cls._contains_term(jd_lower, syn) for syn in synonyms)
            if in_jd:
                jd_required_skills.append(info)

            # Check presence in Resume
            in_resume = any(cls._contains_term(resume_lower, syn) for syn in synonyms)
            if in_resume:
                resume_present_skills.append(info)

        # Calculate Matched, Missing, and Bonus
        matched = [s for s in jd_required_skills if s in resume_present_skills]
        missing_raw = [s for s in jd_required_skills if s not in resume_present_skills]
        bonus = [s for s in resume_present_skills if s not in jd_required_skills]

        # Format Missing Skills with priority and actionable advice
        missing_skills: List[MissingSkill] = []
        for s in missing_raw:
            # Check how frequently it appeared in JD to classify priority
            occurrences = sum(len(re.findall(r'\b' + re.escape(syn) + r'\b', jd_lower)) for syn in [s["name"].lower()] + s.get("synonyms", []))
            is_critical = occurrences >= 2 or any(req_keyword in jd_lower for req_keyword in ["required", "must have", "minimum qualifications"])
            priority = "Critical" if is_critical else "Recommended"
            
            tip = f"Incorporate {s['name']} into your experience bullets or technical skills section with a specific project context."
            if s["category"] == "Cloud & DevOps":
                tip = f"Demonstrate practical hands-on CI/CD or deployment experience using {s['name']}."
            elif s["category"] == "Databases & Storage":
                tip = f"Mention database schema design, querying, or performance tuning involving {s['name']}."

            missing_skills.append(
                MissingSkill(
                    skill=s["name"],
                    priority=priority,
                    category=s["category"],
                    tip=tip
                )
            )

        return matched, missing_skills, bonus

    @staticmethod
    def _contains_term(text: str, term: str) -> bool:
        # Exact word boundary search
        pattern = r'(?:\b|_)' + re.escape(term) + r'(?:\b|_)'
        return bool(re.search(pattern, text, re.IGNORECASE))

    @staticmethod
    def _calculate_skills_score(matched: List[Any], missing: List[MissingSkill]) -> float:
        total = len(matched) + len(missing)
        if total == 0:
            return 75.0
        
        # Critical missing skills carry heavier penalty
        critical_count = sum(1 for m in missing if m.priority == "Critical")
        recommended_count = len(missing) - critical_count

        raw_match_pct = (len(matched) / total) * 100
        penalized_score = raw_match_pct - (critical_count * 4.0) - (recommended_count * 1.5)
        return max(20.0, min(100.0, penalized_score))

    @classmethod
    def _analyze_experience(cls, resume_text: str, jd_text: str, exp_section: str) -> ExperienceAnalysis:
        text_to_eval = exp_section if len(exp_section) > 100 else resume_text
        words = text_to_eval.lower().split()
        
        # 1. Action verb score
        found_strong = set()
        found_weak = set()
        for w in words:
            clean_w = re.sub(r'[^a-z]', '', w)
            if clean_w in STRONG_ACTION_VERBS:
                found_strong.add(clean_w)
            elif clean_w in WEAK_PASSIVE_VERBS:
                found_weak.add(clean_w)

        total_verb_impressions = len(found_strong) + len(found_weak)
        if total_verb_impressions > 0:
            action_verb_score = int(round((len(found_strong) / (total_verb_impressions + 2)) * 100))
        else:
            action_verb_score = 65

        # 2. Quantifiable metrics count (percentages, money, numbers with k/M/B, multipliers)
        metric_matches = re.findall(
            r'(\b\d+(?:\.\d+)?%|\$\d+(?:,\d+)*(?:\.\d+)?(?:k|m|b)?|\b\d+(?:k|m|b)\b|\b\d+\s*(?:times|x|users|clients|engineers|projects|microservices)\b)', 
            text_to_eval, 
            re.IGNORECASE
        )
        quantifiable_metrics_count = len(metric_matches)

        # 3. Estimated years of experience
        years_found = []
        year_spans = re.findall(r'\b(20\d{2}|19\d{2})\s*(?:-|–|—|to)\s*(20\d{2}|present|current)\b', resume_text, re.IGNORECASE)
        current_year = 2026
        for start_str, end_str in year_spans:
            start_yr = int(start_str)
            end_yr = current_year if end_str.lower() in ["present", "current"] else int(end_str)
            if 1980 <= start_yr <= end_yr <= current_year:
                years_found.append(end_yr - start_yr)

        total_years_est = round(sum(years_found), 1) if years_found else 3.0
        # Cap realistic career span
        total_years_est = min(25.0, max(0.5, total_years_est))

        # 4. Seniority detection
        resume_lower = resume_text.lower()
        if any(w in resume_lower for w in ["principal", "staff engineer", "vp of engineering", "head of", "director"]):
            seniority = "Staff / Executive"
        elif any(w in resume_lower for w in ["lead", "architect", "tech lead", "team lead", "manager"]):
            seniority = "Lead / Architect"
        elif any(w in resume_lower for w in ["senior", "sr."]) or total_years_est >= 5:
            seniority = "Senior"
        elif total_years_est >= 2:
            seniority = "Mid-Level"
        else:
            seniority = "Junior / Associate"

        # Check JD expectation
        jd_lower = jd_text.lower()
        req_seniority_match = True
        if "senior" in jd_lower and seniority in ["Junior / Associate"]:
            req_seniority_match = False

        highlights = []
        if quantifiable_metrics_count >= 3:
            highlights.append(f"Strong evidence of quantifiable results ({quantifiable_metrics_count} business/metric indicators detected).")
        else:
            highlights.append("Needs more quantifiable metrics (KPIs, revenue impact, speedups, percentage gains).")

        if len(found_strong) >= 5:
            highlights.append(f"Effective use of high-impact action verbs ({', '.join(list(found_strong)[:4])}).")
        else:
            highlights.append("Elevate bullet points with active verbs like 'Architected', 'Orchestrated', 'Optimized'.")

        bullet_points = [line for line in text_to_eval.split("\n") if line.strip().startswith(("•", "-", "*"))]
        bullet_count = max(len(bullet_points), len(text_to_eval.split("\n\n")))

        summary_verdict = f"Demonstrates {total_years_est} estimated years of practical experience at {seniority} level with an action-orientation score of {action_verb_score}%."

        return ExperienceAnalysis(
            estimated_years=total_years_est,
            detected_seniority=seniority,
            required_seniority_match=req_seniority_match,
            action_verb_score=action_verb_score,
            quantifiable_metrics_count=quantifiable_metrics_count,
            bullet_points_assessed=bullet_count,
            summary_verdict=summary_verdict,
            highlights=highlights
        )

    @staticmethod
    def _calculate_experience_score(exp: ExperienceAnalysis) -> float:
        base = 65.0
        # Bonus for action verbs
        base += (exp.action_verb_score - 50) * 0.3
        # Bonus for metrics
        base += min(15.0, exp.quantifiable_metrics_count * 3.0)
        # Seniority match
        if not exp.required_seniority_match:
            base -= 15.0
        return max(30.0, min(100.0, base))

    @classmethod
    def _analyze_education(cls, resume_text: str, jd_text: str, edu_section: str) -> EducationAnalysis:
        text = (edu_section + "\n" + resume_text).lower()
        
        degree_hierarchy = [
            ("Doctorate / Ph.D.", [r'\bph\.?d\b', r'\bdoctorate\b', r'\bdoctoral\b']),
            ("Master's Degree", [r'\bmaster(?:\'s)?\b', r'\bm\.s\.?\b', r'\bm\.tech\b', r'\bmba\b', r'\bmsc\b']),
            ("Bachelor's Degree", [r'\bbachelor(?:\'s)?\b', r'\bb\.s\.?\b', r'\bb\.tech\b', r'\bb\.e\.?\b', r'\bbsc\b', r'\bundergraduate\b']),
            ("Associate Degree", [r'\bassociate(?:\'s)?\b', r'\ba\.s\.?\b', r'\ba\.a\.?\b']),
            ("Bootcamp / Certificate", [r'\bbootcamp\b', r'\bcertificate\b', r'\bdiploma\b'])
        ]

        detected = []
        highest = None

        for degree_name, patterns in degree_hierarchy:
            if any(re.search(p, text) for p in patterns):
                detected.append(degree_name)
                if not highest:
                    highest = degree_name

        # Certifications
        cert_patterns = [
            "aws certified", "ckad", "cka", "pmp", "cissp", "azure certified",
            "google cloud certified", "scrum master", "comptia", "hashicorp certified"
        ]
        certs_found = [cp.title() for cp in cert_patterns if cp in text]

        # JD match
        jd_lower = jd_text.lower()
        degree_matched = True
        if ("master" in jd_lower or "ph.d" in jd_lower) and highest in ["Associate Degree", "Bootcamp / Certificate", None]:
            degree_matched = False

        verdict = f"Detected {highest or 'general academic/technical background'}."
        if certs_found:
            verdict += f" Includes certifications: {', '.join(certs_found)}."

        return EducationAnalysis(
            detected_degrees=detected,
            highest_degree=highest,
            degree_matched=degree_matched,
            certifications_found=certs_found,
            verdict=verdict
        )

    @classmethod
    def _analyze_keywords(cls, resume_text: str, jd_text: str) -> KeywordAnalysis:
        # Tokenize JD words
        jd_words = re.findall(r'\b[A-Za-z][A-Za-z0-9_-]{2,}\b', jd_text.lower())
        jd_filtered = [w for w in jd_words if w not in STOPWORDS and len(w) > 2]
        jd_counts = Counter(jd_filtered)

        resume_words = re.findall(r'\b[A-Za-z][A-Za-z0-9_-]{2,}\b', resume_text.lower())
        resume_filtered = [w for w in resume_words if w not in STOPWORDS]
        resume_counts = Counter(resume_filtered)

        top_jd_keywords = jd_counts.most_common(20)
        matched_items: List[KeywordItem] = []
        missing_critical: List[str] = []

        total_jd_freq = sum(jd_counts.values()) or 1

        for kw, count in top_jd_keywords:
            res_count = resume_counts.get(kw, 0)
            is_matched = res_count > 0
            importance = "High" if count >= 3 else ("Medium" if count >= 2 else "Low")
            
            matched_items.append(
                KeywordItem(
                    keyword=kw.title(),
                    resume_count=res_count,
                    jd_count=count,
                    matched=is_matched,
                    importance=importance
                )
            )

            if not is_matched and importance == "High":
                missing_critical.append(kw.title())

        # Density score calculation
        matched_count = sum(1 for item in matched_items if item.matched)
        total_items = len(matched_items) or 1
        density_score = int(round((matched_count / total_items) * 100))

        if density_score >= 80:
            recommendation = "Exceptional keyword alignment with high recruiter search visibility."
        elif density_score >= 60:
            recommendation = f"Solid keyword presence, but missing key recurring terms like: {', '.join(missing_critical[:4])}."
        else:
            recommendation = f"Low keyword density. Recruiter search algorithms may screen out this resume. Add high-frequency terms: {', '.join(missing_critical[:5])}."

        return KeywordAnalysis(
            density_score=density_score,
            matched_keywords=matched_items[:12],
            missing_critical_keywords=missing_critical[:8],
            recommendation=recommendation
        )

    @staticmethod
    def _analyze_formatting(resume_text: str, sections: Dict[str, str]) -> float:
        score = 80.0
        # Reward distinct section detection
        detected_sections_count = sum(1 for v in sections.values() if len(v.strip()) > 20)
        score += min(15.0, detected_sections_count * 3.0)

        # Check length (ideal length: 300 to 1200 words)
        words = len(resume_text.split())
        if 350 <= words <= 1100:
            score += 5.0
        elif words < 200 or words > 2000:
            score -= 15.0

        return max(40.0, min(100.0, score))


ats_engine = ATSEngine()
