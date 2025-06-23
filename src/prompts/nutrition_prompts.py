"""
MCP Prompts for nutrition-related AI interactions and guidance.
"""

from typing import List, Dict
import structlog
from mcp.types import Prompt

logger = structlog.get_logger(__name__)


class NutritionPrompts:
    """Prompt templates for nutrition-related AI interactions."""
    
    def __init__(self):
        self.prompts = self._initialize_prompts()
    
    def _initialize_prompts(self) -> Dict[str, Dict]:
        """Initialize all nutrition prompt templates."""
        return {
            "analyze_meal_nutrition": {
                "name": "Analyze Meal Nutrition",
                "description": "Analyze the nutritional content and health impact of a meal",
                "arguments": [
                    {"name": "meal_description", "description": "Description of the meal or list of ingredients"},
                    {"name": "dietary_goals", "description": "User's dietary goals or restrictions"},
                    {"name": "health_conditions", "description": "Any relevant health conditions"}
                ],
                "template": """
You are a registered dietitian analyzing a meal for nutritional content and health impact.

Meal to analyze: {meal_description}

User's dietary goals: {dietary_goals}
Health conditions to consider: {health_conditions}

Please provide a comprehensive analysis including:

1. **Nutritional Breakdown**
   - Estimated calories, macronutrients (protein, carbs, fat)
   - Key vitamins and minerals
   - Fiber content and quality

2. **Health Assessment**
   - How well does this meal align with the user's goals?
   - Nutritional strengths of the meal
   - Areas for improvement

3. **Recommendations**
   - Specific suggestions to optimize nutrition
   - Portion size guidance
   - Complementary foods to add

4. **Health Condition Considerations**
   - Any specific concerns or benefits for mentioned conditions
   - Modifications if needed

Be specific, practical, and focus on actionable advice.
"""
            },
            "create_meal_plan": {
                "name": "Create Personalized Meal Plan",
                "description": "Generate a customized meal plan based on user preferences and requirements",
                "arguments": [
                    {"name": "duration", "description": "Duration of meal plan (daily, weekly, monthly)"},
                    {"name": "dietary_requirements", "description": "Dietary restrictions and preferences"},
                    {"name": "calorie_target", "description": "Target daily calories"},
                    {"name": "health_goals", "description": "Specific health or fitness goals"},
                    {"name": "cooking_skills", "description": "User's cooking skill level and time constraints"}
                ],
                "template": """
You are a meal planning expert creating a personalized nutrition plan.

Plan Duration: {duration}
Dietary Requirements: {dietary_requirements}
Daily Calorie Target: {calorie_target}
Health Goals: {health_goals}
Cooking Skills/Time: {cooking_skills}

Create a detailed meal plan that includes:

1. **Meal Structure**
   - Breakfast, lunch, dinner, and snacks
   - Portion sizes and calorie distribution
   - Timing recommendations

2. **Detailed Meal Suggestions**
   - Specific recipes or meal ideas
   - Ingredient lists for each meal
   - Prep time and cooking difficulty

3. **Nutritional Balance**
   - Ensure adequate protein, healthy fats, complex carbs
   - Include variety of vitamins and minerals
   - Meet fiber and hydration needs

4. **Practical Considerations**
   - Shopping list organization
   - Meal prep suggestions
   - Storage and reheating instructions

5. **Flexibility Options**
   - Substitutions for dietary restrictions
   - Quick alternatives for busy days
   - Restaurant/takeout alternatives

Focus on realistic, sustainable meals that align with the user's lifestyle.
"""
            },
            "nutrition_education": {
                "name": "Nutrition Education",
                "description": "Provide educational information about nutrition topics",
                "arguments": [
                    {"name": "topic", "description": "Specific nutrition topic to explain"},
                    {"name": "audience_level", "description": "Knowledge level of audience (beginner, intermediate, advanced)"},
                    {"name": "specific_questions", "description": "Any specific questions about the topic"}
                ],
                "template": """
You are a nutrition educator explaining complex nutrition concepts in an accessible way.

Topic: {topic}
Audience Level: {audience_level}
Specific Questions: {specific_questions}

Please provide educational content that includes:

1. **Clear Explanation**
   - Define key terms and concepts
   - Use appropriate language for the audience level
   - Include relevant scientific background

2. **Practical Applications**
   - How this applies to daily nutrition choices
   - Real-world examples and scenarios
   - Common misconceptions to clarify

3. **Evidence-Based Information**
   - Current scientific understanding
   - Cite reputable sources when relevant
   - Acknowledge areas of ongoing research

4. **Actionable Takeaways**
   - Key points to remember
   - Practical steps to implement
   - How to make informed food choices

5. **Address Specific Questions**
   - Provide detailed answers to any specific questions
   - Offer additional resources for further learning

Make the information engaging, accurate, and practically useful.
"""
            },
            "dietary_assessment": {
                "name": "Dietary Assessment and Recommendations",
                "description": "Assess current dietary patterns and provide improvement recommendations",
                "arguments": [
                    {"name": "current_diet", "description": "Description of current eating patterns"},
                    {"name": "health_metrics", "description": "Relevant health metrics or lab results"},
                    {"name": "lifestyle_factors", "description": "Activity level, stress, sleep, work schedule"},
                    {"name": "improvement_goals", "description": "Specific areas wanting to improve"}
                ],
                "template": """
You are conducting a comprehensive dietary assessment for personalized recommendations.

Current Diet Pattern: {current_diet}
Health Metrics: {health_metrics}
Lifestyle Factors: {lifestyle_factors}
Improvement Goals: {improvement_goals}

Provide a thorough assessment including:

1. **Current Diet Analysis**
   - Nutritional strengths and deficiencies
   - Meal timing and eating patterns
   - Food quality and processing level
   - Hydration status

2. **Health Impact Assessment**
   - How current diet affects health metrics
   - Potential long-term health implications
   - Connection between diet and lifestyle factors

3. **Priority Recommendations**
   - Top 3-5 most impactful changes to make
   - Ranking by importance and feasibility
   - Timeline for implementing changes

4. **Specific Action Plan**
   - Detailed steps for each recommendation
   - Portion guidance and meal timing
   - Shopping and meal prep strategies

5. **Monitoring and Adjustment**
   - How to track progress
   - Signs of improvement to watch for
   - When to reassess and adjust plan

Focus on sustainable, evidence-based changes that fit the person's lifestyle.
"""
            },
            "food_safety_guidance": {
                "name": "Food Safety Guidance",
                "description": "Provide food safety information and best practices",
                "arguments": [
                    {"name": "food_situation", "description": "Specific food safety situation or question"},
                    {"name": "food_types", "description": "Types of foods involved"},
                    {"name": "storage_conditions", "description": "Current or planned storage conditions"},
                    {"name": "risk_factors", "description": "Any special risk factors (pregnancy, immunocompromised, etc.)"}
                ],
                "template": """
You are a food safety expert providing guidance on safe food handling and consumption.

Food Situation: {food_situation}
Food Types: {food_types}
Storage Conditions: {storage_conditions}
Risk Factors: {risk_factors}

Provide comprehensive food safety guidance including:

1. **Immediate Safety Assessment**
   - Is the current situation safe?
   - Any immediate actions needed?
   - Risk level evaluation

2. **Safe Handling Practices**
   - Proper storage temperatures and times
   - Preparation and cooking guidelines
   - Cross-contamination prevention

3. **Risk-Specific Considerations**
   - Special precautions for high-risk individuals
   - Foods to avoid in specific situations
   - Enhanced safety measures when needed

4. **Temperature and Time Guidelines**
   - Safe internal cooking temperatures
   - Maximum storage times
   - Danger zone awareness

5. **Signs of Spoilage**
   - What to look for in different food types
   - When to discard food
   - How to prevent foodborne illness

Prioritize safety while providing practical, actionable advice.
"""
            },
            "supplement_guidance": {
                "name": "Supplement and Nutrient Guidance",
                "description": "Provide evidence-based information about dietary supplements and nutrients",
                "arguments": [
                    {"name": "supplements_of_interest", "description": "Specific supplements or nutrients being considered"},
                    {"name": "health_status", "description": "Current health status and any medications"},
                    {"name": "dietary_intake", "description": "Current dietary intake and restrictions"},
                    {"name": "specific_goals", "description": "Health goals or deficiency concerns"}
                ],
                "template": """
You are providing evidence-based guidance on dietary supplements and nutrient needs.

Supplements of Interest: {supplements_of_interest}
Health Status: {health_status}
Current Diet: {dietary_intake}
Specific Goals: {specific_goals}

Provide comprehensive supplement guidance including:

1. **Nutrient Assessment**
   - Likelihood of deficiency based on diet and health status
   - Body's actual needs vs. supplement marketing claims
   - Food sources vs. supplement sources

2. **Evidence-Based Recommendations**
   - What the research shows about effectiveness
   - Appropriate dosages and forms
   - Quality and bioavailability considerations

3. **Safety Considerations**
   - Potential interactions with medications
   - Upper intake limits and toxicity risks
   - Contraindications for specific health conditions

4. **Food-First Approach**
   - How to meet needs through whole foods
   - Specific food recommendations
   - When supplements may be necessary

5. **Practical Guidance**
   - How to choose quality supplements if needed
   - Timing and absorption optimization
   - Monitoring for effectiveness

Always emphasize that supplements should complement, not replace, a healthy diet.
"""
            },
            "recipe_nutrition_optimization": {
                "name": "Recipe Nutrition Optimization",
                "description": "Analyze and optimize recipes for better nutrition while maintaining taste",
                "arguments": [
                    {"name": "original_recipe", "description": "The original recipe to analyze and optimize"},
                    {"name": "nutrition_goals", "description": "Specific nutritional improvements desired"},
                    {"name": "dietary_restrictions", "description": "Any dietary restrictions to accommodate"},
                    {"name": "taste_preferences", "description": "Taste and texture preferences to maintain"}
                ],
                "template": """
You are a culinary nutritionist optimizing recipes for better nutrition while preserving flavor.

Original Recipe: {original_recipe}
Nutrition Goals: {nutrition_goals}
Dietary Restrictions: {dietary_restrictions}
Taste Preferences: {taste_preferences}

Provide recipe optimization including:

1. **Nutritional Analysis of Original**
   - Current macro and micronutrient profile
   - Calorie density and portion considerations
   - Nutritional strengths and weaknesses

2. **Optimization Strategies**
   - Ingredient substitutions with rationale
   - Cooking method modifications
   - Portion size adjustments

3. **Enhanced Recipe Version**
   - Complete optimized recipe with measurements
   - Cooking instructions and tips
   - Expected nutritional improvements

4. **Taste and Texture Preservation**
   - How modifications affect flavor profile
   - Tips to maintain appealing taste
   - Optional flavor enhancers

5. **Nutritional Comparison**
   - Before and after nutritional breakdown
   - Percentage improvements in key nutrients
   - Health benefits of modifications

Focus on practical changes that significantly improve nutrition without compromising enjoyment.
"""
            }
        }
    
    async def list_prompts(self) -> List[Prompt]:
        """List all available nutrition prompts."""
        prompts = []
        
        for prompt_id, prompt_data in self.prompts.items():
            # Convert arguments to the expected format
            input_schema = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            for arg in prompt_data["arguments"]:
                input_schema["properties"][arg["name"]] = {
                    "type": "string",
                    "description": arg["description"]
                }
                input_schema["required"].append(arg["name"])
            
            prompt = Prompt(
                name=prompt_id,
                description=prompt_data["description"],
                arguments=input_schema
            )
            prompts.append(prompt)
        
        logger.info("Listed nutrition prompts", count=len(prompts))
        return prompts
    
    async def get_prompt(self, name: str, arguments: Dict[str, str]) -> str:
        """Get a specific prompt with arguments filled in."""
        if name not in self.prompts:
            raise ValueError(f"Unknown prompt: {name}")
        
        prompt_data = self.prompts[name]
        template = prompt_data["template"]
        
        try:
            # Fill in the template with provided arguments
            filled_prompt = template.format(**arguments)
            
            logger.info("Generated prompt", name=name, args=list(arguments.keys()))
            return filled_prompt
            
        except KeyError as e:
            missing_arg = str(e).strip("'")
            raise ValueError(f"Missing required argument for prompt '{name}': {missing_arg}")
        except Exception as e:
            logger.error("Failed to generate prompt", name=name, error=str(e))
            raise ValueError(f"Failed to generate prompt: {str(e)}")
    
    async def analyze_meal_nutrition(
        self,
        meal_description: str,
        dietary_goals: str,
        health_conditions: str = "none"
    ) -> str:
        """Generate a detailed nutrition analysis prompt for a meal."""
        return await self.get_prompt("analyze_meal_nutrition", {
            "meal_description": meal_description,
            "dietary_goals": dietary_goals,
            "health_conditions": health_conditions
        })
    
    async def create_meal_plan(
        self,
        target_calories: int,
        dietary_preferences: str,
        meal_count: int = 3,
        duration_days: int = 7
    ) -> str:
        """Generate a meal planning prompt based on requirements."""
        duration = f"{duration_days} days"
        return await self.get_prompt("create_meal_plan", {
            "duration": duration,
            "dietary_requirements": dietary_preferences,
            "calorie_target": str(target_calories),
            "health_goals": f"Balanced nutrition with {meal_count} meals per day",
            "cooking_skills": "General cooking skills"
        })
    
    async def nutrition_education(
        self,
        topic: str,
        audience_level: str = "general",
        focus_areas: List[str] = None
    ) -> str:
        """Generate nutrition education content prompt."""
        specific_questions = ", ".join(focus_areas) if focus_areas else "General overview"
        return await self.get_prompt("nutrition_education", {
            "topic": topic,
            "audience_level": audience_level,
            "specific_questions": specific_questions
        })
