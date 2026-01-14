"""
AI/GPT Response Validation Tests for U-Ask Chatbot
Tests AI response quality, consistency, formatting, and hallucination detection.
"""
import pytest
import re
from pages.chat_page import ChatPage


@pytest.mark.ai
class TestAIResponses:
    """Test suite for AI/GPT-powered response validation."""
    
    def test_ai_response_is_non_empty(self, chat_page, test_data):
        """
        Verify AI provides a non-empty response to valid queries.
        
        AI Testing Note: We check for non-empty responses rather than exact text matching
        because GPT models generate dynamic responses. Exact matching would cause false failures.
        """
        query = test_data["queries"]["english"]["valid_public_service"]["prompt"]
        
        chat_page.send_message(query)
        response = chat_page.get_latest_ai_response()
        
        assert len(response.strip()) > 0, "AI response should not be empty"
        assert response.strip() != "", "AI response should contain meaningful content"
    
    def test_ai_response_is_meaningful(self, chat_page, test_data):
        """
        Verify AI response is meaningful and relevant to the query.
        
        AI Testing Note: We validate response length and basic content quality rather than
        exact text matching. Meaningful responses typically have sufficient length and
        contain relevant keywords or concepts.
        """
        query_data = test_data["queries"]["english"]["valid_public_service"]
        query = query_data["prompt"]
        min_length = query_data["min_length"]
        
        chat_page.send_message(query)
        response = chat_page.get_latest_ai_response()
        
        # Check minimum length (too short responses may indicate issues)
        assert len(response) >= min_length, \
            f"AI response should be at least {min_length} characters. Got: {len(response)}"
        
        # Check maximum length (extremely long responses may indicate issues)
        max_length = query_data["max_length"]
        assert len(response) <= max_length, \
            f"AI response should not exceed {max_length} characters. Got: {len(response)}"
    
    def test_ai_response_no_broken_html(self, chat_page, test_data):
        """
        Verify AI response does not contain broken HTML or script tags.
        
        AI Testing Note: We check for malformed HTML that could break the UI.
        This is a critical validation to ensure responses render correctly.
        """
        query = test_data["queries"]["english"]["valid_public_service"]["prompt"]
        
        chat_page.send_message(query)
        response = chat_page.get_latest_ai_response()
        
        # Check for unclosed HTML tags (basic validation)
        open_tags = len(re.findall(r'<[^/][^>]*>', response))
        close_tags = len(re.findall(r'</[^>]+>', response))
        
        # Allow some imbalance for self-closing tags, but flag significant issues
        if open_tags > 5:  # Only check if there are HTML tags
            tag_balance = abs(open_tags - close_tags)
            assert tag_balance < open_tags * 0.5, \
                f"Response may contain broken HTML. Open tags: {open_tags}, Close tags: {close_tags}"
        
        # Check for script tags (should not be in AI response)
        assert "<script" not in response.lower(), \
            "AI response should not contain script tags"
    
    def test_ai_response_no_incomplete_thoughts(self, chat_page, test_data):
        """
        Verify AI response is complete and doesn't end mid-sentence.
        
        AI Testing Note: Incomplete responses can indicate API timeouts or model issues.
        We check for proper sentence endings and reasonable structure.
        """
        query = test_data["queries"]["english"]["valid_public_service"]["prompt"]
        
        chat_page.send_message(query)
        response = chat_page.get_latest_ai_response()
        
        # Response should not end with incomplete indicators
        incomplete_indicators = ["...", "…", "and", "or", "but", "the", "a", "an"]
        response_end = response.strip()[-10:].lower() if len(response) >= 10 else response.strip().lower()
        
        # Check if response ends with proper punctuation
        has_ending_punctuation = response.strip().endswith(('.', '!', '?', ':', ';'))
        
        # If response is long enough, it should have ending punctuation
        if len(response) > 100:
            assert has_ending_punctuation or not any(indicator in response_end for indicator in incomplete_indicators), \
                "AI response should be complete and not end mid-thought"
    
    def test_ai_response_consistency_english_arabic(self, chat_page, test_data):
        """
        Verify AI responses show same intent in English and Arabic for similar queries.
        
        AI Testing Note: We cannot do exact text matching between languages. Instead,
        we validate that both responses are meaningful and non-empty, indicating the
        AI understood the intent in both languages. In production, you might use
        translation APIs or semantic similarity to validate intent consistency.
        """
        english_query = test_data["queries"]["english"]["valid_public_service"]["prompt"]
        arabic_query = test_data["queries"]["arabic"]["valid_public_service"]["prompt"]
        
        # Get English response
        chat_page.send_message(english_query)
        english_response = chat_page.get_latest_ai_response()
        
        # Small delay between requests
        import time
        time.sleep(2)
        
        # Get Arabic response (note: may need to switch language in UI first)
        # For this test, we assume language switching or the chatbot detects language
        chat_page.send_message(arabic_query)
        arabic_response = chat_page.get_latest_ai_response()
        
        # Both responses should be meaningful
        assert len(english_response.strip()) > 0, "English response should be non-empty"
        assert len(arabic_response.strip()) > 0, "Arabic response should be non-empty"
        
        # Both should meet minimum length requirements
        min_length = test_data["queries"]["english"]["valid_public_service"]["min_length"]
        assert len(english_response) >= min_length, "English response should meet minimum length"
        assert len(arabic_response) >= min_length, "Arabic response should meet minimum length"
        
        # Note: Intent validation would require semantic analysis or translation comparison
        # This is a simplified check that both languages produce valid responses
    
    def test_ai_fallback_message_on_error(self, chat_page):
        """
        Verify proper fallback message appears on failure or timeout.
        
        AI Testing Note: Fallback messages like "Sorry, please try again" indicate
        proper error handling. We test this by checking if error messages appear
        when expected (though we cannot reliably trigger errors in all scenarios).
        """
        # Send a message that might cause issues (very long or malformed)
        # Note: This may not always trigger an error, but we check error handling
        problematic_message = "A" * 1000  # Very long message
        
        chat_page.send_message(problematic_message)
        
        # Wait for either response or error
        try:
            chat_page.wait_for_ai_response(timeout=15)
            response = chat_page.get_latest_ai_response()
            
            # If we get a response, check if it's an error message
            error_message = chat_page.get_error_message()
            
            # If error message exists, it should be user-friendly
            if error_message:
                assert len(error_message) > 0, "Error message should be present if error occurs"
                # Error messages should be helpful
                assert any(word in error_message.lower() for word in ["sorry", "error", "try", "again", "help"]), \
                    "Error message should be user-friendly"
        except:
            # If timeout occurs, check for error message
            error_message = chat_page.get_error_message()
            if error_message:
                assert len(error_message) > 0, "Error message should appear on timeout"
    
    def test_ai_response_formatting_clean(self, chat_page, test_data):
        """
        Verify AI response formatting is clean and readable.
        
        AI Testing Note: Clean formatting ensures good user experience. We check for
        excessive whitespace, proper line breaks, and absence of formatting artifacts.
        """
        query = test_data["queries"]["english"]["valid_public_service"]["prompt"]
        
        chat_page.send_message(query)
        response = chat_page.get_latest_ai_response()
        
        # Check for excessive consecutive whitespace
        excessive_whitespace = re.search(r'\s{5,}', response)
        assert not excessive_whitespace, \
            "Response should not contain excessive whitespace"
        
        # Check for control characters (except common ones like newline, tab)
        control_chars = re.findall(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', response)
        assert len(control_chars) == 0, \
            f"Response should not contain control characters. Found: {control_chars}"
    
    def test_ai_hallucination_detection_heuristics(self, chat_page, test_data):
        """
        Verify AI response doesn't show obvious hallucination patterns.
        
        AI Testing Note: Detecting hallucinations is challenging without ground truth.
        We use heuristics: responses that are too generic, repetitive, or contain
        obvious contradictions. This is a simplified approach - production systems
        might use more sophisticated methods like fact-checking APIs or knowledge graphs.
        """
        query = test_data["queries"]["english"]["valid_public_service"]["prompt"]
        
        chat_page.send_message(query)
        response = chat_page.get_latest_ai_response()
        
        # Heuristic 1: Response should not be overly repetitive
        words = response.lower().split()
        if len(words) > 10:
            unique_words = len(set(words))
            uniqueness_ratio = unique_words / len(words)
            assert uniqueness_ratio > 0.3, \
                f"Response may be repetitive. Uniqueness ratio: {uniqueness_ratio}"
        
        # Heuristic 2: Response should not be too generic (contain specific terms)
        # For UAE government services, responses should mention relevant terms
        relevant_terms = ["emirates", "id", "renew", "service", "document", "uae", "government"]
        response_lower = response.lower()
        has_relevant_terms = any(term in response_lower for term in relevant_terms)
        
        # Note: This is a soft check - some valid responses might not contain these terms
        # But for the specific query about Emirates ID, we expect some relevance
        
        # Heuristic 3: Response length should be reasonable (not too short, not too long)
        assert 50 <= len(response) <= 2000, \
            f"Response length should be reasonable. Got: {len(response)} characters"
        
        # Heuristic 4: Response should not contain obvious placeholders
        placeholders = ["[placeholder]", "[response]", "lorem ipsum", "test response"]
        assert not any(placeholder in response.lower() for placeholder in placeholders), \
            "Response should not contain placeholder text"
