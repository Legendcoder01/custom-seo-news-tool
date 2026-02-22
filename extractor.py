import yake
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure YAKE
# language = "en"
# max_ngram_size = 3
# deduplication_threshold = 0.9
# num_keywords = 10

kw_extractor = yake.KeywordExtractor(
    lan="en", 
    n=3, 
    dedupLim=0.9, 
    top=10, 
    features=None
)

def extract_keywords(text, top_n=10):
    """
    Extracts the most important keywords/phrases from a given text using YAKE.
    """
    if not text or not isinstance(text, str):
        logger.warning("Empty or invalid text provided for extraction.")
        return []
        
    try:
        # We can dynamically adjust top if needed
        kw_extractor.top = top_n
        keywords = kw_extractor.extract_keywords(text)
        
        # YAKE returns (keyword, score) where LOWER score is BETTER
        # Sort just to be sure
        keywords.sort(key=lambda x: x[1])
        
        # Return just the extracted keyword strings
        return [kw[0] for kw in keywords]
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        return []

if __name__ == "__main__":
    # Quick test
    sample_text = """
    OpenAI today announced Sora 2, the successor to its popular video generation AI. 
    The new model can create up to 60 seconds of high-definition video from a simple text prompt.
    Sora 2 is expected to revolutionize the animation and filmmaking industry by lowering the barrier to entry.
    Microsoft has already confirmed it will integrate Sora 2 into its Copilot suite next month.
    """
    
    keywords = extract_keywords(sample_text)
    print("Extracted Keywords:")
    for kw in keywords:
        print(f"- {kw}")
