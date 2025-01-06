import streamlit as st
import spacy
import re
from collections import Counter

class SpanishValidator:
    def __init__(self):
        # Load SpaCy model
        @st.cache_resource
        def load_spacy():
            return spacy.load("es_core_news_sm")
        self.nlp = load_spacy()
        
    def validate_text(self, text, vocabulary):
        # Process the text with SpaCy
        doc = self.nlp(text)
        
        # Extract proper nouns and numbers
        proper_nouns = {token.text.lower() for token in doc if token.pos_ == "PROPN"}
        numbers = {token.text.lower() for token in doc if token.like_num}
        
        # Tokenize text into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Count non-compliant words
        non_compliant_words = [
            word for word in words
            if word not in vocabulary and word not in proper_nouns and word not in numbers
        ]
        
        # Count occurrences of each non-compliant word
        error_counts = Counter(non_compliant_words)
        
        return {
            "compliant": len(non_compliant_words) == 0,
            "errors": error_counts
        }

def format_text_with_highlights(text, error_words):
    """Format text with highlighted errors using HTML."""
    error_words_lower = {word.lower() for word in error_words}
    formatted_parts = []
    current_pos = 0
    
    for match in re.finditer(r'\b\w+\b', text):
        # Add text before the word
        formatted_parts.append(text[current_pos:match.start()])
        
        # Get the word and check if it's an error
        word = match.group()
        if word.lower() in error_words_lower:
            formatted_parts.append(f'<span style="color: red">{word}</span>')
        else:
            formatted_parts.append(word)
        
        current_pos = match.end()
    
    # Add any remaining text
    formatted_parts.append(text[current_pos:])
    return ''.join(formatted_parts)

def main():
    st.set_page_config(page_title="Spanish Text Validator", layout="wide")
    
    # Add some custom CSS
    st.markdown("""
        <style>
        .stTextInput > div > div > input {
            font-size: 16px;
        }
        .highlight {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.title("Spanish Text Validator")
    
    # Initialize the validator
    validator = SpanishValidator()
    
    # File uploader for vocabulary
    uploaded_file = st.file_uploader("Load vocabulary file", type=['txt'])
    vocabulary = set()
    
    if uploaded_file is not None:
        # Read vocabulary file
        vocabulary = {line.decode('utf-8').strip().lower() 
                     for line in uploaded_file.readlines() 
                     if line.decode('utf-8').strip()}
        st.success(f"Vocabulary loaded: {len(vocabulary)} words")
    
    # Text input
    text_input = st.text_area("Enter text to validate:", height=200)
    
    # Validate button
    if st.button("Validate Text"):
        if not vocabulary:
            st.warning("Please load a vocabulary file first.")
        elif not text_input.strip():
            st.warning("Please enter some text to validate.")
        else:
            # Validate text
            result = validator.validate_text(text_input, vocabulary)
            
            # Display results
            st.markdown("### Validation Results")
            if result["compliant"]:
                st.markdown('✓ <span style="color:green">The text is compliant with the vocabulary list.</span>', 
                          unsafe_allow_html=True)
            else:
                st.markdown('✗ <span style="color:red">Non-compliant words found:</span>', 
                          unsafe_allow_html=True)
                
                # Display non-compliant words with counts
                for word, count in result["errors"].items():
                    if count > 1:
                        st.markdown(f'• {word} <span style="color:blue">({count} times)</span>', 
                                  unsafe_allow_html=True)
                    else:
                        st.markdown(f'• {word}')
            
            # Display highlighted text
            st.markdown("### Text with Highlighted Errors")
            highlighted_text = format_text_with_highlights(text_input, result["errors"].keys())
            st.markdown(f'<div class="highlight">{highlighted_text}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
