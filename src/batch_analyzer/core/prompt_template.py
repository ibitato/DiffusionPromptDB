"""
Prompt Template for Claude Analysis

This module provides the prompt template used to instruct Claude
to analyze and categorize Stable Diffusion prompts.
"""

import json


class PromptTemplate:
    """Template for generating analysis prompts for Claude."""
    
    SYSTEM_PROMPT = """You are an expert at analyzing Stable Diffusion prompts and extracting structured information.

Your task is to analyze prompts used for AI image generation and categorize them into specific fields.
You must return ONLY a valid JSON object following the exact schema provided, with no additional text or explanation.

Be thorough and accurate in your categorization. Extract all relevant information present in the prompt."""

    ANALYSIS_TEMPLATE = """Analyze the following Stable Diffusion prompt and extract structured information according to the schema below.

PROMPT TO ANALYZE:
{prompt_text}

REQUIRED OUTPUT SCHEMA:
Return a JSON object with these exact fields:

{{
  "character": {{
    "number_of_people": <integer: exact count of people/characters, 0 if none, 1, 2, 3, etc.>,
    "genders": [<array: "female", "male", "mixed", "non-binary", "unspecified", "futanari", etc.>],
    "age_ranges": [<array: age for each person - "child", "teen", "young adult", "adult", "mature", "elderly", "loli", "milf", etc.>],
    "body_types": [<array: "petite", "slim", "athletic", "curvy", "muscular", "voluptuous", "chubby", "plus size", "hourglass", "pear", "fit", etc.>],
    "hair": {{
      "colors": [<array: "blonde", "black", "brown", "red", "blue", "pink", "white", "silver", "multicolored", etc.>],
      "styles": [<array: "long", "short", "ponytail", "braided", "curly", "straight", "wavy", "bun", "pigtails", "twin tails", etc.>],
      "lengths": [<array: "short", "medium", "long", "very long", "waist-length", "floor-length", etc.>]
    }},
    "eyes": {{
      "colors": [<array: "blue", "brown", "green", "red", "heterochromia", "golden", "purple", etc.>],
      "shapes": [<array: "large", "narrow", "almond", "round", etc.>]
    }},
    "skin_tones": [<array: "pale", "fair", "tan", "dark", "ebony", "olive", "bronze", "porcelain", etc.>],
    "facial_features": [<array: "freckles", "makeup", "lipstick", "eyeshadow", "blush", "facial hair", "beard", "mustache", "beauty mark", "mole", etc.>],
    "ethnicities": [<array: "caucasian", "asian", "latina", "african", "middle eastern", "mixed", "japanese", "korean", "chinese", etc.>],
    "species": [<array: "human", "elf", "demon", "angel", "furry", "kemonomimi", "catgirl", "monster girl", "alien", "vampire", "werewolf", etc.>],
    "breast_size": "<string: if mentioned - 'flat', 'small', 'medium', 'large', 'huge', 'gigantic', or specific cup sizes, 'unspecified'>",
    "physical_attributes": [<array: "tattoos", "piercings", "scars", "wings", "horns", "tail", "animal ears", "fangs", "muscles", "abs", "thick thighs", "wide hips", "pregnant", "wet", "oiled", "glossy", "shiny", etc.>]
  }},
  "pose": {{
    "main_pose": "<string: primary pose like 'standing', 'sitting', 'lying', 'portrait', etc.>",
    "body_position": "<string: details like 'arched back', 'legs apart', 'arms up', etc.>",
    "view_angle": "<string: 'front view', 'from behind', 'side view', 'dutch angle', etc.>",
    "actions": [<array of strings: actions being performed>]
  }},
  "clothing": {{
    "style": "<string: overall style like 'casual', 'formal', 'fantasy', 'modern', etc.>",
    "items": [<array of strings: specific clothing items mentioned>],
    "coverage": "<string: 'fully clothed', 'partial', 'minimal', 'nude', 'topless', etc.>",
    "accessories": [<array of strings: jewelry, gloves, belts, etc.>]
  }},
  "setting": {{
    "location_type": "<string: type of location>",
    "indoor_outdoor": "<string: 'indoor', 'outdoor', 'mixed', 'unclear'>",
    "specific_place": "<string: specific place if mentioned, e.g., 'barn', 'bedroom', 'city', 'jungle'>",
    "environment_details": [<array of strings: furniture, plants, architecture, props, etc.>]
  }},
  "lighting": {{
    "type": "<string: lighting type like 'cinematic', 'natural', 'dramatic', 'studio', etc.>",
    "time_of_day": "<string: 'sunrise', 'day', 'sunset', 'night', 'unspecified'>",
    "quality": [<array of strings: lighting quality descriptors>]
  }},
  "art_style": {{
    "primary_style": "<string: main style like 'realistic', 'anime', 'photorealistic', '3D', etc.>",
    "quality_tags": [<array of strings: 'masterpiece', 'best quality', 'high detail', etc.>],
    "technique": [<array of strings: techniques mentioned>],
    "score_indicators": [<array of strings: any score tags like 'score_9', 'score_8_up', etc.>]
  }},
  "technical": {{
    "resolution": [<array of strings: '8K', '4K', 'high res', etc.>],
    "camera_settings": [<array of strings: 'depth of field', 'bokeh', 'motion blur', etc.>],
    "detail_level": [<array of strings: 'ultra detailed', 'highly detailed', 'intricate', etc.>]
  }},
  "nsfw_content": {{
    "level": "<string: 'safe', 'suggestive', or 'explicit'>",
    "elements": [<array of strings: specific NSFW elements if present, empty if safe>]
  }},
  "mood_atmosphere": {{
    "overall_mood": "<string: overall emotional tone>",
    "emotions": [<array of strings: emotions expressed or implied>]
  }},
  "sexual_content": {{
    "sexual_acts": [<array: specific acts - "penetration", "oral", "masturbation", "fingering", "anal", "vaginal", "titjob", "handjob", "blowjob", "cunnilingus", etc.>],
    "sexual_positions": [<array: "missionary", "cowgirl", "reverse cowgirl", "doggystyle", "standing", "69", "spooning", etc.>],
    "body_fluids": [<array: "cum", "pussy juice", "sweat", "saliva", "precum", "squirt", etc.>],
    "genital_visibility": "<string: 'none', 'covered', 'partially visible', 'visible', 'explicit focus'>",
    "fetishes": [<array: "BDSM", "voyeur", "exhibitionism", "feet", "lactation", "pregnant", "ahegao", "tentacles", "furry", "incest", etc.>]
  }},
  "relationships": {{
    "interaction_type": "<string: 'solo', 'couple', 'threesome', 'group', 'orgy', 'voyeur', 'exhibitionist', etc.>",
    "relationship": "<string: relationship if mentioned - 'strangers', 'couple', 'family', 'friends', 'teacher-student', 'boss-employee', etc.>",
    "pov_perspective": "<string: 'first person POV', 'third person', 'female POV', 'male POV', 'viewer POV', 'none specified'>"
  }},
  "references": {{
    "character_names": [<array: named characters from anime/games/media, e.g., "makima", "nanakusa nazuna", "yi xuan", etc.>],
    "series_franchise": [<array: series names like "chainsaw man", "yofukashi no uta", "zenless zone zero", etc.>],
    "artist_references": [<array: artist names or style tags like "incase", "moriimee", "akaonimge", etc.>]
  }},
  "camera_composition": {{
    "shot_type": "<string: 'closeup', 'face closeup', 'wide shot', 'full body', 'partial body', 'face focus', 'upper body', 'lower body', etc.>",
    "camera_angle": "<string: 'from above', 'from below', 'dutch angle', 'eye level', 'bird eye view', 'worm eye view', etc.>",
    "focus_area": "<string: main focus of composition - 'face', 'breasts', 'genitals', 'full body', 'ass', 'feet', etc.>",
    "composition_notes": [<array: "foreshortening", "dynamic angle", "dynamic pose", "stationary camera", "movie perspective", etc.>]
  }},
  "main_tags": [<array of 15-20 most important/relevant tags from the prompt>]
}}

INSTRUCTIONS:
1. Extract information that is explicitly present in the prompt
2. Use "unspecified", "unclear", or "none" for missing information
3. For nsfw_content.level, classify as:
   - "safe": No sexual or nude content
   - "suggestive": Implied sexuality, revealing clothing, seductive poses
   - "explicit": Nudity, sexual acts, explicit anatomical references
4. Be comprehensive but accurate - don't invent information not in the prompt
5. Maintain consistent categorization standards
6. Return ONLY the JSON object, no additional text

OUTPUT (JSON only):"""

    @classmethod
    def generate_analysis_prompt(cls, prompt_text: str) -> dict:
        """
        Generate a complete analysis request for Claude.
        
        Args:
            prompt_text: The Stable Diffusion prompt to analyze
            
        Returns:
            dict: Dictionary with 'system' and 'messages' for Claude API
        """
        user_message = cls.ANALYSIS_TEMPLATE.format(prompt_text=prompt_text)
        
        return {
            "system": cls.SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        }
    
    @classmethod
    def generate_batch_request(cls, prompt_id: int, prompt_text: str, 
                              model_id: str, max_tokens: int = 2000,
                              temperature: float = 0.0) -> dict:
        """
        Generate a single batch request in Bedrock Batch API format.
        
        Args:
            prompt_id: Unique identifier for the prompt
            prompt_text: The Stable Diffusion prompt to analyze
            model_id: Bedrock model ID
            max_tokens: Maximum tokens for response
            temperature: Sampling temperature
            
        Returns:
            dict: Batch request formatted for Bedrock
        """
        analysis_request = cls.generate_analysis_prompt(prompt_text)
        
        return {
            "recordId": str(prompt_id),
            "modelInput": {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": analysis_request["system"],
                "messages": analysis_request["messages"]
            }
        }
    
    @classmethod
    def parse_response(cls, response_text: str) -> dict:
        """
        Parse Claude's JSON response.
        
        Args:
            response_text: Raw response from Claude
            
        Returns:
            dict: Parsed JSON response
            
        Raises:
            ValueError: If response is not valid JSON
        """
        try:
            # Claude might wrap JSON in markdown code blocks
            text = response_text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response_text[:500]}")
    
    @classmethod
    def validate_response_structure(cls, response: dict) -> bool:
        """
        Validate that response has required fields.
        
        Args:
            response: Parsed response dictionary
            
        Returns:
            bool: True if valid structure
        """
        required_fields = [
            "character", "pose", "clothing", "setting", 
            "lighting", "art_style", "technical", 
            "nsfw_content", "mood_atmosphere", "main_tags"
        ]
        
        return all(field in response for field in required_fields)
