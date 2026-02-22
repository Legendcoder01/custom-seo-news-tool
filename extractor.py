import sparknlp
from sparknlp.base import DocumentAssembler, Pipeline, LightPipeline
from sparknlp.annotator import (
    SentenceDetector,
    Tokenizer,
    YakeKeywordExtraction
)
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Spark NLP
# Note: Spark NLP requires a JVM. In GitHub Actions, ensure Java is installed.
try:
    logger.info("Starting Spark NLP Session...")
    spark = sparknlp.start()
    
    # Define the Spark NLP Pipeline
    document = DocumentAssembler() \
                .setInputCol("text") \
                .setOutputCol("document")

    sentenceDetector = SentenceDetector() \
                .setInputCols("document") \
                .setOutputCol("sentence")

    token = Tokenizer() \
                .setInputCols("sentence") \
                .setOutputCol("token") \
                .setContextChars(["(", ")", "?", "!", ".", ","])

    keywords = YakeKeywordExtraction() \
                .setInputCols("token") \
                .setOutputCol("keywords") \
                .setNKeywords(10) \
                .setMinNGrams(1) \
                .setMaxNGrams(3)

    yake_pipeline = Pipeline(stages=[document, sentenceDetector, token, keywords])
    
    # Create an empty dataframe to "fit" the pipeline
    empty_df = spark.createDataFrame([['']]).toDF("text")
    yake_Model = yake_pipeline.fit(empty_df)
    
    # Use LightPipeline for fast local processing
    light_model = LightPipeline(yake_Model)
    logger.info("Spark NLP Keyword Extraction Pipeline initialized.")
    
except Exception as e:
    logger.error(f"Failed to initialize Spark NLP: {e}")
    light_model = None

def extract_keywords(text, top_n=10):
    """
    Extracts the most important keywords/phrases from a given text using Spark NLP YAKE.
    """
    if not text or not isinstance(text, str):
        return []
        
    if not light_model:
        logger.error("Spark NLP model not initialized. Keyword extraction failed.")
        return []

    try:
        # LightPipeline.fullAnnotate returns a list of dictionaries
        light_result = light_model.fullAnnotate(text)[0]
        
        # Extract keywords from the 'keywords' annotation
        # Format: result contains the keyword, metadata contains the score
        extracted = []
        for k in light_result.get('keywords', []):
            extracted.append((k.result, float(k.metadata['score'])))
            
        # YAKE scores: Lower is more relevant.
        extracted.sort(key=lambda x: x[1])
        
        # Return unique keywords (deduplicated)
        seen = set()
        unique_keywords = []
        for kw, score in extracted:
            kw_lower = kw.lower()
            if kw_lower not in seen:
                unique_keywords.append(kw)
                seen.add(kw_lower)
            if len(unique_keywords) >= top_n:
                break
                
        return unique_keywords
    except Exception as e:
        logger.error(f"Error during Spark NLP keyword extraction: {e}")
        return []

if __name__ == "__main__":
    # Quick test
    sample_text = """
    OpenAI today announced Sora 2, the successor to its popular video generation AI. 
    The new model can create up to 60 seconds of high-definition video from a simple text prompt.
    Sora 2 is expected to revolutionize the animation and filmmaking industry by lowering the barrier to entry.
    Microsoft has already confirmed it will integrate Sora 2 into its Copilot suite next month.
    """
    
    results = extract_keywords(sample_text)
    print("Extracted Keywords (Spark NLP):")
    for kw in results:
        print(f"- {kw}")
