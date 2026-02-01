import os
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional

# --- 1. Blueprints (The "Schemas") ---

class JournalScores(BaseModel):
    happy: int = Field(description="0-100 score for happiness")
    angry: int = Field(description="0-100 score for anger")
    fearful: int = Field(description="0-100 score for low mood")
    surprised: int = Field(description="0-100 score for surprised")
    bad: int = Field(description="0-100 score for bad")
    disgusted: int = Field(description="0-100 score for disgusted")
    sad: int = Field(description="0-100 score for sad")

class AgenticAdvice(BaseModel):
    nuances: List[str] = Field(description="Sub-emotions like 'academic stress' or 'lonely'")
    personalized_suggestion: str = Field(description="Dynamic, friendly advice like 'Try a 10 min walk'")
    is_emergency: bool = Field(description="Must be True if user mentions self-harm or deep crisis")

class SubAnalysis(BaseModel):
    nuances: List[str] = Field(description="Specific nuances like 'lonely', 'guilt', or 'grief'")
    resource_key: str = Field(description="Keywords for resource matching (e.g., 'academic', 'lonely', 'crisis')")

# --- 2. The Agent Wrapper ---

class ExeterWellbeingAgent:
    def __init__(self):
        self.client = genai.Client()
        self.model_id = "gemini-3-flash-preview"
        
        self.CRISIS_CONTACTS = (
            "It sounds like you're going through a very difficult time. Please reach out for professional support:\n"
            "- NHS: Call 111 (Option 2 for Mental Health) or 999 in an emergency.\n"
            "- Samaritans: Call 116 123 (Free, 24/7 support).\n"
        )

    def triage(self, entry: str):
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=f"Analyze this journal entry: {entry}",
            config={
                "response_mime_type": "application/json",
                "response_schema": JournalScores,
            }
        )
        return response.parsed

    def generate_dynamic_support(self, entry: str, top_emotion: str):
        """AI generates personalized advice based on the specific context of the entry."""
        prompt = f"The user is feeling {top_emotion}. Based on their entry: '{entry}', suggest one small, practical self-care activity."
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config={
                "system_instruction": "Suggest general activities (walks, music, hydration). If the user mentions self-harm, set is_emergency to True.",
                "response_mime_type": "application/json",
                "response_schema": AgenticAdvice,
            }
        )
        return response.parsed
    
    def specialize(self, entry: str, top_emotion: str):
        prompt = f"The user feels {top_emotion}. Analyze for sub-emotions in this text: {entry}"
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config={
                "system_instruction": "Identify sub-emotions. Return a 'resource_key' from: academic, lonely, crisis, anxiety, low_mood, general.",
                "response_mime_type": "application/json",
                "response_schema": SubAnalysis,
            }
        )
        return response.parsed

    def run_workflow(self, entry: str):
        print(f"\n[Agent] Processing Entry...")
        
        # 1. Get Scores
        scores = self.triage(entry)
        emotions_dict = scores.model_dump()
        top_emotion = max(emotions_dict, key=emotions_dict.get)
        
        # 2. Pre-emptive Safety Check (Numerical)
        is_crisis_score = scores.sad > 85 or scores.fearful > 90
        
        # 3. Get AI Advice/Nuance
        advice_data = self.generate_dynamic_support(entry, top_emotion)
        
        # Determine final recommendation
        # We trigger crisis if scores are high OR if the AI flagged an emergency
        if is_crisis_score or advice_data.is_emergency:
            final_recommendation = self.CRISIS_CONTACTS
            is_crisis = True
        else:
            final_recommendation = advice_data.personalized_suggestion
            is_crisis = False

        # --- ALWAYS PRINT REGARDLESS OF OUTCOME ---
        print("-" * 30)
        print(f"ANALYSIS COMPLETE")
        print(f"Top Emotion: {top_emotion.upper()}")
        print(f"Scores: {emotions_dict}")
        print(f"Nuances: {advice_data.nuances}")
        print(f"Recommendation: {final_recommendation}")
        print("-" * 30)
        
        return {
            "scores": scores,
            "nuances": advice_data.nuances,
            "recommendation": final_recommendation,
            "is_crisis": is_crisis
        }

# --- 3. Execution ---
agent = ExeterWellbeingAgent()

# Example Test Case
user_journal = "this work is upsetting me"
result = agent.run_workflow(user_journal)
print(result)