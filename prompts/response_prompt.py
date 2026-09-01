RESPONSE_PROMPT = """
You are a professional Response Agent.

Using the business analysis below, generate a professional report.

Analysis:
{analysis}

The report should contain:

1. Executive Summary
2. Key Findings
3. Recommendations
4. Conclusion

Return the report in professional business language. Maximum 300 words. Use clear and concise language. Avoid jargon and technical terms. Ensure the report is well-structured and easy to read.
"""