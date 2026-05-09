import os
import re
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env if it exists
load_dotenv()

class GroqGenerator:
    """
    Phase 5: Generator using Groq LLM.
    Handles grounded answer generation and formatting.
    """
    
    def __init__(self, model_name: str = None):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
        
        self.client = Groq(api_key=api_key)
        self.model_name = model_name or os.getenv("GROQ_MODEL_NAME", "llama-3.1-8b-instant")

    def _clean_text(self, text: str) -> str:
        """
        Fixes squashed text common in HTML-to-Markdown conversion.
        Example: 'Expense ratio0.75%' -> 'Expense ratio 0.75%'
        """
        # Fix WordNumber
        text = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", text)
        # Fix NumberWord or %Word
        text = re.sub(r"([0-9%])([A-Z])", r"\1 \2", text)
        # Fix excessive whitespace
        return re.sub(r"\s+", " ", text).strip()

    def _clean_sentence(self, text: str) -> str:
        cleaned = self._clean_text(text)
        cleaned = cleaned.replace("EducationMr.", "Education Mr.")
        cleaned = cleaned.replace("ExperiencePrior", "Experience. Prior")
        return cleaned

    def _split_sentences(self, text: str) -> list[str]:
        cleaned = self._clean_sentence(text)
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]

    def _score_sentence(self, sentence: str, question: str) -> int:
        q_tokens = set(re.findall(r"[a-z0-9]+", question.lower()))
        s_tokens = set(re.findall(r"[a-z0-9]+", sentence.lower()))
        overlap = len(q_tokens & s_tokens)
        bonus = 1 if len(sentence) >= 40 else 0
        return overlap * 10 + bonus

    def _build_fallback_answer(self, question: str, context_chunks: list[dict]) -> str:
        """
        Returns a short extractive fallback answer when LLM generation fails.
        """
        best_sentence = ""
        best_score = -1
        for chunk in context_chunks:
            text = (chunk.get("text") or "").strip()
            if text:
                for sentence in self._split_sentences(text):
                    score = self._score_sentence(sentence, question)
                    if score > best_score:
                        best_score = score
                        best_sentence = sentence
        if best_sentence:
            return f"I could not reach the language model right now. Based on available source text: {best_sentence}"
        return "I could not reach the language model right now and do not have enough source text to answer confidently."

    def generate_answer(self, question: str, context_chunks: list[dict]) -> dict:
        """
        Generates a grounded answer based on the provided context.
        Returns a dict containing 'answer', 'citation_url', and 'footer'.
        """
        if not context_chunks:
            return {
                "answer": "I do not have enough information to answer this question from the allowed sources.",
                "citation_url": None,
                "footer": None
            }

        # Keep prompt size bounded to reduce upstream API failures on very large chunks.
        max_chars_per_chunk = 1200
        max_total_chars = 3600
        context_lines = []
        current_total = 0
        for chunk in context_chunks:
            source_url = chunk["metadata"].get("source_url", "")
            raw_text = chunk.get("text", "")
            # Clean text to fix squashed segments like 'Expense ratio0.75%'
            cleaned_text = self._clean_text(raw_text)
            clipped_text = cleaned_text[:max_chars_per_chunk]
            block = f"Source: {source_url}\nContent: {clipped_text}"
            if current_total + len(block) > max_total_chars and context_lines:
                break
            context_lines.append(block)
            current_total += len(block)
        context_text = "\n\n".join(context_lines)
        
        system_prompt = (
            "You are a helpful mutual fund assistant. Use ONLY the provided context to answer. "
            "Follow these rules strictly:\n"
            "1. Answer in at most 3 sentences.\n"
            "2. If the context does not contain the answer, say you don't have enough information.\n"
            "3. Do not offer investment advice or compare funds.\n"
            "4. Do not include URLs in your response text; the system will append the citation automatically."
        )
        
        user_prompt = f"Context:\n{context_text}\n\nQuestion: {question}"
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                max_tokens=300
            )
            raw_answer = completion.choices[0].message.content.strip()
        except Exception as exc:
            print(f"Groq generation failed: {exc}")
            raw_answer = self._build_fallback_answer(question, context_chunks)
        
        # Pick the most relevant citation URL (e.g. from the first chunk)
        citation_url = context_chunks[0]['metadata'].get('source_url')
        
        # Determine the last updated date
        # Fallback to a placeholder if not present, but per policy we should have it. 
        # Since we might not have extracted it perfectly, we fallback to fetched_at or ingestion date.
        dates = [c['metadata'].get('source_last_updated') or c['metadata'].get('fetched_at') for c in context_chunks]
        valid_dates = [d for d in dates if d]
        last_updated = max(valid_dates) if valid_dates else "Unknown Date"
        
        # Format the date if it's in ISO format
        if last_updated != "Unknown Date" and "T" in last_updated:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                last_updated = dt.strftime("%d %b %Y")
            except Exception:
                pass
        
        footer = f"Last updated from sources: {last_updated}"
        
        formatted_answer = f"{raw_answer}\n\nCitation: {citation_url}\n{footer}"
        
        return {
            "answer": raw_answer,
            "citation_url": citation_url,
            "footer": footer,
            "formatted_response": formatted_answer
        }

if __name__ == "__main__":
    # Example usage for verification (requires GROQ_API_KEY)
    try:
        generator = GroqGenerator()
        print(f"Groq Generator initialized with model: {generator.model_name}")
    except ValueError as e:
        print(f"Error: {e}")
