    def _generate_improvement_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on analysis."""
        recommendations = []

        quality_score = result.get("quality_score", 0.0)
        issues = result.get("issues_found", [])

        if quality_score < 0.6:
            recommendations.append("Overall quality needs significant improvement - consider professional editing")
        elif quality_score < 0.8:
            recommendations.append("Good foundation but needs refinement for academic standards")

        if any("length" in issue.lower() for issue in issues):
            recommendations.append("Adjust content length to meet academic requirements")

        if any("tone" in issue.lower() or "language" in issue.lower() for issue in issues):
            recommendations.append("Enhance formal academic tone and eliminate colloquial expressions")

        if any("structure" in issue.lower() for issue in issues):
            recommendations.append("Improve logical structure and paragraph organization")

        if not recommendations:

