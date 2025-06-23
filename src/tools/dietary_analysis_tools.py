"""
Dietary analysis tools for analyzing nutritional intake and compliance.
FastMCP compatible implementation.
"""

from typing import List, Dict, Any, Optional
import structlog
from datetime import datetime, timedelta

from ..services.usda_service import USDAService
from ..config import get_settings

logger = structlog.get_logger(__name__)


class DietaryAnalysisTools:
    """Tools for dietary analysis and compliance checking."""
    
    def __init__(self):
        self.usda_service = USDAService()
        self.settings = get_settings()

    async def analyze_daily_intake(
        self,
        daily_meals: List[Dict[str, Any]],
        person_info: Dict[str, Any],
        analysis_focus: Optional[List[str]] = None
    ) -> str:
        """Analyze daily nutritional intake based on meals and person profile.
        Args:
            daily_meals (List[Dict[str, Any]]): List of meals consumed in a day.
            person_info (Dict[str, Any]): Personal information for nutritional recommendations.
            analysis_focus (Optional[List[str]]): Specific nutrients to focus on (e.g., ['protein', 'fiber']).
        Returns:
            str: Formatted analysis report of daily intake.
        """

        try:
            if not daily_meals:
                return "No meal data provided for daily intake analysis."
            
            if not person_info:
                return "Person information is required for personalized analysis."
            
            analysis_focus = analysis_focus or []
            
            # Calculate daily nutrition
            daily_nutrition = await self._calculate_daily_nutrition(daily_meals)
            
            # Get personalized recommendations
            recommendations = self._get_personalized_recommendations(person_info)
            
            # Perform nutritional analysis
            analysis_results = self._perform_nutritional_analysis(
                daily_nutrition, recommendations, analysis_focus
            )
            
            # Format the analysis
            formatted_analysis = self._format_daily_analysis(
                daily_nutrition, analysis_results, daily_meals
            )
            
            logger.info("Daily intake analysis completed", 
                       meals=len(daily_meals), focus_areas=len(analysis_focus))
            return formatted_analysis
            
        except Exception as e:
            logger.error("Error analyzing daily intake", error=str(e))
            return f"Error analyzing daily intake: {str(e)}"

    async def check_compliance(
        self,
        food_log: List[Dict[str, Any]],
        dietary_guidelines: str,
        custom_restrictions: Optional[List[str]] = None
    ) -> str:
        """Check dietary compliance against guidelines and restrictions.
        Args:
            food_log (List[Dict[str, Any]]): List of daily food logs.
            dietary_guidelines (str): Dietary guidelines to check against (e.g., 'mediterranean', 'dash').
            custom_restrictions (Optional[List[str]]): Custom dietary restrictions (e.g., 'gluten-free').
        Returns:
            str: Formatted compliance report.
        """
        try:
            if not food_log:
                return "No food log data provided for compliance checking."
            
            custom_restrictions = custom_restrictions or []
            
            # Assess dietary compliance
            compliance_results = await self._assess_dietary_compliance(
                food_log, dietary_guidelines, custom_restrictions
            )
            
            # Format the compliance report
            formatted_report = self._format_compliance_report(
                compliance_results, dietary_guidelines
            )
            
            logger.info("Dietary compliance checked", 
                       days=len(food_log), guidelines=dietary_guidelines)
            return formatted_report
            
        except Exception as e:
            logger.error("Error checking dietary compliance", error=str(e))
            return f"Error checking dietary compliance: {str(e)}"

    async def generate_report(
        self,
        analysis_period: Dict[str, Any],
        report_type: str = "comprehensive"
    ) -> str:
        """Generate a nutrition report for a specified analysis period.
        Args:
            analysis_period (Dict[str, Any]): Data for the analysis period including daily logs and person profile.
            report_type (str): Type of report to generate ('summary', 'trends', 'comprehensive').
        Returns:
            str: Formatted nutrition report.
        """
        try:
            if not analysis_period:
                return "Analysis period data is required for report generation."
            
            # Analyze nutrition over the period
            period_analysis = await self._analyze_period_nutrition(
                analysis_period.get('daily_logs', []),
                analysis_period.get('person_profile', {})
            )
            
            # Determine report sections based on type
            if report_type == "summary":
                sections = ["overview", "key_metrics"]
            elif report_type == "trends":
                sections = ["trends", "patterns", "recommendations"]
            else:  # comprehensive
                sections = ["overview", "key_metrics", "trends", "patterns", "recommendations"]
            
            # Compile the report
            formatted_report = self._compile_nutrition_report(
                period_analysis, sections, analysis_period
            )
            
            logger.info("Nutrition report generated", 
                       type=report_type, sections=len(sections))
            return formatted_report
            
        except Exception as e:
            logger.error("Error generating nutrition report", error=str(e))
            return f"Error generating nutrition report: {str(e)}"

    async def identify_patterns(
        self,
        eating_data: List[Dict[str, Any]],
        pattern_types: Optional[List[str]] = None
    ) -> str:
        """Identify eating patterns from provided data.
        Args:
            eating_data (List[Dict[str, Any]]): List of eating data entries.
            pattern_types (Optional[List[str]]): Types of patterns to analyze (e.g., 'timing', 'calories').     
        Returns:
            str: Formatted analysis of eating patterns.
        """
        try:
            if not eating_data:
                return "No eating data provided for pattern analysis."
            
            pattern_types = pattern_types or ["timing", "calories", "weekends", "variety"]
            
            # Analyze eating patterns
            patterns = await self._analyze_eating_patterns(eating_data, pattern_types)
            
            # Format the pattern analysis
            formatted_patterns = self._format_pattern_analysis(patterns)
            
            logger.info("Eating patterns identified", 
                       data_points=len(eating_data), patterns=len(pattern_types))
            return formatted_patterns
            
        except Exception as e:
            logger.error("Error identifying eating patterns", error=str(e))
            return f"Error identifying eating patterns: {str(e)}"

    async def _calculate_daily_nutrition(self, daily_meals: list) -> dict:
        """Calculate total nutrition for all meals in a day."""
        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0,
            'sugar': 0,
            'sodium': 0,
            'saturated_fat': 0,
            'cholesterol': 0
        }
        
        for meal in daily_meals:
            foods = meal.get('foods', [])
            for food in foods:
                # Add up nutrition from each food item
                total_nutrition['calories'] += food.get('calories', 0)
                total_nutrition['protein'] += food.get('protein', 0)
                total_nutrition['carbs'] += food.get('carbs', 0)
                total_nutrition['fat'] += food.get('fat', 0)
                total_nutrition['fiber'] += food.get('fiber', 0)
                total_nutrition['sugar'] += food.get('sugar', 0)
                total_nutrition['sodium'] += food.get('sodium', 0)
                total_nutrition['saturated_fat'] += food.get('saturated_fat', 0)
                total_nutrition['cholesterol'] += food.get('cholesterol', 0)
        
        return total_nutrition

    def _get_personalized_recommendations(self, person_info: dict) -> dict:
        """Get personalized nutrition recommendations."""
        age = person_info.get('age', 30)
        gender = person_info.get('gender', 'unknown')
        weight = person_info.get('weight', 70)
        height = person_info.get('height', 170)
        activity_level = person_info.get('activity_level', 'moderate')
        health_goals = person_info.get('health_goals', [])
        
        # Calculate BMR (simplified)
        if gender.lower() == 'male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
        # Activity level multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        multiplier = activity_multipliers.get(activity_level.lower(), 1.55)
        daily_calories = int(bmr * multiplier)
        
        # Adjust for health goals
        if 'weight_loss' in health_goals:
            daily_calories -= 500  # 1 lb per week deficit
        elif 'weight_gain' in health_goals:
            daily_calories += 500  # 1 lb per week surplus
        
        return {
            'calories': daily_calories,
            'protein': weight * 1.2,  # 1.2g per kg
            'carbs': daily_calories * 0.50 / 4,  # 50% of calories
            'fat': daily_calories * 0.25 / 9,  # 25% of calories
            'fiber': 25 if gender.lower() == 'female' else 38,
            'sugar': daily_calories * 0.10 / 4,  # <10% of calories
            'sodium': 2300,  # mg
            'saturated_fat': daily_calories * 0.10 / 9,  # <10% of calories
            'cholesterol': 300  # mg
        }

    def _perform_nutritional_analysis(self, daily_nutrition: dict, recommendations: dict, focus_areas: list) -> dict:
        """Perform nutritional analysis based on focus areas."""
        analysis = {}
        
        # Analyze all nutrients or specific focus areas
        nutrients_to_analyze = focus_areas if focus_areas else list(recommendations.keys())
        
        for nutrient in nutrients_to_analyze:
            if nutrient in daily_nutrition and nutrient in recommendations:
                actual = daily_nutrition[nutrient]
                target = recommendations[nutrient]
                
                # Calculate percentage of target
                percentage = (actual / target * 100) if target > 0 else 0
                
                # Determine status
                status = self._get_nutrient_status(actual, target, nutrient)
                
                analysis[nutrient] = {
                    'actual': actual,
                    'target': target,
                    'percentage': percentage,
                    'status': status
                }
        
        return analysis

    def _get_nutrient_status(self, actual: float, target: float, nutrient_type: str) -> str:
        """Get status of nutrient intake."""
        if target == 0:
            return "no target set"
        
        ratio = actual / target
        
        # For nutrients we want to limit (sodium, sugar, saturated fat)
        if nutrient_type in ['sodium', 'sugar', 'saturated_fat', 'cholesterol']:
            if ratio > 1.1:
                return "above recommended limit"
            elif ratio > 0.9:
                return "near recommended limit"
            else:
                return "within recommended range"
        
        # For nutrients we want to meet or exceed
        else:
            if ratio < 0.8:
                return "significantly below target"
            elif ratio < 0.9:
                return "below target"
            elif ratio <= 1.1:
                return "on target"
            else:
                return "above target"

    async def _assess_dietary_compliance(self, food_log: list, guidelines: str, custom_restrictions: list) -> dict:
        """Assess compliance with dietary guidelines."""
        compliance_results = {
            'overall_score': 0,
            'daily_scores': [],
            'violations': [],
            'recommendations': []
        }
        
        # Get guideline rules
        rules = self._get_guideline_rules(guidelines)
        
        daily_scores = []
        all_violations = []
        
        # Analyze each day
        for day_log in food_log:
            daily_nutrition = await self._calculate_daily_nutrition(day_log.get('meals', []))
            
            # Check compliance for this day
            day_score, violations = self._check_daily_compliance(
                daily_nutrition, rules, custom_restrictions
            )
            
            daily_scores.append(day_score)
            all_violations.extend(violations)
        
        # Calculate overall score
        compliance_results['overall_score'] = sum(daily_scores) / len(daily_scores) if daily_scores else 0
        compliance_results['daily_scores'] = daily_scores
        compliance_results['violations'] = all_violations
        
        # Generate recommendations
        if compliance_results['overall_score'] < 70:
            compliance_results['recommendations'] = [
                "Focus on meeting daily nutrient targets",
                "Reduce processed foods and added sugars",
                "Increase vegetables and whole grains"
            ]
        
        return compliance_results

    def _get_guideline_rules(self, guidelines: str) -> dict:
        """Get rules for specific dietary guidelines."""
        guidelines_map = {
            'mediterranean': {
                'fruits_servings': 3,
                'vegetables_servings': 4,
                'whole_grains': True,
                'fish_weekly': 2,
                'olive_oil': True,
                'nuts_weekly': 3
            },
            'dash': {
                'sodium_limit': 1500,
                'fruits_servings': 4,
                'vegetables_servings': 5,
                'whole_grains_daily': 3,
                'lean_protein': True
            },
            'keto': {
                'carbs_limit': 50,
                'fat_percentage': 70,
                'protein_percentage': 25
            },
            'paleo': {
                'processed_foods': False,
                'grains': False,
                'legumes': False,
                'dairy': False
            }
        }
        
        return guidelines_map.get(guidelines.lower(), {})

    def _check_daily_compliance(self, daily_nutrition: dict, rules: dict, custom_restrictions: list) -> tuple[float, list]:
        """Check compliance for a single day."""
        score = 100
        violations = []
        
        # Check specific rules
        for rule, target in rules.items():
            if rule == 'sodium_limit' and daily_nutrition.get('sodium', 0) > target:
                score -= 15
                violations.append(f"Sodium intake ({daily_nutrition['sodium']:.0f}mg) exceeded limit ({target}mg)")
            
            elif rule == 'carbs_limit' and daily_nutrition.get('carbs', 0) > target:
                score -= 20
                violations.append(f"Carb intake ({daily_nutrition['carbs']:.0f}g) exceeded limit ({target}g)")
        
        # Check custom restrictions
        for restriction in custom_restrictions:
            if restriction.lower() in ['gluten-free', 'dairy-free', 'nut-free']:
                # Simplified check - would need more detailed food composition data
                pass
        
        return max(0, score), violations

    async def _analyze_period_nutrition(self, daily_logs: list, person_profile: dict) -> dict:
        """Analyze nutrition over a period of time."""
        if not daily_logs:
            return {}
        
        period_nutrition = {
            'average_daily': {},
            'trends': {},
            'variability': {},
            'compliance_score': 0
        }
        
        # Calculate daily nutrition for each day
        daily_nutritions = []
        for day_log in daily_logs:
            day_nutrition = await self._calculate_daily_nutrition(day_log.get('meals', []))
            daily_nutritions.append(day_nutrition)
        
        # Calculate averages
        nutrients = ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sodium']
        for nutrient in nutrients:
            values = [day.get(nutrient, 0) for day in daily_nutritions]
            period_nutrition['average_daily'][nutrient] = sum(values) / len(values) if values else 0
            period_nutrition['variability'][nutrient] = self._calculate_std_dev(values)
        
        return period_nutrition

    def _calculate_std_dev(self, values: list) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

    async def _analyze_eating_patterns(self, food_diary: list, pattern_types: list) -> dict:
        """Analyze eating patterns over time."""
        patterns = {}
        
        if 'timing' in pattern_types:
            patterns['meal_timing'] = self._analyze_meal_timing(food_diary)
        
        if 'calories' in pattern_types:
            patterns['calorie_trends'] = await self._analyze_calorie_trends(food_diary)
        
        if 'weekends' in pattern_types:
            patterns['weekend_patterns'] = await self._analyze_weekend_patterns(food_diary)
        
        if 'variety' in pattern_types:
            patterns['food_variety'] = self._analyze_food_variety(food_diary)
        
        return patterns

    def _analyze_meal_timing(self, food_diary: list) -> dict:
        """Analyze meal timing patterns."""
        meal_times = {
            'breakfast': [],
            'lunch': [],
            'dinner': []
        }
        
        for day in food_diary:
            meals = day.get('meals', [])
            for meal in meals:
                meal_type = meal.get('type', '').lower()
                meal_time = meal.get('time', '')
                
                if meal_type in meal_times and meal_time:
                    # Convert time to minutes since midnight for analysis
                    try:
                        hour, minute = map(int, meal_time.split(':'))
                        minutes = hour * 60 + minute
                        meal_times[meal_type].append(minutes)
                    except:
                        continue
        
        # Calculate consistency
        timing_analysis = {}
        for meal_type, times in meal_times.items():
            if times:
                avg_time = sum(times) / len(times)
                consistency = self._calculate_time_consistency(times)
                timing_analysis[meal_type] = {
                    'average_time': f"{int(avg_time//60):02d}:{int(avg_time%60):02d}",
                    'consistency': consistency
                }
        
        return timing_analysis

    def _calculate_time_consistency(self, minutes: list) -> str:
        """Calculate consistency of meal timing."""
        if len(minutes) < 2:
            return "insufficient data"
        
        std_dev = self._calculate_std_dev(minutes)
        
        if std_dev < 30:  # Within 30 minutes
            return "very consistent"
        elif std_dev < 60:  # Within 1 hour
            return "consistent"
        elif std_dev < 120:  # Within 2 hours
            return "somewhat variable"
        else:
            return "highly variable"

    async def _analyze_calorie_trends(self, food_diary: list) -> dict:
        """Analyze calorie trends over time."""
        daily_calories = []
        
        for day in food_diary:
            day_nutrition = await self._calculate_daily_nutrition(day.get('meals', []))
            daily_calories.append(day_nutrition.get('calories', 0))
        
        if not daily_calories:
            return {}
        
        avg_calories = sum(daily_calories) / len(daily_calories)
        calorie_variability = self._calculate_std_dev(daily_calories)
        
        # Identify trend direction
        if len(daily_calories) >= 3:
            recent_avg = sum(daily_calories[-3:]) / 3
            early_avg = sum(daily_calories[:3]) / 3
            
            if recent_avg > early_avg * 1.05:
                trend = "increasing"
            elif recent_avg < early_avg * 0.95:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient data"
        
        return {
            'average_calories': avg_calories,
            'variability': calorie_variability,
            'trend': trend,
            'min_calories': min(daily_calories),
            'max_calories': max(daily_calories)
        }

    async def _analyze_weekend_patterns(self, food_diary: list) -> dict:
        """Analyze differences between weekend and weekday eating."""
        weekday_calories = []
        weekend_calories = []
        
        for day in food_diary:
            day_nutrition = await self._calculate_daily_nutrition(day.get('meals', []))
            calories = day_nutrition.get('calories', 0)
            
            # Simplified - would need actual date info
            day_of_week = day.get('day_of_week', 'weekday')
            
            if day_of_week in ['saturday', 'sunday']:
                weekend_calories.append(calories)
            else:
                weekday_calories.append(calories)
        
        analysis = {}
        
        if weekday_calories:
            analysis['weekday_avg'] = sum(weekday_calories) / len(weekday_calories)
        
        if weekend_calories:
            analysis['weekend_avg'] = sum(weekend_calories) / len(weekend_calories)
        
        if weekday_calories and weekend_calories:
            difference = analysis['weekend_avg'] - analysis['weekday_avg']
            analysis['weekend_difference'] = difference
            
            if abs(difference) < 100:
                analysis['pattern'] = "consistent eating pattern"
            elif difference > 100:
                analysis['pattern'] = "higher weekend intake"
            else:
                analysis['pattern'] = "lower weekend intake"
        
        return analysis

    def _analyze_food_variety(self, food_diary: list) -> dict:
        """Analyze food variety and repetition."""
        all_foods = []
        
        for day in food_diary:
            meals = day.get('meals', [])
            for meal in meals:
                foods = meal.get('foods', [])
                for food in foods:
                    food_name = food.get('name', '').lower()
                    if food_name:
                        all_foods.append(food_name)
        
        if not all_foods:
            return {}
        
        unique_foods = set(all_foods)
        food_counts = {food: all_foods.count(food) for food in unique_foods}
        
        # Calculate variety metrics
        total_foods = len(all_foods)
        unique_count = len(unique_foods)
        variety_ratio = unique_count / total_foods if total_foods > 0 else 0
        
        # Find most repeated foods
        most_common = sorted(food_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_food_instances': total_foods,
            'unique_foods': unique_count,
            'variety_ratio': variety_ratio,
            'most_common_foods': most_common,
            'variety_assessment': "high" if variety_ratio > 0.7 else "moderate" if variety_ratio > 0.4 else "low"
        }

    def _format_daily_analysis(self, daily_nutrition: dict, analysis_results: dict, daily_meals: list) -> str:
        """Format daily nutrition analysis."""
        formatted = "# Daily Nutrition Analysis\n\n"
        
        # Summary
        formatted += "## Daily Intake Summary:\n"
        formatted += f"- **Calories**: {daily_nutrition.get('calories', 0):.0f}\n"
        formatted += f"- **Protein**: {daily_nutrition.get('protein', 0):.1f}g\n"
        formatted += f"- **Carbohydrates**: {daily_nutrition.get('carbs', 0):.1f}g\n"
        formatted += f"- **Fat**: {daily_nutrition.get('fat', 0):.1f}g\n"
        formatted += f"- **Fiber**: {daily_nutrition.get('fiber', 0):.1f}g\n"
        formatted += f"- **Sodium**: {daily_nutrition.get('sodium', 0):.0f}mg\n\n"
        
        # Analysis by nutrient
        formatted += "## Nutritional Analysis:\n"
        for nutrient, analysis in analysis_results.items():
            actual = analysis['actual']
            target = analysis['target']
            percentage = analysis['percentage']
            status = analysis['status']
            
            formatted += f"### {nutrient.replace('_', ' ').title()}\n"
            formatted += f"- Current: {actual:.1f}\n"
            formatted += f"- Target: {target:.1f}\n"
            formatted += f"- Achievement: {percentage:.1f}%\n"
            formatted += f"- Status: {status}\n\n"
        
        # Meal breakdown
        formatted += "## Meals Analyzed:\n"
        for i, meal in enumerate(daily_meals, 1):
            meal_type = meal.get('type', f'Meal {i}')
            foods = meal.get('foods', [])
            formatted += f"**{meal_type.title()}**: {len(foods)} items\n"
        
        return formatted

    def _format_compliance_report(self, compliance_results: dict, guidelines: str) -> str:
        """Format dietary compliance report."""
        formatted = f"# Dietary Compliance Report: {guidelines.title()}\n\n"
        
        overall_score = compliance_results.get('overall_score', 0)
        formatted += f"## Overall Compliance Score: {overall_score:.1f}/100\n\n"
        
        if overall_score >= 80:
            formatted += "✅ Excellent compliance with dietary guidelines!\n\n"
        elif overall_score >= 60:
            formatted += "⚠️ Good compliance with room for improvement\n\n"
        else:
            formatted += "❌ Poor compliance - significant changes needed\n\n"
        
        # Daily scores
        daily_scores = compliance_results.get('daily_scores', [])
        if daily_scores:
            formatted += "## Daily Compliance Scores:\n"
            for i, score in enumerate(daily_scores, 1):
                formatted += f"Day {i}: {score:.1f}/100\n"
            formatted += "\n"
        
        # Violations
        violations = compliance_results.get('violations', [])
        if violations:
            formatted += "## Areas for Improvement:\n"
            for violation in violations:
                formatted += f"- {violation}\n"
            formatted += "\n"
        
        # Recommendations
        recommendations = compliance_results.get('recommendations', [])
        if recommendations:
            formatted += "## Recommendations:\n"
            for rec in recommendations:
                formatted += f"- {rec}\n"
        
        return formatted

    def _compile_nutrition_report(self, period_analysis: dict, sections: list, analysis_period: dict) -> str:
        """Compile comprehensive nutrition report."""
        formatted = "# Comprehensive Nutrition Report\n\n"
        
        period_days = len(analysis_period.get('daily_logs', []))
        formatted += f"**Analysis Period**: {period_days} days\n\n"
        
        if 'overview' in sections:
            formatted += "## Overview\n"
            avg_daily = period_analysis.get('average_daily', {})
            formatted += f"- Average daily calories: {avg_daily.get('calories', 0):.0f}\n"
            formatted += f"- Average daily protein: {avg_daily.get('protein', 0):.1f}g\n"
            formatted += f"- Average daily carbs: {avg_daily.get('carbs', 0):.1f}g\n"
            formatted += f"- Average daily fat: {avg_daily.get('fat', 0):.1f}g\n\n"
        
        if 'key_metrics' in sections:
            formatted += "## Key Metrics\n"
            variability = period_analysis.get('variability', {})
            formatted += f"- Calorie consistency: {variability.get('calories', 0):.0f} (std dev)\n"
            formatted += f"- Protein consistency: {variability.get('protein', 0):.1f}g (std dev)\n\n"
        
        if 'recommendations' in sections:
            formatted += "## Recommendations\n"
            formatted += "- Continue tracking daily intake\n"
            formatted += "- Focus on consistent meal timing\n"
            formatted += "- Increase variety in food choices\n"
            formatted += "- Monitor portion sizes for better control\n"
        
        return formatted

    def _format_pattern_analysis(self, patterns: dict) -> str:
        """Format eating pattern analysis."""
        formatted = "# Eating Pattern Analysis\n\n"
        
        if 'meal_timing' in patterns:
            formatted += "## Meal Timing Patterns\n"
            timing = patterns['meal_timing']
            for meal_type, data in timing.items():
                avg_time = data.get('average_time', 'N/A')
                consistency = data.get('consistency', 'N/A')
                formatted += f"- **{meal_type.title()}**: {avg_time} (consistency: {consistency})\n"
            formatted += "\n"
        
        if 'calorie_trends' in patterns:
            formatted += "## Calorie Trends\n"
            trends = patterns['calorie_trends']
            formatted += f"- Average daily calories: {trends.get('average_calories', 0):.0f}\n"
            formatted += f"- Trend direction: {trends.get('trend', 'unknown')}\n"
            formatted += f"- Daily variability: {trends.get('variability', 0):.0f} calories\n\n"
        
        if 'food_variety' in patterns:
            formatted += "## Food Variety\n"
            variety = patterns['food_variety']
            assessment = variety.get('variety_assessment', 'unknown')
            unique_foods = variety.get('unique_foods', 0)
            formatted += f"- Variety assessment: {assessment}\n"
            formatted += f"- Unique foods consumed: {unique_foods}\n"
            
            most_common = variety.get('most_common_foods', [])
            if most_common:
                formatted += "- Most frequently consumed:\n"
                for food, count in most_common[:3]:
                    formatted += f"  - {food}: {count} times\n"
        
        return formatted